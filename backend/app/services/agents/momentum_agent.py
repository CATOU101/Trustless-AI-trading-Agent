"""Momentum-based trading agent."""

from typing import TypedDict

from app.models.decision import TradingDecision


class AgentSignal(TypedDict):
    """Structured output from a strategy agent."""

    agent: str
    action: TradingDecision
    confidence: float
    reason: str


class MomentumAgent:
    """Agent that follows short-term directional strength."""

    name = "MomentumAgent"

    async def evaluate(
        self, asset: str, price: float, change_24h: float, rsi: float, ma20: float
    ) -> AgentSignal:
        """Return a momentum-oriented action."""
        if rsi < 45:
            action = TradingDecision.BUY
            confidence = 0.72
            reason = f"{asset} has improving momentum with RSI below 45, supporting a long setup."
        elif rsi > 65:
            action = TradingDecision.SELL
            confidence = 0.74
            reason = f"{asset} momentum is overheated with RSI above 65, favoring profit-taking."
        else:
            action = TradingDecision.HOLD
            confidence = 0.58
            reason = f"{asset} momentum setup is mixed, so there is no clean momentum trade."

        return {
            "agent": self.name,
            "action": action,
            "confidence": round(confidence, 2),
            "reason": reason,
        }


momentum_agent = MomentumAgent()
