"""Focus mode with DND threshold and quiet hours."""
from datetime import datetime, time, timedelta

from ..core.config_manager import load_config


class FocusModeService:
    """Manage focus mode / do not disturb functionality."""

    def __init__(self) -> None:
        self._snoozed_until: datetime | None = None

    def snooze(self, minutes: int) -> None:
        """Snooze notifications for specified minutes."""
        self._snoozed_until = datetime.now() + timedelta(minutes=minutes)

    def clear_snooze(self) -> None:
        """Clear any active snooze."""
        self._snoozed_until = None

    def is_snoozed(self) -> bool:
        """Check if currently snoozed."""
        if self._snoozed_until is None:
            return False
        return datetime.now() < self._snoozed_until

    def get_snooze_remaining(self) -> int:
        """Get remaining snooze time in seconds, 0 if not snoozed."""
        if self._snoozed_until is None:
            return 0
        remaining = (self._snoozed_until - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def is_in_quiet_hours(self) -> bool:
        """Check if current time is in quiet hours."""
        config = load_config().focus_mode
        if not config.enabled:
            return False
        if not config.quiet_hours_start or not config.quiet_hours_end:
            return False

        now = datetime.now().time()
        start = time.fromisoformat(config.quiet_hours_start)
        end = time.fromisoformat(config.quiet_hours_end)

        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start > end:
            return now >= start or now <= end
        return start <= now <= end

    def is_dnd_by_usage(self, current_usage: float) -> bool:
        """Check if DND should be active based on usage threshold."""
        config = load_config().focus_mode
        if not config.enabled:
            return False
        return current_usage > config.dnd_threshold

    def should_suppress_notification(self, current_usage: float) -> bool:
        """Check if notification should be suppressed.

        Returns True if any of these conditions are met:
        - Snoozed
        - In quiet hours
        - Usage exceeds DND threshold
        """
        if self.is_snoozed():
            return True
        if self.is_in_quiet_hours():
            return True
        return bool(self.is_dnd_by_usage(current_usage))

    def get_suppression_reason(self, current_usage: float) -> str | None:
        """Get reason for notification suppression, or None if not suppressed."""
        if self.is_snoozed():
            remaining = self.get_snooze_remaining()
            mins = remaining // 60
            return f"Snoozed for {mins} more minutes"
        if self.is_in_quiet_hours():
            config = load_config().focus_mode
            return f"Quiet hours ({config.quiet_hours_start} - {config.quiet_hours_end})"
        if self.is_dnd_by_usage(current_usage):
            config = load_config().focus_mode
            return f"DND active (usage > {config.dnd_threshold}%)"
        return None


# Singleton instance
_service: FocusModeService | None = None


def get_focus_mode_service() -> FocusModeService:
    """Get singleton focus mode service instance."""
    global _service
    if _service is None:
        _service = FocusModeService()
    return _service
