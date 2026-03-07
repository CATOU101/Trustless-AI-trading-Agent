"""Agent analysis API routes."""

import httpx
from fastapi import APIRouter, HTTPException, status

from app.models.decision import AnalyzeRequest, AnalyzeResponse, AgentProfileResponse
from app.services.agent_service import (
    OllamaUnavailableError,
    agent_service,
)
from app.services.indicator_service import compute_indicators
from app.services.market_service import CoinNotFoundError, market_service
from app.services.reputation_service import reputation_service
from app.services.trading_service import trading_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/profile", response_model=AgentProfileResponse)
async def get_agent_profile() -> AgentProfileResponse:
    """Return agent identity and current trading reputation."""
    return AgentProfileResponse(**reputation_service.get_agent_profile())


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_market(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Fetch market data and return an AI-generated trading decision."""
    try:
        market_data = await market_service.get_coin_price(payload.coin)
        indicators = compute_indicators(market_data["prices"])
        portfolio_state = trading_service.get_portfolio()
        ai_decision = await agent_service.analyze_market(
            asset=market_data["asset"],
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
            cash_balance=portfolio_state["cash_balance"],
            asset_holdings=portfolio_state["assets"].get(market_data["asset"], 0.0),
        )
        if ai_decision["decision"].value in {"BUY", "SELL"}:
            trading_service.execute_trade(
                asset=market_data["asset"],
                decision=ai_decision["decision"].value,
                price=market_data["price_usd"],
            )

        valuation = trading_service.calculate_portfolio_value(
            asset=market_data["asset"], price=market_data["price_usd"]
        )
        portfolio = {
            "cash_balance": valuation["cash_balance"],
            market_data["asset"]: valuation["asset_holdings"],
            "portfolio_value": valuation["portfolio_value"],
        }
        return AnalyzeResponse(**ai_decision, portfolio=portfolio, indicators=indicators)
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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
