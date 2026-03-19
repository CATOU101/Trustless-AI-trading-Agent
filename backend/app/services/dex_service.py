"""DEX quote and simulated swap service."""

from typing import Any, TypedDict

import httpx

from app.services.intent_service import TradeIntent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DexQuote(TypedDict):
    """Quote returned by the DEX layer."""

    source: str
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    estimated_price: float
    raw: dict[str, Any]


class SimulatedSwap(TypedDict):
    """Simulated trade execution result from a quote."""

    action: str
    token_in: str
    token_out: str
    sell_amount: float
    buy_amount: float
    estimated_price: float
    quote: DexQuote


class DexService:
    """Fetch quotes from 0x and provide a deterministic fallback simulation."""

    _zero_x_price_url = "https://api.0x.org/swap/v1/price"
    _token_prices_usd = {
        "USDC": 1.0,
        "WBTC": 70000.0,
        "WETH": 3500.0,
        "SOL": 150.0,
    }
    _asset_to_token = {
        "BTC": "WBTC",
        "BITCOIN": "WBTC",
        "ETH": "WETH",
        "ETHEREUM": "WETH",
        "SOL": "SOL",
        "SOLANA": "SOL",
    }
    _token_decimals = {
        "USDC": 6,
        "WBTC": 8,
        "WETH": 18,
        "SOL": 9,
    }
    _token_addresses = {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "WETH": "0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2",
        "SOL": "0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
    }

    def _normalize_token(self, token: str) -> str:
        """Normalize a symbol or asset name to an on-chain token symbol."""
        normalized = token.strip().upper()
        return self._asset_to_token.get(normalized, normalized)

    def _build_simulated_quote(
        self, token_in: str, token_out: str, amount: float, raw: dict[str, Any] | None = None
    ) -> DexQuote:
        """Build fallback deterministic quote when remote DEX endpoint is unavailable."""
        price_in = self._token_prices_usd.get(token_in, 1.0)
        price_out = self._token_prices_usd.get(token_out, 1.0)
        gross_out = amount * price_in / price_out
        amount_out = max(gross_out * 0.997, 0.0)  # 0.3% effective fee/slippage
        estimated_price = amount_out / amount if amount > 0 else 0.0
        return {
            "source": "simulated",
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": round(amount, 10),
            "amount_out": round(amount_out, 10),
            "estimated_price": round(estimated_price, 10),
            "raw": raw or {},
        }

    def get_swap_quote(self, token_in: str, token_out: str, amount: float) -> DexQuote:
        """Fetch a swap quote from 0x, falling back to deterministic simulation."""
        if amount <= 0:
            raise ValueError("Swap amount must be greater than zero.")

        normalized_in = self._normalize_token(token_in)
        normalized_out = self._normalize_token(token_out)
        in_decimals = self._token_decimals.get(normalized_in, 18)
        out_decimals = self._token_decimals.get(normalized_out, 18)
        sell_amount = int(amount * (10**in_decimals))
        sell_token = self._token_addresses.get(normalized_in, normalized_in)
        buy_token = self._token_addresses.get(normalized_out, normalized_out)

        try:
            response = httpx.get(
                self._zero_x_price_url,
                params={
                    "sellToken": sell_token,
                    "buyToken": buy_token,
                    "sellAmount": str(sell_amount),
                },
                timeout=8.0,
            )
            response.raise_for_status()
            payload = response.json()
            buy_amount_wei = float(payload.get("buyAmount", 0))
            sell_amount_wei = float(payload.get("sellAmount", sell_amount))
            amount_in = sell_amount_wei / (10**in_decimals)
            amount_out = buy_amount_wei / (10**out_decimals)
            estimated_price = amount_out / amount_in if amount_in > 0 else 0.0
            quote: DexQuote = {
                "source": "0x",
                "token_in": normalized_in,
                "token_out": normalized_out,
                "amount_in": round(amount_in, 10),
                "amount_out": round(amount_out, 10),
                "estimated_price": round(estimated_price, 10),
                "raw": payload,
            }
            logger.info(
                "DEX quote fetched | source=%s in=%s out=%s amount_in=%s amount_out=%s",
                quote["source"],
                quote["token_in"],
                quote["token_out"],
                quote["amount_in"],
                quote["amount_out"],
            )
            return quote
        except Exception as exc:  # noqa: BLE001
            quote = self._build_simulated_quote(
                token_in=normalized_in,
                token_out=normalized_out,
                amount=amount,
                raw={"error": str(exc)},
            )
            logger.info(
                "DEX quote fetched | source=%s in=%s out=%s amount_in=%s amount_out=%s",
                quote["source"],
                quote["token_in"],
                quote["token_out"],
                quote["amount_in"],
                quote["amount_out"],
            )
            return quote

    def simulate_swap(self, intent: TradeIntent) -> SimulatedSwap:
        """Simulate a DEX swap for a signed intent without submitting on-chain tx."""
        action = intent["action"].strip().upper()
        asset_token = self._normalize_token(intent["asset"])

        if action == "BUY":
            token_in = "USDC"
            token_out = asset_token
            amount = float(intent["amount"])
        elif action == "SELL":
            token_in = asset_token
            token_out = "USDC"
            amount = float(intent["amount"])
        else:
            raise ValueError("Intent action must be BUY or SELL.")

        quote = self.get_swap_quote(token_in=token_in, token_out=token_out, amount=amount)
        return {
            "action": action,
            "token_in": quote["token_in"],
            "token_out": quote["token_out"],
            "sell_amount": quote["amount_in"],
            "buy_amount": quote["amount_out"],
            "estimated_price": quote["estimated_price"],
            "quote": quote,
        }


dex_service = DexService()
