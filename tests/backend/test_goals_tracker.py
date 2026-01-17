"""Tests for goals tracker module."""
import pytest
from datetime import datetime

from backend.core.goals_tracker import (
    GoalsTracker,
    PaceStatus,
    get_goals_tracker,
)
from backend.core.config_manager import AppConfig, GoalsConfig


class TestPaceStatus:
    """Test PaceStatus named tuple."""

    def test_pace_status_creation(self):
        """Test creating PaceStatus."""
        status = PaceStatus(
            is_on_track=True,
            current_usage=50.0,
            expected_usage=60.0,
            message="On track",
        )
        assert status.is_on_track is True
        assert status.current_usage == 50.0
        assert status.expected_usage == 60.0
        assert status.message == "On track"


class TestGoalsTracker:
    """Test GoalsTracker class."""

    def test_calculate_pace_disabled(self, monkeypatch):
        """Test pace calculation when goals disabled."""
        # Mock config to return disabled goals
        monkeypatch.setattr(
            "backend.core.goals_tracker.load_config",
            lambda: AppConfig(goals=GoalsConfig(enabled=False)),
        )

        tracker = GoalsTracker()
        pace = tracker.calculate_pace(50.0)

        assert pace.is_on_track is True
        assert pace.current_usage == 50.0
        assert pace.expected_usage == 0
        assert pace.message == ""

    def test_calculate_pace_on_track(self, monkeypatch):
        """Test pace calculation when on track."""
        monkeypatch.setattr(
            "backend.core.goals_tracker.load_config",
            lambda: AppConfig(goals=GoalsConfig(enabled=True, daily_budget_percent=100)),
        )

        tracker = GoalsTracker()
        # With 100% daily budget, any reasonable usage should be on track
        pace = tracker.calculate_pace(10.0)

        assert pace.is_on_track is True
        assert pace.current_usage == 10.0
        assert "On track" in pace.message or pace.message != ""

    def test_get_budget_status(self, monkeypatch):
        """Test budget status calculation."""
        monkeypatch.setattr(
            "backend.core.goals_tracker.load_config",
            lambda: AppConfig(goals=GoalsConfig(enabled=True, daily_budget_percent=80)),
        )

        tracker = GoalsTracker()
        used, budget, exceeded = tracker.get_budget_status(75.0)

        assert used == 75.0
        assert budget == 80
        assert exceeded is False

    def test_get_budget_status_exceeded(self, monkeypatch):
        """Test budget status when exceeded."""
        monkeypatch.setattr(
            "backend.core.goals_tracker.load_config",
            lambda: AppConfig(goals=GoalsConfig(enabled=True, daily_budget_percent=50)),
        )

        tracker = GoalsTracker()
        used, budget, exceeded = tracker.get_budget_status(75.0)

        assert used == 75.0
        assert budget == 50
        assert exceeded is True

    def test_should_warn(self, monkeypatch):
        """Test should_warn when goals enabled."""
        monkeypatch.setattr(
            "backend.core.goals_tracker.load_config",
            lambda: AppConfig(
                goals=GoalsConfig(
                    enabled=True,
                    daily_budget_percent=100,
                    warn_when_pace_exceeded=True,
                )
            ),
        )

        tracker = GoalsTracker()
        # Low usage should not warn
        assert tracker.should_warn(10.0) is False

    def test_should_warn_disabled(self, monkeypatch):
        """Test should_warn when goals disabled."""
        monkeypatch.setattr(
            "backend.core.goals_tracker.load_config",
            lambda: AppConfig(goals=GoalsConfig(enabled=False)),
        )

        tracker = GoalsTracker()
        assert tracker.should_warn(100.0) is False

    def test_singleton_instance(self):
        """Test get_goals_tracker returns singleton."""
        tracker1 = get_goals_tracker()
        tracker2 = get_goals_tracker()
        assert tracker1 is tracker2
