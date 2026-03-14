"""Mean-reversion trading agent."""

from typing import TypedDict

from app.models.decision import TradingDecision


class AgentSignal(TypedDict):
    """Structured output from a strategy agent."""

    agent: str
    action: TradingDecision
    confidence: float
    reason: str


class MeanReversionAgent:
    """Agent that fades overextension relative to RSI and moving average."""

    name = "MeanReversionAgent"

    async def evaluate(
        self, asset: str, price: float, change_24h: float, rsi: float, ma20: float
    ) -> AgentSignal:
        """Return a mean-reversion action."""
        if rsi < 30:
            action = TradingDecision.BUY
            confidence = 0.76
            reason = f"{asset} is oversold with RSI below 30, which supports a rebound setup."
        elif rsi > 70:
            action = TradingDecision.SELL
            confidence = 0.76
            reason = f"{asset} is overbought with RSI above 70, which supports mean reversion lower."
        else:
            action = TradingDecision.HOLD
            confidence = 0.57
            reason = f"{asset} is near its balance zone, so the reversion edge is weak."

        return {
            "agent": self.name,
            "action": action,
            "confidence": round(confidence, 2),
            "reason": reason,
        }


mean_reversion_agent = MeanReversionAgent()
