"""Agent analysis API routes."""

import httpx
from fastapi import APIRouter

from app.models.decision import AnalyzeRequest, AnalyzeResponse, AgentProfileResponse
from app.models.decision import TradingDecision
from app.services.agent_coordinator import agent_coordinator
from app.services.agent_service import (
    agent_service,
)
from app.services.indicator_service import compute_indicators
from app.services.market_service import market_service
from app.services.reputation_service import reputation_service
from app.services.risk_service import risk_service
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
        market_data = await market_service.get_market_data(coin)
    except Exception:
        return _fallback_response(coin=coin, reason="Market data unavailable")

    try:
        print(
            f"Price: {market_data['price_usd']} | Change: {market_data['change_24h']}"
        )
        indicators = compute_indicators(market_data["prices"])
        portfolio_state = trading_service.get_portfolio()
        coordination = await agent_coordinator.coordinate(
            asset=coin,
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
        )
        current_value = trading_service.calculate_portfolio_value(
            asset=coin, price=market_data["price_usd"]
        )["portfolio_value"]
        risk = risk_service.evaluate(
            current_portfolio_value=current_value,
            peak_portfolio_value=trading_service.get_peak_portfolio_value(),
            volatility=abs(market_data["change_24h"]),
            last_trade_timestamp=trading_service.get_last_trade_timestamp(),
        )
        final_action = coordination["final_action"]
        if not risk["allowed"]:
            final_action = TradingDecision.HOLD

        ai_decision = await agent_service.analyze_market(
            asset=coin,
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
            cash_balance=portfolio_state["cash_balance"],
            asset_holdings=portfolio_state["assets"].get(coin, 0.0),
            decision=final_action,
        )
        if risk["allowed"] and ai_decision["decision"].value in {"BUY", "SELL"}:
            trading_service.execute_trade(
                asset=coin,
                decision=ai_decision["decision"].value,
                price=market_data["price_usd"],
                confidence=ai_decision["confidence"],
                position_size=float(risk["adjusted_position_size"]),
            )
            ma20 = indicators["ma20"] or market_data["price_usd"]
            if coordination["final_action"] == TradingDecision.BUY:
                trade_return = round((ma20 - market_data["price_usd"]) / ma20, 6)
            elif coordination["final_action"] == TradingDecision.SELL:
                trade_return = round((market_data["price_usd"] - ma20) / ma20, 6)
            else:
                trade_return = 0.0
            for vote in coordination["agent_votes"]:
                if vote["action"] == coordination["final_action"]:
                    reputation_service.record_agent_trade(vote["agent"], trade_return)

        valuation = trading_service.calculate_portfolio_value(
            asset=coin, price=market_data["price_usd"]
        )
        portfolio = {
            "cash_balance": valuation["cash_balance"],
            coin: valuation["asset_holdings"],
            "portfolio_value": valuation["portfolio_value"],
        }
        return AnalyzeResponse(
            **ai_decision,
            portfolio=portfolio,
            indicators=indicators,
            final_action=coordination["final_action"],
            agent_votes=coordination["agent_votes"],
            leaderboard=reputation_service.get_agent_leaderboard(),
            risk=risk,
        )
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
        final_action=TradingDecision.HOLD,
        agent_votes=[],
        leaderboard=reputation_service.get_agent_leaderboard(),
        risk={
            "allowed": False,
            "adjusted_position_size": 0.0,
            "reason": "Fallback response triggered.",
        },
    )
