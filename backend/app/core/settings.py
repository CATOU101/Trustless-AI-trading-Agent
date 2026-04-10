"""Application settings and environment configuration."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


def _load_env_file() -> None:
    """Load simple KEY=VALUE pairs from backend/.env into the process env.

    This keeps configuration lightweight without introducing another settings
    dependency. Existing environment variables always win over values in the file.
    """

    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            os.environ.setdefault(key, value)


_load_env_file()


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment flag with a safe default."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class AppSettings(BaseModel):
    """Runtime settings for the AutoHedge AI backend."""

    app_name: str = Field(default="AutoHedge AI")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    use_llm: bool = Field(default=_env_bool("USE_LLM", True))
    sepolia_rpc_url: str | None = Field(default=os.getenv("SEPOLIA_RPC_URL"))
    agent_private_key: str | None = Field(default=os.getenv("AGENT_PRIVATE_KEY"))


settings = AppSettings()
