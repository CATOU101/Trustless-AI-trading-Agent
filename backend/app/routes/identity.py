"""Agent identity API routes."""

from fastapi import APIRouter

from app.services.identity_service import identity_service

router = APIRouter(prefix="/agent", tags=["identity"])


@router.get("/identity")
async def get_agent_identity() -> dict[str, str]:
    """Return the persistent autonomous agent identity."""
    return dict(identity_service.get_identity())
