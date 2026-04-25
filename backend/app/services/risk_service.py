"""Risk management rules for coordinated trading decisions."""

from datetime import UTC, datetime, timedelta
from typing import TypedDict


class RiskCheck(TypedDict):
    """Risk filter output."""

    allowed: bool
    adjusted_position_size: float
    reason: str


class RiskService:
    """Applies portfolio-level constraints before trade execution."""

    def evaluate(
        self,
        *,
        current_portfolio_value: float,
        peak_portfolio_value: float,
        volatility: float,
        last_trade_timestamp: str | None,
    ) -> RiskCheck:
        """Return whether trading is allowed and what size to use."""
        adjusted_position_size = 0.10
        reason = "Risk checks passed."

        if peak_portfolio_value > 0:
            drawdown = (peak_portfolio_value - current_portfolio_value) / peak_portfolio_value
            if drawdown > 0.20:
                return {
                    "allowed": False,
                    "adjusted_position_size": 0.0,
                    "reason": "Trading blocked due to portfolio drawdown above 20%.",
                }

        if volatility > 6:
            adjusted_position_size = 0.05
            reason = "Volatility elevated. Position size reduced to 5%."

        if last_trade_timestamp:
            last_trade_time = datetime.fromisoformat(last_trade_timestamp)
            if datetime.now(UTC) - last_trade_time < timedelta(minutes=3):
                return {
                    "allowed": False,
                    "adjusted_position_size": 0.0,
                    "reason": "Trading blocked to avoid repeated trades within 3 minutes.",
                }

        return {
            "allowed": True,
            "adjusted_position_size": adjusted_position_size,
            "reason": reason,
        }


risk_service = RiskService()
