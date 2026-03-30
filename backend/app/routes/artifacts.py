"""Artifact API routes."""

from fastapi import APIRouter

from app.services.artifact_service import artifact_service

router = APIRouter(prefix="/agent", tags=["artifacts"])


@router.get("/artifacts")
async def get_artifacts() -> list[dict[str, object]]:
    """Return persisted audit artifacts."""
    return artifact_service.get_artifacts()
