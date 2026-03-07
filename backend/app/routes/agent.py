"""Agent analysis API routes."""

import httpx
from fastapi import APIRouter

from app.models.decision import AnalyzeRequest, AnalyzeResponse, AgentProfileResponse
from app.services.agent_service import (
    agent_service,
)
from app.services.indicator_service import compute_indicators
from app.services.market_service import market_service
from app.services.reputation_service import reputation_service
from app.services.trading_service import trading_service

router = APIRouter(prefix="/agent", tags=["agent"])

COIN_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
}


@router.get("/profile", response_model=AgentProfileResponse)
async def get_agent_profile() -> AgentProfileResponse:
    """Return agent identity and current trading reputation."""
    return AgentProfileResponse(**reputation_service.get_agent_profile())


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_market(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Fetch market data and return an AI-generated trading decision."""
    coin_input = payload.coin.lower()
    coin = COIN_MAP.get(coin_input, coin_input).strip()
    if not coin:
        return _fallback_response(
            coin="unknown",
            reason="Fallback decision due to temporary data error",
        )

    print(f"Analyzing coin: {coin}")
    try:
        market_data = await market_service.get_coin_price(coin)
    except Exception:
        return _fallback_response(coin=coin, reason="Market data unavailable")

    try:
        print(
            f"Price: {market_data['price_usd']} | Change: {market_data['change_24h']}"
        )
        indicators = compute_indicators(market_data["prices"])
        portfolio_state = trading_service.get_portfolio()
        ai_decision = await agent_service.analyze_market(
            asset=coin,
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
            cash_balance=portfolio_state["cash_balance"],
            asset_holdings=portfolio_state["assets"].get(coin, 0.0),
        )
        if ai_decision["decision"].value in {"BUY", "SELL"}:
            trading_service.execute_trade(
                asset=coin,
                decision=ai_decision["decision"].value,
                price=market_data["price_usd"],
                confidence=ai_decision["confidence"],
            )

        valuation = trading_service.calculate_portfolio_value(
            asset=coin, price=market_data["price_usd"]
        )
        portfolio = {
            "cash_balance": valuation["cash_balance"],
            coin: valuation["asset_holdings"],
            "portfolio_value": valuation["portfolio_value"],
        }
        return AnalyzeResponse(**ai_decision, portfolio=portfolio, indicators=indicators)
    except (httpx.HTTPError, ValueError, Exception):
        return _fallback_response(
            coin=coin,
            reason="Fallback decision due to temporary data error",
        )


def _fallback_response(coin: str, reason: str) -> AnalyzeResponse:
    """Return a safe fallback decision payload for temporary failures."""
    portfolio_state = trading_service.get_portfolio()
    cash_balance = float(portfolio_state["cash_balance"])
    asset_holdings = float(portfolio_state["assets"].get(coin, 0.0))
    return AnalyzeResponse(
        asset=coin,
        decision="HOLD",
        confidence=0.5,
        reasoning=reason,
        portfolio={
            "cash_balance": cash_balance,
            coin: asset_holdings,
            "portfolio_value": cash_balance,
        },
        indicators={"rsi": 50.0, "ma20": 0.0},
    )
