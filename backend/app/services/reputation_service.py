"""In-memory agent identity and reputation tracking service."""

from datetime import UTC, datetime
from typing import TypedDict


class AgentProfile(TypedDict):
    """Profile and performance summary for the trading agent."""

    agent_id: str
    strategy: str
    created_at: str
    total_trades: int
    wins: int
    losses: int
    reputation_score: float


class ReputationService:
    """Service for managing agent identity and performance reputation."""

    def __init__(self) -> None:
        """Initialize default agent profile."""
        self._profile: AgentProfile = {
            "agent_id": "explainable_trader",
            "strategy": "Explainable AI trading strategy",
            "created_at": datetime.now(UTC).isoformat(),
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "reputation_score": 0.0,
        }

    def get_agent_profile(self) -> AgentProfile:
        """Return a copy of the current agent profile."""
        return dict(self._profile)

    def record_trade(self, result: str) -> AgentProfile:
        """Record trade outcome and refresh reputation score.

        Args:
            result: One of ``WIN``, ``LOSS``, or ``NEUTRAL``.
        """
        normalized_result = result.strip().upper()
        if normalized_result not in {"WIN", "LOSS", "NEUTRAL"}:
            raise ValueError("Trade result must be WIN, LOSS, or NEUTRAL.")

        self._profile["total_trades"] += 1
        if normalized_result == "WIN":
            self._profile["wins"] += 1
        elif normalized_result == "LOSS":
            self._profile["losses"] += 1

        self._profile["reputation_score"] = self.calculate_reputation()
        return self.get_agent_profile()

    def calculate_reputation(self) -> float:
        """Compute reputation as wins divided by total trades."""
        total_trades = self._profile["total_trades"]
        if total_trades == 0:
            return 0.0
        return round(self._profile["wins"] / total_trades, 4)


reputation_service = ReputationService()
