"""Tests for usage API client."""

from __future__ import annotations

import pytest

from backend.models.usage import FiveHourUsage, UsageResponse


class TestUsageModels:
    """Tests for usage models."""

    def test_five_hour_usage_valid(self) -> None:
        """Test valid FiveHourUsage model."""
        usage = FiveHourUsage(
            utilization=0.75,
            resets_at="2026-01-17T10:00:00Z",
        )
        assert usage.utilization == 0.75
        assert usage.resets_at == "2026-01-17T10:00:00Z"

    def test_usage_response_with_five_hour(self) -> None:
        """Test UsageResponse with five_hour data."""
        response = UsageResponse(
            five_hour=FiveHourUsage(
                utilization=0.5,
                resets_at="2026-01-17T10:00:00Z",
            ),
        )
        assert response.five_hour is not None
        assert response.five_hour.utilization == 0.5

    def test_usage_response_empty(self) -> None:
        """Test UsageResponse with no data."""
        response = UsageResponse()
        assert response.five_hour is None
        assert response.extra_usage is None
