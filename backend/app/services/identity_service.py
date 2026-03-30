"""Persistent ERC-8004-style agent identity service."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

from app.services.wallet_service import wallet_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AgentIdentity(TypedDict):
    """Persistent identity payload for the autonomous trading agent."""

    agent_name: str
    wallet: str
    version: str
    created_at: str
    description: str


class IdentityService:
    """Create, load, and expose a stable agent identity."""

    _identity_path = Path(__file__).resolve().parents[1] / "agent_identity.json"

    def __init__(self) -> None:
        """Initialize identity cache."""
        self._identity: AgentIdentity | None = None

    def create_identity(self) -> AgentIdentity:
        """Create a new identity linked to the current wallet and persist it."""
        wallet_address = wallet_service.get_wallet_address()
        identity: AgentIdentity = {
            "agent_name": "AutoHedge AI",
            "wallet": wallet_address,
            "version": "1.0",
            "created_at": datetime.now(UTC).isoformat(),
            "description": "Autonomous multi-agent trading system",
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
        """Load persisted identity, creating one if needed."""
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
            "created_at": str(payload.get("created_at", datetime.now(UTC).isoformat())),
            "description": str(
                payload.get("description", "Autonomous multi-agent trading system")
            ),
        }
        self._identity = identity

        if str(payload.get("wallet", "")).lower() != wallet_address.lower():
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


identity_service = IdentityService()
