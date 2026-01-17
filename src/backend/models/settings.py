"""Application settings using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ReminderSettings(BaseSettings):
    """Reminder configuration."""

    enabled: bool = Field(default=True, description="Enable reminders")
    before_reset_minutes: list[int] = Field(
        default=[30, 15, 5],
        description="Minutes before reset to send reminder",
    )
    on_reset: bool = Field(default=True, description="Remind on reset")
    custom_command: str | None = Field(None, description="Custom command to run on reminder")


class AppSettings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    environment: str = Field(default="production", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")

    # Credentials path
    credentials_path: Path = Field(
        default=Path.home() / ".claude" / ".credentials.json",
        description="Path to Claude credentials file",
    )

    # API
    api_base_url: str = Field(
        default="https://api.anthropic.com",
        description="Anthropic API base URL",
    )
    cache_duration_seconds: int = Field(
        default=60,
        description="Cache duration for API responses",
    )

    # Reminders
    reminder: ReminderSettings = Field(
        default_factory=ReminderSettings,
        description="Reminder settings",
    )

    # UI
    theme: str = Field(default="dark", description="UI theme")


@lru_cache
def get_settings() -> AppSettings:
    """Get cached settings instance."""
    return AppSettings()
