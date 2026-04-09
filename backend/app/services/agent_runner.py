"""Autonomous background runner for periodic market scanning and trading."""

import asyncio
from typing import TypedDict

from app.models.decision import TradingDecision
from app.services.artifact_service import artifact_service
from app.services.agent_coordinator import agent_coordinator
from app.services.agent_service import agent_service
from app.services.indicator_service import compute_indicators
from app.services.market_service import market_service
from app.services.reputation_service import reputation_service
from app.services.risk_service import risk_service
from app.services.trading_service import enforce_position_rules, trading_service

ASSETS = [
    "ethereum",
]


class RunnerResult(TypedDict):
    """Result from a single autonomous analyze-and-trade cycle."""

    asset: str
    final_action: TradingDecision
    confidence: float
    reasoning: str


class AgentRunner:
    """Continuously scans supported assets and executes paper trades."""

    def __init__(self) -> None:
        """Initialize runner state."""
        self._lock = asyncio.Lock()

    async def analyze_and_trade(self, asset: str) -> RunnerResult:
        """Run the existing analyze-and-trade pipeline for one asset."""
        normalized_asset = asset.strip().lower()
        print("Analyzing:", normalized_asset)

        market_data = await market_service.get_market_data(normalized_asset)
        indicators = compute_indicators(market_data["prices"])
        portfolio_state = trading_service.get_portfolio()
        coordination = await agent_coordinator.coordinate(
            asset=normalized_asset,
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
        )
        artifact_service.log_strategy_decision(
            asset=normalized_asset,
            action=coordination["final_action"].value,
            confidence=coordination["confidence"],
            metadata={"agent_votes": coordination["agent_votes"]},
        )
        current_value = trading_service.calculate_portfolio_value(
            asset=normalized_asset,
            price=market_data["price_usd"],
        )["portfolio_value"]
        risk = risk_service.evaluate(
            current_portfolio_value=current_value,
            peak_portfolio_value=trading_service.get_peak_portfolio_value(),
            volatility=abs(market_data["change_24h"]),
            last_trade_timestamp=trading_service.get_last_trade_timestamp(),
        )
        artifact_service.log_risk_check(
            asset=normalized_asset,
            action=coordination["final_action"].value,
            confidence=coordination["confidence"],
            metadata=risk,
        )

        final_action = coordination["final_action"]
        if not risk["allowed"]:
            final_action = TradingDecision.HOLD
        execution_portfolio = {
            "cash_balance": float(portfolio_state["cash_balance"]),
            normalized_asset: float(portfolio_state["assets"].get(normalized_asset, 0.0)),
        }
        original_action = final_action.value
        adjusted_action, override_reason = enforce_position_rules(
            final_action.value,
            normalized_asset,
            execution_portfolio,
        )
        final_action = TradingDecision(adjusted_action)
        print("Original action:", original_action)
        print("Adjusted action:", final_action.value)
        print("Override reason:", override_reason)

        decision_payload = await agent_service.analyze_market(
            asset=normalized_asset,
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
            cash_balance=portfolio_state["cash_balance"],
            asset_holdings=portfolio_state["assets"].get(normalized_asset, 0.0),
            decision=final_action,
        )
        if override_reason:
            decision_payload["decision"] = TradingDecision.HOLD
            decision_payload["reasoning"] = override_reason

        if risk["allowed"] and final_action in {TradingDecision.BUY, TradingDecision.SELL}:
            print("Executing trade...")
            trading_service.execute_trade(
                asset=normalized_asset,
                decision=final_action.value,
                price=market_data["price_usd"],
                confidence=coordination["confidence"],
                position_size=float(risk["adjusted_position_size"]),
                agent="AutonomousRunner",
            )
            ma20 = indicators["ma20"] or market_data["price_usd"]
            if final_action == TradingDecision.BUY:
                trade_return = round((ma20 - market_data["price_usd"]) / ma20, 6)
            else:
                trade_return = round((market_data["price_usd"] - ma20) / ma20, 6)

            for vote in coordination["agent_votes"]:
                if vote["action"] == final_action:
                    reputation_service.record_agent_trade(vote["agent"], trade_return)

        return {
            "asset": normalized_asset,
            "final_action": final_action,
            "confidence": coordination["confidence"],
            "reasoning": decision_payload["reasoning"],
        }

    async def run_agent_loop(self) -> None:
        """Continuously scan configured assets on a fixed schedule."""
        try:
            while True:
                async with self._lock:
                    for asset in ASSETS:
                        try:
                            await self.analyze_and_trade(asset)
                        except asyncio.CancelledError:
                            print("Agent runner stopped")
                            raise
                        except Exception as exc:
                            print(f"Autonomous runner error for {asset}: {exc}")
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            print("Agent loop shutting down...")
            print("Agent runner stopped")
            raise


agent_runner = AgentRunner()
