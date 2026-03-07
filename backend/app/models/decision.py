"""Pydantic models for market and decision APIs."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TradingDecision(str, Enum):
    """Supported agent trading actions."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class MarketPriceResponse(BaseModel):
    """Response model for market price endpoint."""

    asset: str = Field(..., description="CoinGecko asset id.")
    price_usd: float = Field(..., ge=0, description="Current market price in USD.")
    change_24h: float = Field(..., description="24-hour percentage price change.")
    market_cap: float = Field(..., ge=0, description="Current market capitalization.")


class AnalyzeRequest(BaseModel):
    """Request payload for decision analysis."""

    coin: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="CoinGecko asset id (for example: bitcoin, ethereum).",
    )

    @field_validator("coin")
    @classmethod
    def normalize_coin(cls, value: str) -> str:
        """Normalize the coin id to lowercase for consistency."""
        return value.strip().lower()


class AnalyzeResponse(BaseModel):
    """Agent output with explainable decision."""

    asset: str = Field(..., description="CoinGecko asset id.")
    decision: TradingDecision = Field(..., description="BUY, SELL, or HOLD.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Decision confidence.")
    reasoning: str = Field(..., min_length=5, description="Human-readable explanation.")
    portfolio: dict[str, float] = Field(
        ...,
        description=(
            "Portfolio summary including cash balance, asset amount for the analyzed "
            "coin, and total portfolio value."
        ),
    )
    indicators: dict[str, float] = Field(
        ...,
        description="Technical indicators used for analysis (RSI and MA20).",
    )


class AgentProfileResponse(BaseModel):
    """Response model for agent identity and reputation profile."""

    agent_id: str = Field(..., description="Stable identifier for the trading agent.")
    strategy: str = Field(..., description="High-level strategy description.")
    created_at: str = Field(..., description="ISO 8601 creation timestamp.")
    total_trades: int = Field(..., ge=0, description="Total recorded trades.")
    wins: int = Field(..., ge=0, description="Number of winning trades.")
    losses: int = Field(..., ge=0, description="Number of losing trades.")
    reputation_score: float = Field(
        ..., ge=0.0, le=1.0, description="Wins divided by total trades."
    )
