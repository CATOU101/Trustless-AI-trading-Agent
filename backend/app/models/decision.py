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
    market_cap: float | None = Field(
        default=None,
        ge=0,
        description="Current market capitalization when available.",
    )


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
    final_action: TradingDecision | None = Field(
        default=None,
        description="Aggregated action from the multi-agent coordinator.",
    )
    agent_votes: list[dict[str, str | float]] = Field(
        default_factory=list,
        description="Votes emitted by each strategy agent.",
    )
    leaderboard: list[dict[str, str | int | float]] = Field(
        default_factory=list,
        description="Per-agent performance snapshot for the dashboard.",
    )
    risk: dict[str, bool | float | str] = Field(
        default_factory=dict,
        description="Risk management outcome and adjusted position size.",
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


class AgentIdentityResponse(BaseModel):
    """Response model for the persistent ERC-8004-style agent identity."""

    agent_name: str = Field(..., description="Human-readable agent name.")
    wallet: str = Field(..., description="Wallet address linked to the agent.")
    version: str = Field(..., description="Identity document version.")
    registry_type: str = Field(..., description="Identity registry standard.")
    chain_id: int = Field(..., description="Chain identifier for signed intents.")
    agent_id: str = Field(..., description="Stable UUID for the agent identity.")
    created_at: str = Field(..., description="ISO 8601 creation timestamp.")
    description: str = Field(..., description="Short identity description.")
    capabilities: list[str] = Field(
        default_factory=list,
        description="Declared capabilities exposed by the autonomous agent.",
    )
    endpoints: dict[str, str] = Field(
        default_factory=dict,
        description="Relevant API endpoints exposed by the agent.",
    )
    artifact_endpoint: str = Field(
        ..., description="Primary endpoint for validation artifacts."
    )
    registry_agent_id: str | None = Field(
        default=None,
        description="Onchain AgentRegistry identifier when registration succeeds.",
    )
    allocation_claimed: bool = Field(
        default=False,
        description="Whether the Sepolia hackathon allocation has been claimed.",
    )


class AgentDecisionResponse(BaseModel):
    """Response model for aggregated multi-agent decisions."""

    asset: str = Field(..., description="CoinGecko asset id.")
    final_action: TradingDecision = Field(..., description="Aggregated platform action.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Aggregate confidence.")
    agent_votes: list[dict[str, str | float]] = Field(
        ..., description="Vote details from each agent."
    )


class AgentLeaderboardEntry(BaseModel):
    """Response model for per-agent leaderboard entries."""

    agent: str = Field(..., description="Strategy agent name.")
    total_trades: int = Field(..., ge=0)
    win_rate: float = Field(..., ge=0.0, le=1.0)
    profit: float = Field(..., description="Cumulative paper profit contribution.")
    average_return: float = Field(..., description="Average return per recorded trade.")
