"""Tests for Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.models.usage import ExtraUsage, FiveHourUsage, UsageResponse


class TestFiveHourUsage:
    """Tests for FiveHourUsage model."""

    def test_valid_creation(self):
        """Test creating valid FiveHourUsage."""
        usage = FiveHourUsage(
            utilization=0.5,
            resets_at="2026-01-17T12:00:00Z",
        )
        assert usage.utilization == 0.5
        assert usage.resets_at == "2026-01-17T12:00:00Z"

    def test_utilization_zero(self):
        """Test utilization at zero."""
        usage = FiveHourUsage(utilization=0.0, resets_at="2026-01-17T12:00:00Z")
        assert usage.utilization == 0.0

    def test_utilization_full(self):
        """Test utilization at full."""
        usage = FiveHourUsage(utilization=1.0, resets_at="2026-01-17T12:00:00Z")
        assert usage.utilization == 1.0

    def test_utilization_over_full(self):
        """Test utilization over 100% is valid."""
        usage = FiveHourUsage(utilization=1.5, resets_at="2026-01-17T12:00:00Z")
        assert usage.utilization == 1.5

    def test_missing_utilization_raises(self):
        """Test missing utilization raises ValidationError."""
        with pytest.raises(ValidationError):
            FiveHourUsage(resets_at="2026-01-17T12:00:00Z")  # type: ignore

    def test_missing_resets_at_raises(self):
        """Test missing resets_at raises ValidationError."""
        with pytest.raises(ValidationError):
            FiveHourUsage(utilization=0.5)  # type: ignore


class TestExtraUsage:
    """Tests for ExtraUsage model."""

    def test_disabled_extra_usage(self):
        """Test disabled extra usage."""
        usage = ExtraUsage(is_enabled=False)
        assert usage.is_enabled is False
        assert usage.monthly_limit is None
        assert usage.used_credits is None
        assert usage.utilization is None

    def test_enabled_extra_usage(self):
        """Test enabled extra usage with limits."""
        usage = ExtraUsage(
            is_enabled=True,
            monthly_limit=100.0,
            used_credits=45.0,
            utilization=0.45,
        )
        assert usage.is_enabled is True
        assert usage.monthly_limit == 100.0
        assert usage.used_credits == 45.0
        assert usage.utilization == 0.45


class TestUsageResponse:
    """Tests for UsageResponse model."""

    def test_full_response(self):
        """Test full response with all fields."""
        response = UsageResponse(
            five_hour=FiveHourUsage(
                utilization=0.3,
                resets_at="2026-01-17T12:00:00Z",
            ),
            extra_usage=ExtraUsage(is_enabled=False),
        )
        assert response.five_hour is not None
        assert response.five_hour.utilization == 0.3
        assert response.extra_usage is not None
        assert response.extra_usage.is_enabled is False

    def test_minimal_response(self):
        """Test minimal response with only required fields."""
        response = UsageResponse()
        assert response.five_hour is None
        assert response.extra_usage is None

    def test_from_api_json(self):
        """Test creating from API JSON response."""
        json_data = {
            "five_hour": {
                "utilization": 0.75,
                "resets_at": "2026-01-17T15:30:00Z",
            },
            "extra_usage": {
                "is_enabled": True,
                "monthly_limit": 50.0,
                "used_credits": 25.0,
                "utilization": 0.5,
            },
        }
        response = UsageResponse.model_validate(json_data)
        assert response.five_hour is not None
        assert response.five_hour.utilization == 0.75
        assert response.extra_usage is not None
        assert response.extra_usage.monthly_limit == 50.0

    def test_model_dump(self):
        """Test model serialization."""
        response = UsageResponse(
            five_hour=FiveHourUsage(
                utilization=0.5,
                resets_at="2026-01-17T12:00:00Z",
            ),
        )
        dumped = response.model_dump()
        assert "five_hour" in dumped
        assert dumped["five_hour"]["utilization"] == 0.5
