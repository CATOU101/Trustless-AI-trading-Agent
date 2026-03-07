"""Market data API routes."""

import httpx
from fastapi import APIRouter, HTTPException, status

from app.models.decision import MarketPriceResponse
from app.services.market_service import CoinNotFoundError, market_service

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/price/{coin}", response_model=MarketPriceResponse)
async def get_market_price(coin: str) -> MarketPriceResponse:
    """Fetch live market data for a coin from CoinGecko."""
    try:
        market_data = await market_service.get_coin_price(coin)
        return MarketPriceResponse(**market_data)
    except CoinNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="CoinGecko returned an error response.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to fetch market data from CoinGecko.",
        ) from exc
