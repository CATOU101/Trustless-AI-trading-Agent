"""Artifact logging service for ERC-8004-style audit records."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

from app.utils.logger import get_logger

logger = get_logger(__name__)


class Artifact(TypedDict):
    """Normalized audit artifact."""

    type: str
    asset: str
    action: str
    confidence: float | None
    timestamp: str
    metadata: dict[str, Any]


class ArtifactService:
    """Persist and expose runtime audit artifacts."""

    _artifact_path = Path(__file__).resolve().parents[1] / "artifacts.json"

    def __init__(self) -> None:
        """Initialize artifact cache."""
        self._artifacts: list[Artifact] | None = None

    def _load_artifacts(self) -> list[Artifact]:
        """Load artifacts from disk if present."""
        if self._artifacts is not None:
            return self._artifacts
        if not self._artifact_path.exists():
            self._artifacts = []
            return self._artifacts
        try:
            payload = json.loads(self._artifact_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            self._artifacts = []
            return self._artifacts
        self._artifacts = list(payload) if isinstance(payload, list) else []
        return self._artifacts

    def _persist(self) -> None:
        """Persist current artifacts to disk."""
        self._artifact_path.write_text(
            json.dumps(self._load_artifacts(), indent=2),
            encoding="utf-8",
        )

    def _append_artifact(
        self,
        artifact_type: str,
        asset: str,
        action: str,
        confidence: float | None,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Append and persist a normalized artifact."""
        artifact: Artifact = {
            "type": artifact_type,
            "asset": asset,
            "action": action,
            "confidence": confidence,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }
        artifacts = self._load_artifacts()
        artifacts.append(artifact)
        self._persist()
        label = artifact_type.replace("_decision", "").replace("_check", "")
        logger.info("Artifact logged: %s", label)
        return artifact

    def log_strategy_decision(
        self,
        asset: str,
        action: str,
        confidence: float,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Log strategy decision artifact."""
        return self._append_artifact(
            "strategy_decision",
            asset,
            action,
            confidence,
            metadata,
        )

    def log_risk_check(
        self,
        asset: str,
        action: str,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Log risk evaluation artifact."""
        return self._append_artifact(
            "risk_check",
            asset,
            action,
            confidence,
            metadata,
        )

    def log_trade_intent(
        self,
        asset: str,
        action: str,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Log trade intent artifact."""
        return self._append_artifact(
            "trade_intent",
            asset,
            action,
            None,
            metadata,
        )

    def log_execution(
        self,
        asset: str,
        action: str,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Log trade execution artifact."""
        return self._append_artifact(
            "execution_result",
            asset,
            action,
            confidence,
            metadata,
        )

    def get_artifacts(self) -> list[Artifact]:
        """Return the current artifact list."""
        return list(self._load_artifacts())


artifact_service = ArtifactService()
