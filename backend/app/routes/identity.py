"""Agent identity API routes."""

from fastapi import APIRouter

from app.models.decision import AgentIdentityResponse
from app.services.identity_service import identity_service

router = APIRouter(prefix="/agent", tags=["identity"])


@router.get("/identity", response_model=AgentIdentityResponse)
async def get_agent_identity() -> AgentIdentityResponse:
    """Return the persistent autonomous agent identity."""
    return AgentIdentityResponse(**identity_service.get_identity())
