"""Shared fixtures for backend tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from backend.models.usage import ExtraUsage, FiveHourUsage, UsageResponse


@pytest.fixture
def mock_five_hour_usage() -> FiveHourUsage:
    """Create mock FiveHourUsage."""
    return FiveHourUsage(
        utilization=0.45,
        resets_at="2026-01-17T12:00:00Z",
    )


@pytest.fixture
def mock_extra_usage() -> ExtraUsage:
    """Create mock ExtraUsage."""
    return ExtraUsage(
        is_enabled=False,
        monthly_limit=None,
        used_credits=None,
        utilization=None,
    )


@pytest.fixture
def mock_usage_response(
    mock_five_hour_usage: FiveHourUsage,
    mock_extra_usage: ExtraUsage,
) -> UsageResponse:
    """Create mock UsageResponse."""
    return UsageResponse(
        five_hour=mock_five_hour_usage,
        extra_usage=mock_extra_usage,
    )


@pytest.fixture
def mock_usage_json(mock_usage_response: UsageResponse) -> dict[str, Any]:
    """Create mock usage JSON response."""
    return mock_usage_response.model_dump()


@pytest.fixture
def mock_credentials_file(tmp_path: Path) -> Path:
    """Create mock credentials file."""
    creds_data = {
        "claudeAiOauth": {
            "access_token": "test-token-12345",
            "refresh_token": "test-refresh-token",
            "expires_at": 9999999999,
            "subscription_type": "pro",
            "rate_limit_tier": "tier1",
        }
    }
    creds_file = tmp_path / ".credentials.json"
    creds_file.write_text(json.dumps(creds_data))
    return creds_file


@pytest.fixture
def mock_empty_credentials_file(tmp_path: Path) -> Path:
    """Create empty credentials file."""
    creds_file = tmp_path / ".credentials.json"
    creds_file.write_text("{}")
    return creds_file


@pytest.fixture(autouse=True)
def reset_caches():
    """Reset module caches before each test."""
    from backend.api.usage import clear_usage_cache
    from backend.utils.credentials import clear_credentials_cache

    clear_usage_cache()
    clear_credentials_cache()
    yield
    clear_usage_cache()
    clear_credentials_cache()


@pytest.fixture
def mock_settings(tmp_path: Path):
    """Mock settings with test values."""
    from backend.models.settings import Settings

    test_settings = Settings(
        api_base_url="https://api.claude.ai",
        cache_duration_seconds=30,
        credentials_path=tmp_path / ".credentials.json",
        config_dir=tmp_path / "config",
    )

    with patch("backend.models.settings.get_settings", return_value=test_settings):
        yield test_settings
