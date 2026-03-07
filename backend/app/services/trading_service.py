"""Capital sandbox service for in-memory portfolio simulation."""

from datetime import UTC, datetime
from typing import TypedDict

from app.services.reputation_service import reputation_service


class PortfolioState(TypedDict):
    """Current portfolio state."""

    cash_balance: float
    assets: dict[str, float]


class PortfolioValue(TypedDict):
    """Calculated mark-to-market portfolio values for a single asset."""

    cash_balance: float
    asset_holdings: float
    portfolio_value: float


class TradeRecord(TypedDict):
    """Recorded simulated trade transaction."""

    timestamp: str
    asset: str
    decision: str
    price: float
    confidence: float
    cash_balance: float
    asset_holdings: float
    portfolio_value: float


class TradingService:
    """Service for virtual trade execution and portfolio valuation."""

    def __init__(self) -> None:
        """Initialize portfolio with default sandbox capital."""
        self._portfolio: PortfolioState = {
            "cash_balance": 10000.0,
            "assets": {"bitcoin": 0.0},
        }
        self._trade_history: list[TradeRecord] = []

    def get_portfolio(self) -> PortfolioState:
        """Return the current in-memory portfolio state."""
        return {
            "cash_balance": self._portfolio["cash_balance"],
            "assets": dict(self._portfolio["assets"]),
        }

    def execute_trade(
        self, asset: str, decision: str, price: float, confidence: float = 0.0
    ) -> PortfolioState:
        """Execute a virtual trade based on the decision signal.

        Rules:
        - BUY: spend 10% of available cash.
        - SELL: sell 10% of held quantity for the asset.
        - HOLD: no trade.
        """
        if price <= 0:
            raise ValueError("Price must be greater than zero.")

        normalized_asset = asset.strip().lower()
        normalized_decision = decision.strip().upper()
        self._portfolio["assets"].setdefault(normalized_asset, 0.0)
        pre_trade_total = self.calculate_portfolio_value(
            asset=normalized_asset, price=price
        )["portfolio_value"]

        if normalized_decision == "BUY":
            invest_amount = self._portfolio["cash_balance"] * 0.10
            asset_bought = invest_amount / price
            self._portfolio["cash_balance"] -= invest_amount
            self._portfolio["assets"][normalized_asset] += asset_bought
        elif normalized_decision == "SELL":
            held_quantity = self._portfolio["assets"][normalized_asset]
            quantity_to_sell = held_quantity * 0.10
            proceeds = quantity_to_sell * price
            self._portfolio["assets"][normalized_asset] -= quantity_to_sell
            self._portfolio["cash_balance"] += proceeds
        elif normalized_decision == "HOLD":
            pass
        else:
            raise ValueError("Decision must be BUY, SELL, or HOLD.")

        if normalized_decision in {"BUY", "SELL"}:
            post_trade_total = self.calculate_portfolio_value(
                asset=normalized_asset, price=price
            )["portfolio_value"]
            snapshot = self.calculate_portfolio_value(asset=normalized_asset, price=price)
            self._trade_history.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "asset": normalized_asset,
                    "decision": normalized_decision,
                    "price": round(price, 6),
                    "confidence": round(confidence, 4),
                    "cash_balance": snapshot["cash_balance"],
                    "asset_holdings": snapshot["asset_holdings"],
                    "portfolio_value": snapshot["portfolio_value"],
                }
            )
            if post_trade_total > pre_trade_total:
                reputation_service.record_trade("WIN")
            elif post_trade_total < pre_trade_total:
                reputation_service.record_trade("LOSS")
            else:
                reputation_service.record_trade("NEUTRAL")

        return self.get_portfolio()

    def calculate_portfolio_value(self, asset: str, price: float) -> PortfolioValue:
        """Calculate total portfolio value using latest asset price."""
        if price < 0:
            raise ValueError("Price must be non-negative.")

        normalized_asset = asset.strip().lower()
        holdings = self._portfolio["assets"].get(normalized_asset, 0.0)
        cash_balance = self._portfolio["cash_balance"]
        asset_value = holdings * price

        return {
            "cash_balance": round(cash_balance, 6),
            "asset_holdings": round(holdings, 10),
            "portfolio_value": round(cash_balance + asset_value, 6),
        }

    def get_trade_history(self) -> list[TradeRecord]:
        """Return trade history in reverse chronological order."""
        return list(reversed(self._trade_history))


trading_service = TradingService()
