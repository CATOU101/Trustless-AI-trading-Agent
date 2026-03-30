"""Kraken integration service with CLI-first and REST fallback support."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class KrakenCLIError(Exception):
    """Raised when the Kraken CLI fails or returns malformed output."""


class KrakenRESTError(Exception):
    """Raised when the Kraken REST API fails or returns malformed output."""


class KrakenService:
    """Wrapper around Kraken CLI and public REST endpoints."""

    _pair_map = {
        "bitcoin": ("BTC/USD", "XBTUSD"),
        "ethereum": ("ETH/USD", "ETHUSD"),
        "solana": ("SOL/USD", "SOLUSD"),
        "dogecoin": ("DOGE/USD", "DOGEUSD"),
        "cardano": ("ADA/USD", "ADAUSD"),
    }
    _rest_ticker_url = "https://api.kraken.com/0/public/Ticker"
    _rest_ohlc_url = "https://api.kraken.com/0/public/OHLC"
    _extra_path_entries = (
        "/Users/madhavan/Library/Python/3.13/bin",
        "/Users/madhavan/Library/Python/3.11/bin",
    )

    def _build_env(self) -> dict[str, str]:
        """Return an environment with common user-bin locations on PATH."""
        env = os.environ.copy()
        current_path = env.get("PATH", "")
        env["PATH"] = ":".join((*self._extra_path_entries, current_path))
        return env

    def _resolve_pair(self, asset: str) -> tuple[str, str]:
        """Map a CoinGecko-style asset id to CLI and REST Kraken pairs."""
        normalized = asset.strip().lower()
        if normalized in self._pair_map:
            return self._pair_map[normalized]
        symbol = normalized.upper()
        return f"{symbol}/USD", f"{symbol}USD"

    def kraken_cli_available(self) -> bool:
        """Return True when the Kraken CLI is installed and runnable."""
        candidate = shutil.which("kraken", path=self._build_env()["PATH"])
        if not candidate:
            return False
        try:
            result = subprocess.run(
                ["kraken", "--help"],
                capture_output=True,
                text=True,
                env=self._build_env(),
                check=False,
            )
        except Exception:
            return False
        return result.returncode == 0

    def run_kraken_command(self, cmd: str) -> dict[str, Any]:
        """Execute a Kraken CLI command and parse the JSON response."""
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
            env=self._build_env(),
        )
        if result.returncode != 0:
            raise KrakenCLIError(result.stderr.strip() or result.stdout.strip() or cmd)
        stdout = result.stdout.strip()
        if not stdout:
            raise KrakenCLIError("Kraken CLI returned empty output.")
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise KrakenCLIError("Kraken CLI returned invalid JSON.") from exc

    def _unwrap_result(self, payload: dict[str, Any], pair: str) -> Any:
        """Return the most relevant Kraken payload section for a pair."""
        result = payload.get("result", payload)
        if isinstance(result, dict):
            if pair in result:
                return result[pair]
            for value in result.values():
                return value
        return result

    def _coerce_float(self, value: Any) -> float | None:
        """Convert a field into a float when possible."""
        if isinstance(value, list) and value:
            value = value[0]
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def get_kraken_price(self, asset: str) -> dict[str, Any]:
        """Fetch price from Kraken CLI when available, else public REST."""
        if self.kraken_cli_available():
            logger.info("Kraken CLI detected")
            print("Kraken CLI detected")
            return await self._get_cli_price(asset)
        logger.info("Using Kraken REST fallback")
        print("Using Kraken REST fallback")
        return await self._get_rest_price(asset)

    async def get_kraken_history(self, asset: str) -> list[float]:
        """Fetch history from Kraken CLI when available, else public REST."""
        if self.kraken_cli_available():
            return await self._get_cli_history(asset)
        logger.info("Using Kraken REST fallback")
        print("Using Kraken REST fallback")
        return await self._get_rest_history(asset)

    async def _get_cli_price(self, asset: str) -> dict[str, Any]:
        """Fetch the latest market price from Kraken CLI."""
        pair, _ = self._resolve_pair(asset)
        payload = await asyncio.to_thread(
            self.run_kraken_command, f"kraken ticker {pair} -o json"
        )
        ticker = self._unwrap_result(payload, pair)
        if not isinstance(ticker, dict):
            raise KrakenCLIError(f"Unexpected ticker payload for {pair}.")

        price = None
        for key in ("last", "close", "price", "c"):
            price = self._coerce_float(ticker.get(key))
            if price is not None:
                break
        if price is None:
            raise KrakenCLIError(f"Unable to parse Kraken price for {pair}.")

        change_24h = None
        for key in ("change_24h", "change", "p"):
            change_24h = self._coerce_float(ticker.get(key))
            if change_24h is not None:
                break

        logger.info("Kraken price fetched | asset=%s pair=%s", asset, pair)
        print("Kraken price fetched")
        return {
            "asset": asset.strip().lower(),
            "pair": pair,
            "price_usd": price,
            "change_24h": change_24h,
            "market_cap": None,
        }

    async def _get_cli_history(self, asset: str) -> list[float]:
        """Fetch daily historical close prices from Kraken CLI."""
        pair, _ = self._resolve_pair(asset)
        payload = await asyncio.to_thread(
            self.run_kraken_command, f"kraken ohlc {pair} --interval 1440 -o json"
        )
        rows = self._unwrap_result(payload, pair)
        if not isinstance(rows, list):
            raise KrakenCLIError(f"Unexpected OHLC payload for {pair}.")

        prices: list[float] = []
        for row in rows:
            close_value: float | None = None
            if isinstance(row, list) and len(row) >= 5:
                close_value = self._coerce_float(row[4])
            elif isinstance(row, dict):
                close_value = self._coerce_float(
                    row.get("close") or row.get("c") or row.get("price")
                )
            if close_value is not None:
                prices.append(close_value)

        if len(prices) < 30:
            raise KrakenCLIError(f"Not enough Kraken history returned for {pair}.")
        return prices[-30:]

    async def _get_rest_price(self, asset: str) -> dict[str, Any]:
        """Fetch the latest market price from Kraken public REST."""
        _, rest_pair = self._resolve_pair(asset)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self._rest_ticker_url, params={"pair": rest_pair})
            response.raise_for_status()
            payload = response.json()
        if payload.get("error"):
            raise KrakenRESTError(str(payload["error"]))
        ticker = self._unwrap_result(payload, rest_pair)
        if not isinstance(ticker, dict):
            raise KrakenRESTError(f"Unexpected REST ticker payload for {rest_pair}.")

        price = None
        for key in ("c", "p", "last", "close"):
            price = self._coerce_float(ticker.get(key))
            if price is not None:
                break
        if price is None:
            raise KrakenRESTError(f"Unable to parse Kraken REST price for {rest_pair}.")

        logger.info("Kraken price fetched | asset=%s pair=%s", asset, rest_pair)
        print("Kraken price fetched")
        return {
            "asset": asset.strip().lower(),
            "pair": rest_pair,
            "price_usd": price,
            "change_24h": None,
            "market_cap": None,
        }

    async def _get_rest_history(self, asset: str) -> list[float]:
        """Fetch daily history from Kraken public REST."""
        _, rest_pair = self._resolve_pair(asset)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self._rest_ohlc_url,
                params={"pair": rest_pair, "interval": 1440},
            )
            response.raise_for_status()
            payload = response.json()
        if payload.get("error"):
            raise KrakenRESTError(str(payload["error"]))
        rows = self._unwrap_result(payload, rest_pair)
        if not isinstance(rows, list):
            raise KrakenRESTError(f"Unexpected REST OHLC payload for {rest_pair}.")

        prices: list[float] = []
        for row in rows:
            if isinstance(row, list) and len(row) >= 5:
                close_value = self._coerce_float(row[4])
                if close_value is not None:
                    prices.append(close_value)
        if len(prices) < 30:
            raise KrakenRESTError(f"Not enough Kraken REST history for {rest_pair}.")
        return prices[-30:]

    def extract_execution_price(self, payload: dict[str, Any]) -> float | None:
        """Best-effort extraction of an execution price from Kraken trade output."""
        result = payload.get("result", payload)
        if isinstance(result, dict):
            for key in ("price", "avg_price", "executed_price"):
                parsed = self._coerce_float(result.get(key))
                if parsed is not None:
                    return parsed
            descr = result.get("descr")
            if isinstance(descr, dict):
                parsed = self._coerce_float(descr.get("price"))
                if parsed is not None:
                    return parsed
        return None

    def execute_kraken_trade(
        self,
        asset: str,
        action: str,
        amount: float,
    ) -> dict[str, Any]:
        """Submit a Kraken CLI paper trade when available."""
        if not self.kraken_cli_available():
            raise KrakenCLIError("Kraken CLI unavailable for paper trading.")
        pair, _ = self._resolve_pair(asset)
        side = action.strip().lower()
        if side not in {"buy", "sell"}:
            raise KrakenCLIError(f"Unsupported Kraken trade side '{action}'.")
        payload = self.run_kraken_command(f"kraken paper {side} {pair} {amount} -o json")
        logger.info(
            "Kraken trade executed | asset=%s action=%s pair=%s amount=%s",
            asset,
            side.upper(),
            pair,
            amount,
        )
        print("Kraken trade executed")
        return payload


def kraken_available() -> bool:
    """Return True when Kraken CLI is installed and runnable."""
    return kraken_service.kraken_cli_available()


def kraken_cli_available() -> bool:
    """Return True when Kraken CLI is installed and runnable."""
    return kraken_service.kraken_cli_available()


import asyncio

kraken_service = KrakenService()
