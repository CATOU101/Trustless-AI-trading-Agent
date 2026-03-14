"""Coordinator for multi-agent trading decisions."""

from typing import TypedDict

from app.models.decision import TradingDecision
from app.services.agents.mean_reversion_agent import mean_reversion_agent
from app.services.agents.momentum_agent import momentum_agent
from app.services.agents.trend_agent import trend_agent


class AgentVote(TypedDict):
    """Vote emitted by an individual strategy agent."""

    agent: str
    action: TradingDecision
    confidence: float
    reason: str


class CoordinationResult(TypedDict):
    """Aggregated multi-agent decision result."""

    asset: str
    final_action: TradingDecision
    confidence: float
    agent_votes: list[AgentVote]


class AgentCoordinator:
    """Collect votes from multiple agents and aggregate the outcome."""

    _score_map = {
        TradingDecision.BUY: 1,
        TradingDecision.SELL: -1,
        TradingDecision.HOLD: 0,
    }

    def __init__(self) -> None:
        """Register the active strategy agents."""
        self._agents = [momentum_agent, mean_reversion_agent, trend_agent]

    async def get_agent_votes(
        self, asset: str, price: float, change_24h: float, rsi: float, ma20: float
    ) -> list[AgentVote]:
        """Collect votes from each strategy agent."""
        votes: list[AgentVote] = []
        for agent in self._agents:
            votes.append(
                await agent.evaluate(
                    asset=asset,
                    price=price,
                    change_24h=change_24h,
                    rsi=rsi,
                    ma20=ma20,
                )
            )
        return votes

    async def coordinate(
        self, asset: str, price: float, change_24h: float, rsi: float, ma20: float
    ) -> CoordinationResult:
        """Aggregate agent votes into a final action."""
        votes = await self.get_agent_votes(asset, price, change_24h, rsi, ma20)
        score = sum(self._score_map[vote["action"]] for vote in votes)
        if score > 0:
            final_action = TradingDecision.BUY
        elif score < 0:
            final_action = TradingDecision.SELL
        else:
            final_action = TradingDecision.HOLD

        print("Agent votes:", votes)
        print("Score:", score)
        print("Final action:", final_action)

        confidence = round(
            sum(vote["confidence"] for vote in votes) / len(votes),
            2,
        )
        return {
            "asset": asset,
            "final_action": final_action,
            "confidence": confidence,
            "agent_votes": votes,
        }

    def list_agents(self) -> list[str]:
        """Return registered agent names."""
        return [agent.name for agent in self._agents]


agent_coordinator = AgentCoordinator()
