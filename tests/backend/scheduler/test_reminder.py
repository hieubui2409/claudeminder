"""Tests for reminder service."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.scheduler.reminder_service import (
    ReminderService,
    ReminderType,
    get_reminder_service,
)


@pytest.fixture
def reminder_service() -> ReminderService:
    """Create fresh reminder service instance."""
    return ReminderService()


@pytest.fixture
def mock_config():
    """Mock reminder config."""
    mock = MagicMock()
    mock.reminder.enabled = True
    mock.reminder.percentage_thresholds = [50, 75, 90, 100]
    mock.reminder.before_reset_minutes = [15, 30, 60]
    mock.reminder.on_reset = True
    return mock


class TestReminderService:
    """Tests for ReminderService class."""

    def test_initial_state(self, reminder_service: ReminderService):
        """Test initial state is empty."""
        assert len(reminder_service._triggered_percentages) == 0
        assert len(reminder_service._triggered_before_reset) == 0
        assert reminder_service._reset_triggered is False

    def test_reset_triggers(self, reminder_service: ReminderService):
        """Test reset_triggers clears all state."""
        reminder_service._triggered_percentages.add(50)
        reminder_service._triggered_before_reset.add(15)
        reminder_service._reset_triggered = True

        reminder_service.reset_triggers()

        assert len(reminder_service._triggered_percentages) == 0
        assert len(reminder_service._triggered_before_reset) == 0
        assert reminder_service._reset_triggered is False

    def test_add_and_remove_callback(self, reminder_service: ReminderService):
        """Test adding and removing callbacks."""

        def test_callback(t: ReminderType, m: str) -> None:
            pass

        reminder_service.add_callback(test_callback)
        assert test_callback in reminder_service._callbacks

        reminder_service.remove_callback(test_callback)
        assert test_callback not in reminder_service._callbacks

    def test_remove_nonexistent_callback(self, reminder_service: ReminderService):
        """Test removing non-existent callback doesn't raise."""

        def test_callback(t: ReminderType, m: str) -> None:
            pass

        reminder_service.remove_callback(test_callback)  # Should not raise


class TestCheckAndTrigger:
    """Tests for check_and_trigger method."""

    def test_returns_empty_when_disabled(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test returns empty when reminders disabled."""
        mock_config.reminder.enabled = False

        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            result = reminder_service.check_and_trigger(95.0, None)
            assert result == []

    def test_returns_empty_when_suppressed(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test returns empty when notifications suppressed."""
        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            with patch(
                "backend.scheduler.reminder_service.get_focus_mode_service"
            ) as mock_focus:
                mock_instance = MagicMock()
                mock_instance.should_suppress_notification.return_value = True
                mock_instance.get_suppression_reason.return_value = "Snoozed"
                mock_focus.return_value = mock_instance

                result = reminder_service.check_and_trigger(95.0, None)
                assert result == []

    def test_triggers_percentage_threshold(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test triggers percentage threshold reminders."""
        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            with patch(
                "backend.scheduler.reminder_service.get_focus_mode_service"
            ) as mock_focus:
                mock_instance = MagicMock()
                mock_instance.should_suppress_notification.return_value = False
                mock_focus.return_value = mock_instance

                with patch(
                    "backend.scheduler.reminder_service.send_notification_sync"
                ):
                    result = reminder_service.check_and_trigger(75.0, None)

                    # Should trigger 50 and 75 thresholds
                    types = [r[0] for r in result]
                    assert ReminderType.PERCENTAGE in types
                    assert 50 in reminder_service._triggered_percentages
                    assert 75 in reminder_service._triggered_percentages

    def test_does_not_retrigger_percentage(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test does not re-trigger same percentage."""
        reminder_service._triggered_percentages.add(50)

        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            with patch(
                "backend.scheduler.reminder_service.get_focus_mode_service"
            ) as mock_focus:
                mock_instance = MagicMock()
                mock_instance.should_suppress_notification.return_value = False
                mock_focus.return_value = mock_instance

                with patch(
                    "backend.scheduler.reminder_service.send_notification_sync"
                ):
                    result = reminder_service.check_and_trigger(55.0, None)

                    # 50 already triggered, should not be in result
                    messages = [r[1] for r in result]
                    assert not any("50%" in m for m in messages)

    def test_triggers_before_reset(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test triggers before-reset reminders."""
        reset_time = datetime.now() + timedelta(minutes=14)

        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            with patch(
                "backend.scheduler.reminder_service.get_focus_mode_service"
            ) as mock_focus:
                mock_instance = MagicMock()
                mock_instance.should_suppress_notification.return_value = False
                mock_focus.return_value = mock_instance

                with patch(
                    "backend.scheduler.reminder_service.send_notification_sync"
                ):
                    result = reminder_service.check_and_trigger(30.0, reset_time)

                    types = [r[0] for r in result]
                    assert ReminderType.BEFORE_RESET in types
                    assert 15 in reminder_service._triggered_before_reset

    def test_callback_is_called(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test callback is invoked on trigger."""
        callback_called = []

        def test_callback(t: ReminderType, m: str) -> None:
            callback_called.append((t, m))

        reminder_service.add_callback(test_callback)

        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            with patch(
                "backend.scheduler.reminder_service.get_focus_mode_service"
            ) as mock_focus:
                mock_instance = MagicMock()
                mock_instance.should_suppress_notification.return_value = False
                mock_focus.return_value = mock_instance

                with patch(
                    "backend.scheduler.reminder_service.send_notification_sync"
                ):
                    reminder_service.check_and_trigger(50.0, None)

                    assert len(callback_called) > 0
                    assert callback_called[0][0] == ReminderType.PERCENTAGE

    def test_callback_error_handled(
        self,
        reminder_service: ReminderService,
        mock_config: MagicMock,
    ):
        """Test callback error is handled gracefully."""

        def bad_callback(t: ReminderType, m: str) -> None:
            raise Exception("Callback error")

        reminder_service.add_callback(bad_callback)

        with patch("backend.scheduler.reminder_service.load_config", return_value=mock_config):
            with patch(
                "backend.scheduler.reminder_service.get_focus_mode_service"
            ) as mock_focus:
                mock_instance = MagicMock()
                mock_instance.should_suppress_notification.return_value = False
                mock_focus.return_value = mock_instance

                with patch(
                    "backend.scheduler.reminder_service.send_notification_sync"
                ):
                    # Should not raise
                    result = reminder_service.check_and_trigger(50.0, None)
                    assert len(result) > 0


class TestSnooze:
    """Tests for snooze method."""

    def test_calls_focus_service(self, reminder_service: ReminderService):
        """Test snooze calls focus service."""
        with patch(
            "backend.scheduler.reminder_service.get_focus_mode_service"
        ) as mock_focus:
            mock_instance = MagicMock()
            mock_focus.return_value = mock_instance

            reminder_service.snooze(15)

            mock_instance.snooze.assert_called_once_with(15)


class TestGetReminderService:
    """Tests for get_reminder_service singleton."""

    def test_returns_same_instance(self):
        """Test returns same singleton instance."""
        import backend.scheduler.reminder_service as module

        module._service = None  # Reset singleton

        service1 = get_reminder_service()
        service2 = get_reminder_service()

        assert service1 is service2

        module._service = None  # Cleanup
