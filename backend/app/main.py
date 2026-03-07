"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.agent import router as agent_router
from app.routes.backtest import router as backtest_router
from app.routes.market import router as market_router
from app.routes.trading import router as trading_router

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return health status for uptime checks."""
    return {"status": "ok"}


app.include_router(market_router)
app.include_router(agent_router)
app.include_router(trading_router)
app.include_router(backtest_router)
