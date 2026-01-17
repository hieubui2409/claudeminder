"""Reset countdown timer widget."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Static

from ...i18n import get_string


class ResetCountdown(Static):
    """Display countdown to next reset."""

    reset_time: reactive[datetime | None] = reactive(None)
    show_human_readable: reactive[bool] = reactive(True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.border_title = get_string("reset_in")
        self._timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Static(get_string("loading"), id="countdown-text")

    def on_mount(self) -> None:
        """Start the countdown timer."""
        self._timer = self.set_interval(1.0, self._update_countdown)

    def watch_reset_time(self, _value: datetime | None) -> None:
        self._update_countdown()

    def on_unmount(self) -> None:
        """Stop the countdown timer."""
        if self._timer:
            self._timer.stop()

    def _update_countdown(self) -> None:
        """Update countdown display."""
        try:
            content = self.query_one("#countdown-text", Static)
        except Exception:
            return

        if self.reset_time is None:
            content.update(get_string("loading"))
            return

        now = datetime.now()
        if now >= self.reset_time:
            content.update(f"[bold green]{get_string('reset_complete')}[/]")
            return

        delta = self.reset_time - now
        total_seconds = int(delta.total_seconds())

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if self.show_human_readable:
            parts = []
            if hours > 0:
                parts.append(f"{hours} {get_string('hours')}")
            if minutes > 0:
                parts.append(f"{minutes} {get_string('minutes')}")
            parts.append(f"{seconds} {get_string('seconds')}")
            time_str = ", ".join(parts)
        else:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Color based on time remaining
        if total_seconds < 300:  # < 5 min
            color = "red bold"
        elif total_seconds < 900:  # < 15 min
            color = "yellow"
        else:
            color = "cyan"

        content.update(f"[{color}]{time_str}[/]")

    def toggle_format(self) -> None:
        """Toggle between HH:MM:SS and human readable."""
        self.show_human_readable = not self.show_human_readable

    def set_reset_time(self, reset_time: datetime | None) -> None:
        """Set the reset time."""
        self.reset_time = reset_time
