"""FastAPI application entrypoint."""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.agent import router as agent_router
from app.routes.agents import router as agents_router
from app.routes.backtest import router as backtest_router
from app.routes.market import router as market_router
from app.routes.trading import router as trading_router
from app.services.agent_runner import agent_runner
from app.utils.task_cleanup import stop_background_tasks

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


@app.on_event("startup")
async def start_agent_loop() -> None:
    """Start the autonomous agent loop when the API boots."""
    app.state.agent_runner_task = asyncio.create_task(agent_runner.run_agent_loop())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Stop background tasks cleanly when the API shuts down."""
    await stop_background_tasks()


app.include_router(market_router)
app.include_router(agent_router)
app.include_router(agents_router)
app.include_router(trading_router)
app.include_router(backtest_router)
