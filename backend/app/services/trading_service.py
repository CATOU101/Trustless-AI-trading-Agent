"""Capital sandbox service for in-memory portfolio simulation."""

from datetime import UTC, datetime
from typing import TypedDict

from app.services.artifact_service import artifact_service
from app.services.dex_service import dex_service
from app.services.intent_service import intent_service
from app.services.kraken_service import kraken_cli_available, kraken_service
from app.services.reputation_service import reputation_service
from app.services.wallet_service import wallet_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


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
    position_size: float
    wallet: str
    intent_signature: str
    dex_source: str
    dex_price: float


def enforce_position_rules(
    action: str,
    asset: str,
    portfolio: dict[str, float],
) -> tuple[str, str | None]:
    """Prevent impossible trades when cash or holdings are unavailable."""
    holdings = float(portfolio.get(asset, 0.0))
    cash = float(portfolio.get("cash_balance", 0.0))

    if action == "SELL" and holdings <= 0:
        return "HOLD", "No holdings available to sell."

    if action == "BUY" and cash <= 0:
        return "HOLD", "No cash available to buy."

    return action, None


class TradingService:
    """Service for virtual trade execution and portfolio valuation."""

    _asset_symbol_map = {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "solana": "SOL",
        "dogecoin": "DOGE",
        "cardano": "ADA",
    }

    def __init__(self) -> None:
        """Initialize portfolio with default sandbox capital."""
        self._portfolio: PortfolioState = {
            "cash_balance": 10000.0,
            "assets": {"ethereum": 0.0},
        }
        self._trade_history: list[TradeRecord] = []
        self._peak_portfolio_value = 10000.0

    def get_portfolio(self) -> PortfolioState:
        """Return the current in-memory portfolio state."""
        return {
            "cash_balance": self._portfolio["cash_balance"],
            "assets": dict(self._portfolio["assets"]),
        }

    def _resolve_asset_symbol(self, asset: str) -> str:
        """Resolve a CoinGecko asset id to a signer-friendly symbol."""
        return self._asset_symbol_map.get(asset, asset.upper())

    def execute_trade(
        self,
        asset: str,
        decision: str,
        price: float,
        confidence: float = 0.0,
        position_size: float = 0.10,
        agent: str = "AgentCoordinator",
    ) -> PortfolioState:
        """Execute a virtual trade based on the decision signal.

        Rules:
        - BUY: spend 10% of available cash.
        - SELL: sell 10% of held quantity for the asset.
        - HOLD: no trade.
        """
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if not 0.0 <= position_size <= 1.0:
            raise ValueError("Position size must be between 0 and 1.")

        normalized_asset = asset.strip().lower()
        normalized_decision = decision.strip().upper()
        self._portfolio["assets"].setdefault(normalized_asset, 0.0)
        pre_trade_total = self.calculate_portfolio_value(
            asset=normalized_asset, price=price
        )["portfolio_value"]

        if normalized_decision not in {"BUY", "SELL", "HOLD"}:
            raise ValueError("Decision must be BUY, SELL, or HOLD.")

        wallet_address = wallet_service.get_wallet_address()
        if normalized_decision == "BUY":
            intended_amount = self._portfolio["cash_balance"] * position_size
        elif normalized_decision == "SELL":
            held_quantity = self._portfolio["assets"][normalized_asset]
            intended_amount = held_quantity * position_size
        else:
            intended_amount = 0.0

        intent = intent_service.create_trade_intent(
            decision={
                "asset": self._resolve_asset_symbol(normalized_asset),
                "final_action": normalized_decision,
            },
            amount=intended_amount,
            agent=agent,
            wallet=wallet_address,
        )
        logger.info(
            "Intent created: asset=%s action=%s amount=%s agent=%s",
            intent["asset"],
            intent["action"],
            intent["amount"],
            agent,
        )
        print(
            f"Intent created: asset={intent['asset']} action={intent['action']} amount={intent['amount']}"
        )
        signature = intent_service.sign_intent(intent)
        if not intent_service.verify_signature(intent, signature):
            raise ValueError("Trade intent signature verification failed.")
        artifact_service.log_trade_intent(
            asset=normalized_asset,
            action=normalized_decision,
            metadata={
                "agent": agent,
                "wallet": wallet_address,
                "intent": intent,
                "signature": signature,
            },
        )

        if normalized_decision == "HOLD":
            return self.get_portfolio()

        if intended_amount <= 0:
            return self.get_portfolio()

        execution_source = "sandbox"
        execution_price = price
        sandbox_execution = None
        if kraken_cli_available():
            try:
                logger.info(
                    "Execution path: Kraken | asset=%s action=%s",
                    normalized_asset,
                    normalized_decision,
                )
                print("Execution path: Kraken")
                kraken_execution = kraken_service.execute_kraken_trade(
                    normalized_asset,
                    normalized_decision,
                    intended_amount,
                )
                execution_source = "kraken"
                execution_price = (
                    kraken_service.extract_execution_price(kraken_execution) or price
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Execution failed, fallback to sandbox | asset=%s action=%s error=%s",
                    normalized_asset,
                    normalized_decision,
                    exc,
                )
                print("Execution failed, fallback to sandbox")
                execution_source = "sandbox"
                sandbox_execution = dex_service.simulate_swap(intent)
        else:
            logger.info(
                "Execution path: Sandbox | asset=%s action=%s",
                normalized_asset,
                normalized_decision,
            )
            print("Execution path: Sandbox")
            sandbox_execution = dex_service.simulate_swap(intent)

        if normalized_decision == "BUY":
            if execution_source == "kraken":
                invest_amount = min(intended_amount, self._portfolio["cash_balance"])
                if execution_price <= 0:
                    return self.get_portfolio()
                asset_bought = invest_amount / execution_price
            else:
                invest_amount = min(
                    sandbox_execution["sell_amount"],
                    self._portfolio["cash_balance"],
                )
                quote_sell_amount = sandbox_execution["sell_amount"]
                quote_buy_amount = sandbox_execution["buy_amount"]
                if quote_sell_amount <= 0:
                    return self.get_portfolio()

                buy_scaler = invest_amount / quote_sell_amount
                asset_bought = quote_buy_amount * buy_scaler
            self._portfolio["cash_balance"] -= invest_amount
            self._portfolio["assets"][normalized_asset] += asset_bought
        else:
            held_quantity = self._portfolio["assets"][normalized_asset]
            if execution_source == "kraken":
                quantity_to_sell = min(intended_amount, held_quantity)
                proceeds = quantity_to_sell * execution_price
            else:
                quantity_to_sell = min(sandbox_execution["sell_amount"], held_quantity)
                quote_sell_amount = sandbox_execution["sell_amount"]
                quote_buy_amount = sandbox_execution["buy_amount"]
                if quote_sell_amount <= 0:
                    return self.get_portfolio()

                sell_scaler = quantity_to_sell / quote_sell_amount
                proceeds = quote_buy_amount * sell_scaler
            self._portfolio["assets"][normalized_asset] -= quantity_to_sell
            self._portfolio["cash_balance"] += proceeds

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
                "position_size": round(position_size, 4),
                "wallet": wallet_address,
                "intent_signature": signature,
                "dex_source": execution_source,
                "dex_price": round(execution_price, 10),
            }
        )
        artifact_service.log_execution(
            asset=normalized_asset,
            action=normalized_decision,
            confidence=confidence,
            metadata={
                "wallet": wallet_address,
                "position_size": round(position_size, 4),
                "execution_source": execution_source,
                "execution_price": round(execution_price, 10),
                "portfolio_value": snapshot["portfolio_value"],
            },
        )
        logger.info(
            "Trade executed | asset=%s action=%s wallet=%s dex_source=%s",
            normalized_asset,
            normalized_decision,
            wallet_address,
            execution_source,
        )
        self._peak_portfolio_value = max(self._peak_portfolio_value, snapshot["portfolio_value"])
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

    def get_last_trade_timestamp(self) -> str | None:
        """Return the latest trade timestamp if present."""
        if not self._trade_history:
            return None
        return self._trade_history[-1]["timestamp"]

    def get_peak_portfolio_value(self) -> float:
        """Return the historical peak portfolio value."""
        return self._peak_portfolio_value


trading_service = TradingService()
