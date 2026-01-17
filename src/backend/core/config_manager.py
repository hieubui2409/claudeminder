"""TOML configuration manager for Claudiminder."""
from pathlib import Path
from typing import Any

import tomli
import tomli_w
from pydantic import BaseModel, Field

CONFIG_DIR = Path.home() / ".config" / "backend"
CONFIG_FILE = CONFIG_DIR / "config.toml"


class ReminderConfig(BaseModel):
    """Reminder settings."""
    enabled: bool = True
    before_reset_minutes: list[int] = Field(default_factory=lambda: [15, 30, 60])
    on_reset: bool = True
    percentage_thresholds: list[int] = Field(default_factory=lambda: [50, 75, 90, 100])
    snooze_minutes: list[int] = Field(default_factory=lambda: [5, 15, 30])
    custom_command: str | None = None
    custom_url: str | None = None


class FocusModeConfig(BaseModel):
    """Focus mode / DND settings."""
    enabled: bool = False
    dnd_threshold: int = 80
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None


class GoalsConfig(BaseModel):
    """Daily usage goals settings."""
    enabled: bool = False
    daily_budget_percent: int = 100
    warn_when_pace_exceeded: bool = True


class AppConfig(BaseModel):
    """Main application configuration."""
    language: str = "en"
    log_level: str = "INFO"
    poll_interval_seconds: int = 60
    reminder: ReminderConfig = Field(default_factory=ReminderConfig)
    focus_mode: FocusModeConfig = Field(default_factory=FocusModeConfig)
    goals: GoalsConfig = Field(default_factory=GoalsConfig)


def load_config() -> AppConfig:
    """Load config from TOML file, or return defaults."""
    if not CONFIG_FILE.exists():
        return AppConfig()
    with open(CONFIG_FILE, "rb") as f:
        data = tomli.load(f)
    return AppConfig.model_validate(data)


def _remove_none_values(d: dict[str, Any]) -> dict[str, Any]:
    """Recursively remove None values from dict for TOML serialization."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _remove_none_values(v)
        elif v is not None:
            result[k] = v
    return result


def save_config(config: AppConfig) -> None:
    """Save config to TOML file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Remove None values as TOML doesn't support them
    data = _remove_none_values(config.model_dump())
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(data, f)


def get_config_path() -> Path:
    """Get the config file path."""
    return CONFIG_FILE
