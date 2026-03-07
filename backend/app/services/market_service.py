"""Market service for retrieving cryptocurrency data from CoinGecko."""

from typing import TypedDict

import httpx


class CoinNotFoundError(Exception):
    """Raised when a requested coin id does not exist on CoinGecko."""


class CoinMarketData(TypedDict):
    """Typed payload returned by market service."""

    asset: str
    price_usd: float
    change_24h: float
    market_cap: float


class MarketService:
    """Service layer for market data retrieval."""

    _base_url: str = "https://api.coingecko.com/api/v3/simple/price"

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

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self._base_url, params=params)
            response.raise_for_status()
            payload = response.json()

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

        return {
            "asset": normalized,
            "price_usd": float(price_usd),
            "change_24h": float(change_24h),
            "market_cap": float(market_cap),
        }


market_service = MarketService()
