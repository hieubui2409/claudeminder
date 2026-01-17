"""Daily usage goals and pace tracking."""
from datetime import datetime
from typing import NamedTuple

from .config_manager import load_config


class PaceStatus(NamedTuple):
    """Pace calculation result."""
    is_on_track: bool
    current_usage: float
    expected_usage: float
    message: str


class GoalsTracker:
    """Track daily usage goals and pace."""

    def __init__(self) -> None:
        self._session_start = datetime.now()
        self._last_reset_time: datetime | None = None

    def set_reset_time(self, reset_time: datetime) -> None:
        """Set the next reset time for accurate pace calculation."""
        self._last_reset_time = reset_time

    def calculate_pace(self, current_usage: float) -> PaceStatus:
        """Calculate if usage is on track for daily budget.

        Args:
            current_usage: Current usage percentage (0-100)

        Returns:
            PaceStatus with is_on_track, current/expected usage, and message
        """
        config = load_config().goals

        if not config.enabled:
            return PaceStatus(
                is_on_track=True,
                current_usage=current_usage,
                expected_usage=0,
                message=""
            )

        # Calculate hours elapsed today
        now = datetime.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hours_elapsed = (now - day_start).total_seconds() / 3600

        # Calculate expected usage at this time
        # Assumes even distribution across 24 hours
        expected_usage = (hours_elapsed / 24) * config.daily_budget_percent

        # 10% buffer for "on track"
        is_on_track = current_usage <= expected_usage * 1.1

        if is_on_track:
            message = f"On track: {current_usage:.1f}% / {expected_usage:.1f}% expected"
        else:
            overage = current_usage - expected_usage
            message = f"Pace exceeded by {overage:.1f}%"

        return PaceStatus(
            is_on_track=is_on_track,
            current_usage=current_usage,
            expected_usage=expected_usage,
            message=message
        )

    def get_budget_status(self, current_usage: float) -> tuple[float, float, bool]:
        """Get budget status: (used%, budget%, exceeded).

        Returns:
            Tuple of (current_usage, daily_budget, is_exceeded)
        """
        config = load_config().goals
        budget = config.daily_budget_percent if config.enabled else 100
        exceeded = current_usage > budget
        return current_usage, budget, exceeded

    def should_warn(self, current_usage: float) -> bool:
        """Check if pace warning should be shown."""
        config = load_config().goals
        if not config.enabled or not config.warn_when_pace_exceeded:
            return False

        pace = self.calculate_pace(current_usage)
        return not pace.is_on_track


# Singleton instance
_tracker: GoalsTracker | None = None


def get_goals_tracker() -> GoalsTracker:
    """Get singleton goals tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = GoalsTracker()
    return _tracker
