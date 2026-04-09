"""Agent analysis API routes."""

from fastapi import APIRouter, Query

from app.models.decision import AnalyzeRequest, AnalyzeResponse, AgentProfileResponse
from app.models.decision import TradingDecision
from app.services.artifact_service import artifact_service
from app.services.agent_coordinator import agent_coordinator
from app.services.agent_service import (
    agent_service,
)
from app.services.indicator_service import compute_indicators
from app.services.market_service import market_service
from app.services.reputation_service import reputation_service
from app.services.risk_service import risk_service
from app.services.trading_service import enforce_position_rules, trading_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/agent", tags=["agent"])
logger = get_logger(__name__)

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


@router.get("/decision", response_model=AnalyzeResponse)
async def get_latest_decision(
    coin: str = Query(default="bitcoin", min_length=2, max_length=50)
) -> AnalyzeResponse:
    """Return the latest explainable decision for a coin without requiring POST."""
    return await _analyze_coin(coin)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_market(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Fetch market data and return an AI-generated trading decision."""
    return await _analyze_coin(payload.coin)


async def _analyze_coin(raw_coin: str) -> AnalyzeResponse:
    """Run the shared analyze-and-trade flow for a coin identifier."""
    coin_input = raw_coin.lower()
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

    print(f"Price: {market_data['price_usd']} | Change: {market_data['change_24h']}")
    try:
        indicators = compute_indicators(market_data["prices"])
    except ValueError:
        return _fallback_response(
            coin=coin,
            reason="Fallback decision due to temporary data error",
        )

    portfolio_state = trading_service.get_portfolio()
    coordination = await agent_coordinator.coordinate(
        asset=coin,
        price=market_data["price"],
        change_24h=market_data["change_24h"],
        rsi=indicators["rsi"],
        ma20=indicators["ma20"],
    )
    artifact_service.log_strategy_decision(
        asset=coin,
        action=coordination["final_action"].value,
        confidence=coordination["confidence"],
        metadata={"agent_votes": coordination["agent_votes"]},
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
    artifact_service.log_risk_check(
        asset=coin,
        action=coordination["final_action"].value,
        confidence=coordination["confidence"],
        metadata=risk,
    )
    final_action = coordination["final_action"]
    if not risk["allowed"]:
        final_action = TradingDecision.HOLD
    execution_portfolio = {
        "cash_balance": float(portfolio_state["cash_balance"]),
        coin: float(portfolio_state["assets"].get(coin, 0.0)),
    }
    original_action = final_action.value
    adjusted_action, override_reason = enforce_position_rules(
        final_action.value,
        coin,
        execution_portfolio,
    )
    final_action = TradingDecision(adjusted_action)
    print("Original action:", original_action)
    print("Adjusted action:", final_action.value)
    print("Override reason:", override_reason)
    logger.info(
        "Decision computed: asset=%s coordination=%s final=%s",
        coin,
        coordination["final_action"].value,
        final_action.value,
    )
    print(f"Decision computed: {final_action.value}")

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
    if override_reason:
        ai_decision["decision"] = TradingDecision.HOLD
        ai_decision["reasoning"] = override_reason

    if risk["allowed"] and ai_decision["decision"].value in {"BUY", "SELL"}:
        try:
            trading_service.execute_trade(
                asset=coin,
                decision=ai_decision["decision"].value,
                price=market_data["price_usd"],
                confidence=ai_decision["confidence"],
                position_size=float(risk["adjusted_position_size"]),
                agent="AgentAPI",
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
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Trade execution failed but decision preserved | asset=%s action=%s error=%s",
                coin,
                ai_decision["decision"].value,
                exc,
            )

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
        final_action=final_action,
        agent_votes=coordination["agent_votes"],
        leaderboard=reputation_service.get_agent_leaderboard(),
        risk=risk,
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
