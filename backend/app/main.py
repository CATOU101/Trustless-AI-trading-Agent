"""FastAPI application entrypoint."""

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.agent import router as agent_router
from app.routes.agents import router as agents_router
from app.routes.artifacts import router as artifacts_router
from app.routes.backtest import router as backtest_router
from app.routes.identity import router as identity_router
from app.routes.market import router as market_router
from app.routes.trading import router as trading_router
from app.routes.wallet import router as wallet_router
from app.services.agent_runner import agent_runner
from app.services.erc8004_service import erc8004_service
from app.services.identity_service import identity_service
from app.utils.logger import get_logger
from app.utils.task_cleanup import stop_background_tasks

logger = get_logger(__name__)

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
    identity_path = identity_service._identity_path
    existed = identity_path.exists()
    identity = identity_service.load_identity()
    registry_agent_id = erc8004_service.register_agent(identity)
    if registry_agent_id and identity.get("registry_agent_id") != registry_agent_id:
        identity["registry_agent_id"] = registry_agent_id
        identity_service.persist_identity(identity)
    if identity.get("registry_agent_id") and not identity.get("allocation_claimed", False):
        claim_tx = erc8004_service.claim_allocation(identity["registry_agent_id"])
        if claim_tx:
            identity["allocation_claimed"] = True
            identity_service.persist_identity(identity)
    if existed:
        logger.info("Agent identity loaded")
    else:
        logger.info("Agent identity created")
    app.state.agent_runner_task = asyncio.create_task(agent_runner.run_agent_loop())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Stop background tasks cleanly when the API shuts down."""
    await stop_background_tasks()


app.include_router(market_router)
app.include_router(agent_router)
app.include_router(artifacts_router)
app.include_router(identity_router)
app.include_router(agents_router)
app.include_router(trading_router)
app.include_router(backtest_router)
app.include_router(wallet_router)
