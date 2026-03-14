"""Trend-following trading agent."""

from typing import TypedDict

from app.models.decision import TradingDecision


class AgentSignal(TypedDict):
    """Structured output from a strategy agent."""

    agent: str
    action: TradingDecision
    confidence: float
    reason: str


class TrendAgent:
    """Agent that follows higher-level trend state."""

    name = "TrendAgent"

    async def evaluate(
        self, asset: str, price: float, change_24h: float, rsi: float, ma20: float
    ) -> AgentSignal:
        """Return a trend-based action."""
        if price > ma20:
            action = TradingDecision.BUY
            confidence = 0.68
            reason = f"{asset} is trading above MA20, so the trend remains constructive."
        elif price < ma20:
            action = TradingDecision.SELL
            confidence = 0.68
            reason = f"{asset} is trading below MA20, so the trend remains weak."
        else:
            action = TradingDecision.HOLD
            confidence = 0.56
            reason = f"{asset} trend signal is flat, so a directional trade is not justified."

        return {
            "agent": self.name,
            "action": action,
            "confidence": round(confidence, 2),
            "reason": reason,
        }


trend_agent = TrendAgent()
