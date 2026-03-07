"""Market service for retrieving cryptocurrency data from CoinGecko."""

import asyncio
from typing import TypedDict

import httpx


class CoinNotFoundError(Exception):
    """Raised when a requested coin id does not exist on CoinGecko."""


class CoinMarketData(TypedDict):
    """Typed payload returned by market service."""

    asset: str
    price: float
    price_usd: float
    change_24h: float
    market_cap: float
    prices: list[float]


class MarketService:
    """Service layer for market data retrieval."""

    _simple_price_url: str = "https://api.coingecko.com/api/v3/simple/price"
    _market_chart_url: str = "https://api.coingecko.com/api/v3/coins/{coin}/market_chart"

    async def get_coin_price(self, coin: str) -> CoinMarketData:
        """Fetch current market metrics for a coin from CoinGecko.

        Args:
            coin: CoinGecko coin id (e.g., ``bitcoin``).

        Returns:
            Standardized market data payload.

        Raises:
            CoinNotFoundError: If the coin id is invalid or missing in the response.
            httpx.HTTPError: If the upstream request fails.
        """
        normalized = coin.strip().lower()
        params = {
            "ids": normalized,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
        }
        chart_params = {"vs_currency": "usd", "days": 30, "interval": "daily"}

        await asyncio.sleep(1)
        async with httpx.AsyncClient(timeout=10.0) as client:
            price_response = await client.get(self._simple_price_url, params=params)
            price_response.raise_for_status()
            payload = price_response.json()
            chart_response = await client.get(
                self._market_chart_url.format(coin=normalized),
                params=chart_params,
            )
            chart_response.raise_for_status()
            chart_payload = chart_response.json()

        coin_payload = payload.get(normalized)
        if not coin_payload:
            raise CoinNotFoundError(f"Coin '{coin}' was not found.")

        price_usd = coin_payload.get("usd")
        change_24h = coin_payload.get("usd_24h_change")
        market_cap = coin_payload.get("usd_market_cap")

        if price_usd is None or change_24h is None or market_cap is None:
            raise CoinNotFoundError(
                f"Incomplete market data returned for coin '{coin}'."
            )

        historical_points = chart_payload.get("prices", [])
        if not historical_points:
            raise CoinNotFoundError(
                f"Historical market data was not found for coin '{coin}'."
            )

        historical_prices = [float(point[1]) for point in historical_points if len(point) >= 2]
        if len(historical_prices) < 30:
            raise CoinNotFoundError(
                f"Not enough historical price data returned for coin '{coin}'."
            )

        return {
            "asset": normalized,
            "price": float(price_usd),
            "price_usd": float(price_usd),
            "change_24h": float(change_24h),
            "market_cap": float(market_cap),
            "prices": historical_prices,
        }


market_service = MarketService()
