"""Usage response models from Anthropic OAuth API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FiveHourUsage(BaseModel):
    """5-hour usage window data."""

    utilization: float = Field(..., description="Usage utilization (0.0 - 1.0)")
    resets_at: str = Field(..., description="ISO 8601 timestamp when quota resets")


class ExtraUsage(BaseModel):
    """Extra usage (paid) data."""

    is_enabled: bool = Field(..., description="Whether extra usage is enabled")
    monthly_limit: float | None = Field(None, description="Monthly spending limit")
    used_credits: float | None = Field(None, description="Credits used this month")
    utilization: float | None = Field(None, description="Extra usage utilization")


class UsageResponse(BaseModel):
    """Response from Anthropic OAuth Usage API."""

    five_hour: FiveHourUsage | None = Field(None, description="5-hour usage window")
    extra_usage: ExtraUsage | None = Field(None, description="Extra usage data")

    # Unused fields (kept for completeness)
    seven_day: dict | None = Field(None, description="7-day usage data")
    seven_day_opus: dict | None = Field(None, description="7-day Opus usage")
    seven_day_sonnet: dict | None = Field(None, description="7-day Sonnet usage")
    seven_day_oauth_apps: dict | None = Field(None, description="7-day OAuth apps usage")
