"""Tests for focus mode service."""
import pytest
from datetime import datetime, timedelta

from backend.scheduler.focus_mode import (
    FocusModeService,
    get_focus_mode_service,
)
from backend.core.config_manager import AppConfig, FocusModeConfig


class TestFocusModeService:
    """Test FocusModeService functionality."""

    def test_snooze(self):
        """Test snoozing notifications."""
        service = FocusModeService()
        assert service.is_snoozed() is False

        service.snooze(5)
        assert service.is_snoozed() is True
        assert service.get_snooze_remaining() > 0

    def test_clear_snooze(self):
        """Test clearing snooze."""
        service = FocusModeService()
        service.snooze(5)
        assert service.is_snoozed() is True

        service.clear_snooze()
        assert service.is_snoozed() is False
        assert service.get_snooze_remaining() == 0

    def test_is_dnd_by_usage_disabled(self, monkeypatch):
        """Test DND when focus mode disabled."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(focus_mode=FocusModeConfig(enabled=False)),
        )

        service = FocusModeService()
        assert service.is_dnd_by_usage(100.0) is False

    def test_is_dnd_by_usage_enabled(self, monkeypatch):
        """Test DND when usage exceeds threshold."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(
                focus_mode=FocusModeConfig(enabled=True, dnd_threshold=80)
            ),
        )

        service = FocusModeService()
        assert service.is_dnd_by_usage(50.0) is False
        assert service.is_dnd_by_usage(85.0) is True

    def test_is_in_quiet_hours_disabled(self, monkeypatch):
        """Test quiet hours when disabled."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(focus_mode=FocusModeConfig(enabled=False)),
        )

        service = FocusModeService()
        assert service.is_in_quiet_hours() is False

    def test_is_in_quiet_hours_no_config(self, monkeypatch):
        """Test quiet hours when not configured."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(
                focus_mode=FocusModeConfig(
                    enabled=True,
                    quiet_hours_start=None,
                    quiet_hours_end=None,
                )
            ),
        )

        service = FocusModeService()
        assert service.is_in_quiet_hours() is False

    def test_should_suppress_notification_snoozed(self, monkeypatch):
        """Test suppression when snoozed."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(focus_mode=FocusModeConfig(enabled=False)),
        )

        service = FocusModeService()
        service.snooze(5)
        assert service.should_suppress_notification(50.0) is True

    def test_get_suppression_reason_snoozed(self, monkeypatch):
        """Test getting suppression reason when snoozed."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(focus_mode=FocusModeConfig(enabled=False)),
        )

        service = FocusModeService()
        service.snooze(5)
        reason = service.get_suppression_reason(50.0)
        assert "Snoozed" in reason

    def test_get_suppression_reason_none(self, monkeypatch):
        """Test getting suppression reason when not suppressed."""
        monkeypatch.setattr(
            "backend.scheduler.focus_mode.load_config",
            lambda: AppConfig(focus_mode=FocusModeConfig(enabled=False)),
        )

        service = FocusModeService()
        reason = service.get_suppression_reason(50.0)
        assert reason is None

    def test_singleton_instance(self):
        """Test get_focus_mode_service returns singleton."""
        service1 = get_focus_mode_service()
        service2 = get_focus_mode_service()
        assert service1 is service2
