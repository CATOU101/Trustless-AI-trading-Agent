"""Persistent ERC-8004-style agent identity service."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from app.services.wallet_service import wallet_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AgentIdentity(TypedDict):
    """Persistent identity payload for the autonomous trading agent."""

    agent_name: str
    wallet: str
    version: str
    registry_type: str
    chain_id: int
    agent_id: str
    created_at: str
    description: str
    capabilities: list[str]
    endpoints: dict[str, str]
    artifact_endpoint: str
    registry_agent_id: str | None
    allocation_claimed: bool


class IdentityService:
    """Create, load, and expose a stable agent identity."""

    _identity_path = Path(__file__).resolve().parents[1] / "agent_identity.json"

    def __init__(self) -> None:
        """Initialize identity cache."""
        self._identity: AgentIdentity | None = None

    def create_identity(self) -> AgentIdentity:
        """Create and persist an ERC-8004-compatible identity document."""
        wallet_address = wallet_service.get_wallet_address()
        identity: AgentIdentity = {
            "agent_name": "AutoHedge AI",
            "wallet": wallet_address,
            "version": "1.0",
            "registry_type": "ERC-8004",
            "chain_id": 11155111,
            "agent_id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "description": "Autonomous multi-agent trading system",
            "capabilities": ["trade", "risk", "backtest"],
            "endpoints": {
                "decision": "/agent/decision",
                "artifacts": "/agent/artifacts",
            },
            "artifact_endpoint": "/agent/artifacts",
            "registry_agent_id": None,
            "allocation_claimed": False,
        }
        self._identity_path.write_text(
            json.dumps(identity, indent=2),
            encoding="utf-8",
        )
        self._identity = identity
        logger.info("Identity created")
        logger.info("Wallet linked to identity: %s", wallet_address)
        return identity

    def load_identity(self) -> AgentIdentity:
        """Load persisted ERC-8004 identity, creating one if needed."""
        if self._identity is not None:
            logger.info("Identity loaded")
            return self._identity

        if not self._identity_path.exists():
            logger.info("Agent identity created")
            return self.create_identity()

        try:
            payload = json.loads(self._identity_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            logger.warning("Identity file unreadable. Recreating identity.")
            logger.info("Agent identity created")
            return self.create_identity()

        wallet_address = wallet_service.get_wallet_address()
        identity: AgentIdentity = {
            "agent_name": str(payload.get("agent_name", "AutoHedge AI")),
            "wallet": wallet_address,
            "version": str(payload.get("version", "1.0")),
            "registry_type": str(payload.get("registry_type", "ERC-8004")),
            "chain_id": int(payload.get("chain_id", 11155111)),
            "agent_id": str(payload.get("agent_id", uuid4())),
            "created_at": str(payload.get("created_at", datetime.now(UTC).isoformat())),
            "description": str(
                payload.get("description", "Autonomous multi-agent trading system")
            ),
            "capabilities": list(payload.get("capabilities", ["trade", "risk", "backtest"])),
            "endpoints": dict(
                payload.get(
                    "endpoints",
                    {
                        "decision": "/agent/decision",
                        "artifacts": "/agent/artifacts",
                    },
                )
            ),
            "artifact_endpoint": str(
                payload.get("artifact_endpoint", "/agent/artifacts")
            ),
            "registry_agent_id": (
                None
                if payload.get("registry_agent_id") in {None, ""}
                else str(payload.get("registry_agent_id"))
            ),
            "allocation_claimed": bool(payload.get("allocation_claimed", False)),
        }
        self._identity = identity

        needs_persist = (
            str(payload.get("wallet", "")).lower() != wallet_address.lower()
            or "registry_type" not in payload
            or "chain_id" not in payload
            or "agent_id" not in payload
            or "capabilities" not in payload
            or "endpoints" not in payload
            or "artifact_endpoint" not in payload
            or "registry_agent_id" not in payload
            or "allocation_claimed" not in payload
        )
        if needs_persist:
            self._identity_path.write_text(
                json.dumps(identity, indent=2),
                encoding="utf-8",
            )
            logger.info("Wallet linked to identity: %s", wallet_address)

        logger.info("Identity loaded")
        return identity

    def get_identity(self) -> AgentIdentity:
        """Return the current agent identity."""
        return self.load_identity()

    def persist_identity(self, identity: AgentIdentity) -> AgentIdentity:
        """Persist an updated identity document to disk and cache."""
        self._identity_path.write_text(
            json.dumps(identity, indent=2),
            encoding="utf-8",
        )
        self._identity = identity
        return identity


identity_service = IdentityService()
