"""Reminder service for usage thresholds and reset times."""
from collections.abc import Callable
from datetime import datetime
from enum import Enum

from loguru import logger

from ..core.config_manager import load_config
from .focus_mode import get_focus_mode_service
from .notifier import send_notification_sync


class ReminderType(Enum):
    """Types of reminders."""
    BEFORE_RESET = "before_reset"
    ON_RESET = "on_reset"
    PERCENTAGE = "percentage"


class ReminderService:
    """Manage and trigger usage reminders."""

    def __init__(self) -> None:
        self._triggered_before_reset: set[int] = set()  # Minutes already triggered
        self._triggered_percentages: set[int] = set()
        self._reset_triggered = False
        self._last_reset_time: datetime | None = None
        self._callbacks: list[Callable[[ReminderType, str], None]] = []

    def add_callback(self, callback: Callable[[ReminderType, str], None]) -> None:
        """Add callback for when reminder triggers."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[ReminderType, str], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self, reminder_type: ReminderType, message: str) -> None:
        """Notify all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(reminder_type, message)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def reset_triggers(self) -> None:
        """Reset all triggers (call after token reset)."""
        self._triggered_before_reset.clear()
        self._triggered_percentages.clear()
        self._reset_triggered = False
        logger.debug("Reminder triggers reset")

    def check_and_trigger(
        self,
        current_usage: float,
        reset_time: datetime | None,
    ) -> list[tuple[ReminderType, str]]:
        """Check conditions and trigger appropriate reminders.

        Args:
            current_usage: Current usage percentage (0-100)
            reset_time: When the usage will reset

        Returns:
            List of (ReminderType, message) for triggered reminders
        """
        config = load_config().reminder
        if not config.enabled:
            return []

        focus_service = get_focus_mode_service()
        if focus_service.should_suppress_notification(current_usage):
            reason = focus_service.get_suppression_reason(current_usage)
            logger.debug(f"Notifications suppressed: {reason}")
            return []

        triggered: list[tuple[ReminderType, str]] = []

        # Check percentage thresholds
        for threshold in config.percentage_thresholds:
            if threshold not in self._triggered_percentages and current_usage >= threshold:
                self._triggered_percentages.add(threshold)
                message = f"Usage reached {threshold}%"
                triggered.append((ReminderType.PERCENTAGE, message))
                send_notification_sync("Claudiminder", message)
                self._notify_callbacks(ReminderType.PERCENTAGE, message)
                logger.info(f"Triggered percentage reminder: {threshold}%")

        # Check before-reset reminders
        if reset_time:
            now = datetime.now()
            time_until_reset = reset_time - now
            minutes_until = time_until_reset.total_seconds() / 60

            for minutes in config.before_reset_minutes:
                if minutes not in self._triggered_before_reset and 0 < minutes_until <= minutes:
                    self._triggered_before_reset.add(minutes)
                    message = f"Token reset in {int(minutes_until)} minutes!"
                    triggered.append((ReminderType.BEFORE_RESET, message))
                    send_notification_sync("Claudiminder", message)
                    self._notify_callbacks(ReminderType.BEFORE_RESET, message)
                    logger.info(f"Triggered before-reset reminder: {minutes}m")

            # Check on-reset
            if config.on_reset and not self._reset_triggered and self._last_reset_time and reset_time > self._last_reset_time:
                self._reset_triggered = True
                message = "Your token has reset!"
                triggered.append((ReminderType.ON_RESET, message))
                send_notification_sync("Claudiminder", message)
                self._notify_callbacks(ReminderType.ON_RESET, message)
                logger.info("Triggered on-reset reminder")

            self._last_reset_time = reset_time

        return triggered

    def snooze(self, minutes: int) -> None:
        """Snooze all reminders for specified minutes."""
        focus_service = get_focus_mode_service()
        focus_service.snooze(minutes)
        logger.info(f"Reminders snoozed for {minutes} minutes")


# Singleton instance
_service: ReminderService | None = None


def get_reminder_service() -> ReminderService:
    """Get singleton reminder service instance."""
    global _service
    if _service is None:
        _service = ReminderService()
    return _service
