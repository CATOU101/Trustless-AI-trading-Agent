"""Application settings and environment configuration."""

from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Runtime settings for the Explainable AI Trading Agent backend."""

    app_name: str = Field(default="Explainable AI Trading Agent")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)


settings = AppSettings()
