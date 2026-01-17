"""Usage display widget showing all metrics."""
from typing import Any

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from ...i18n import get_string


class UsageDisplay(Static):
    """Display usage metrics: 5h, 7d, extra usage."""

    five_hour_usage: reactive[float] = reactive(0.0)
    seven_day_usage: reactive[float | None] = reactive(None)
    extra_usage: reactive[float | None] = reactive(None)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.border_title = get_string("usage_title")

    def compose(self) -> ComposeResult:
        yield Static(id="usage-content")

    def watch_five_hour_usage(self, _value: float) -> None:
        self._update_display()

    def watch_seven_day_usage(self, _value: float | None) -> None:
        self._update_display()

    def watch_extra_usage(self, _value: float | None) -> None:
        self._update_display()

    def on_mount(self) -> None:
        self._update_display()

    def _update_display(self) -> None:
        """Update the display content."""
        try:
            content = self.query_one("#usage-content", Static)
        except Exception:
            return

        lines = []

        # 5-hour usage (main metric)
        five_h = get_string("five_hour_usage")
        lines.append(f"[bold cyan]{five_h}:[/] {self.five_hour_usage:.1f}%")
        lines.append(self._progress_bar(self.five_hour_usage))

        # 7-day usage
        if self.seven_day_usage is not None:
            seven_d = get_string("seven_day_usage")
            lines.append(f"\n[cyan]{seven_d}:[/] {self.seven_day_usage:.1f}%")
            lines.append(self._progress_bar(self.seven_day_usage))

        # Extra usage
        if self.extra_usage is not None and self.extra_usage > 0:
            extra = get_string("extra_usage")
            lines.append(f"\n[yellow]{extra}:[/] {self.extra_usage:.1f}%")

        content.update("\n".join(lines))

    def _progress_bar(self, percent: float, width: int = 30) -> str:
        """Create ASCII progress bar."""
        filled = int(width * min(percent, 100) / 100)
        empty = width - filled

        # Color based on percentage
        if percent >= 90:
            color = "red"
        elif percent >= 75:
            color = "yellow"
        else:
            color = "green"

        bar = f"[{color}]{'█' * filled}{'░' * empty}[/]"
        return bar

    def update_usage(
        self,
        five_hour: float,
        seven_day: float | None = None,
        extra: float | None = None,
    ) -> None:
        """Update all usage values."""
        self.five_hour_usage = five_hour
        self.seven_day_usage = seven_day
        self.extra_usage = extra
