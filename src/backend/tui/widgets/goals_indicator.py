"""Goals and pace indicator widget."""
from typing import Any

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from ...core.goals_tracker import get_goals_tracker
from ...i18n import get_string


class GoalsIndicator(Static):
    """Display daily goals and pace status."""

    current_usage: reactive[float] = reactive(0.0)
    is_visible: reactive[bool] = reactive(False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.border_title = get_string("daily_goal")

    def compose(self) -> ComposeResult:
        yield Static(id="goals-content")

    def on_mount(self) -> None:
        self._update_display()

    def watch_current_usage(self, _value: float) -> None:
        self._update_display()

    def watch_is_visible(self, value: bool) -> None:
        self.display = value

    def _update_display(self) -> None:
        """Update the goals display."""
        try:
            content = self.query_one("#goals-content", Static)
        except Exception:
            return

        tracker = get_goals_tracker()

        pace = tracker.calculate_pace(self.current_usage)
        used, budget, exceeded = tracker.get_budget_status(self.current_usage)

        if not pace.message:
            # Goals not enabled
            self.is_visible = False
            return

        self.is_visible = True

        lines = []

        # Budget status
        budget_str = get_string("budget_used", used=f"{used:.1f}", total=str(int(budget)))
        if exceeded:
            lines.append(f"[bold red]{budget_str}[/]")
        else:
            lines.append(f"[cyan]{budget_str}[/]")

        # Pace status
        if pace.is_on_track:
            pace_str = get_string("pace_ok")
            lines.append(f"[green]✓ {pace_str}[/]")
        else:
            pace_str = get_string("pace_exceeded")
            lines.append(f"[yellow bold]⚠ {pace_str}[/]")

        # Expected vs actual
        lines.append(f"[dim]{pace.message}[/]")

        content.update("\n".join(lines))

    def update_usage(self, usage: float) -> None:
        """Update current usage for pace calculation."""
        self.current_usage = usage
