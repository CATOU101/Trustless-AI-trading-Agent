"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.config import settings
from app.routes.agent import router as agent_router
from app.routes.market import router as market_router

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return health status for uptime checks."""
    return {"status": "ok"}


app.include_router(market_router)
app.include_router(agent_router)
