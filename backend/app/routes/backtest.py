"""Backtesting API routes."""

import httpx
from fastapi import APIRouter, HTTPException, status

from app.services.backtest_service import backtest_service

router = APIRouter(prefix="/backtest", tags=["backtest"])

COIN_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
}


@router.get("/{coin}")
async def run_backtest(coin: str) -> dict[str, object]:
    """Run historical backtest for a coin over the last 60 days."""
    normalized = COIN_MAP.get(coin.strip().lower(), coin.strip().lower())
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coin",
        )

    try:
        return await backtest_service.run_backtest(normalized)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="CoinGecko returned an error response for backtest data.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to fetch historical market data for backtest.",
        ) from exc
