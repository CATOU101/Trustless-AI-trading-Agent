"""Agent analysis API routes."""

import httpx
from fastapi import APIRouter, HTTPException, status

from app.models.decision import AnalyzeRequest, AnalyzeResponse
from app.services.agent_service import (
    InvalidModelResponseError,
    OllamaUnavailableError,
    agent_service,
)
from app.services.market_service import CoinNotFoundError, market_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_market(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Fetch market data and return an AI-generated trading decision."""
    try:
        market_data = await market_service.get_coin_price(payload.coin)
        ai_decision = await agent_service.analyze_market(
            asset=market_data["asset"],
            price=market_data["price_usd"],
            change_24h=market_data["change_24h"],
        )
        return AnalyzeResponse(**ai_decision)
    except CoinNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except OllamaUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except InvalidModelResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama returned an error response.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to reach required upstream services.",
        ) from exc
