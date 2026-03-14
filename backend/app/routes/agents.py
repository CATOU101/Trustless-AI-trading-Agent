"""Multi-agent platform API routes."""

from fastapi import APIRouter, HTTPException, Query, status

from app.models.decision import AgentDecisionResponse, AgentLeaderboardEntry
from app.services.agent_coordinator import agent_coordinator
from app.services.indicator_service import compute_indicators
from app.services.market_service import market_service
from app.services.reputation_service import reputation_service

router = APIRouter(prefix="/agents", tags=["agents"])

COIN_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
}


@router.get("")
async def list_agents() -> dict[str, list[str]]:
    """Return registered strategy agent names."""
    return {"agents": agent_coordinator.list_agents()}


@router.get("/leaderboard", response_model=list[AgentLeaderboardEntry])
async def get_leaderboard() -> list[AgentLeaderboardEntry]:
    """Return current agent leaderboard."""
    return [
        AgentLeaderboardEntry(**entry)
        for entry in reputation_service.get_agent_leaderboard()
    ]


@router.get("/decisions", response_model=AgentDecisionResponse)
async def get_agent_decisions(
    coin: str = Query(default="bitcoin", min_length=2, max_length=50)
) -> AgentDecisionResponse:
    """Return the latest coordinated agent votes for a coin."""
    normalized = COIN_MAP.get(coin.strip().lower(), coin.strip().lower())
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coin",
        )

    try:
        market_data = await market_service.get_coin_price(normalized)
        indicators = compute_indicators(market_data["prices"])
        coordination = await agent_coordinator.coordinate(
            asset=normalized,
            price=market_data["price"],
            change_24h=market_data["change_24h"],
            rsi=indicators["rsi"],
            ma20=indicators["ma20"],
        )
        return AgentDecisionResponse(
            asset=normalized,
            final_action=coordination["final_action"],
            confidence=coordination["confidence"],
            agent_votes=coordination["agent_votes"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to compute agent decisions for {normalized}.",
        ) from exc
