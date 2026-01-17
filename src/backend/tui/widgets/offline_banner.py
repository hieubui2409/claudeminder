"""Offline mode banner widget."""
from typing import Any

from textual.reactive import reactive
from textual.widgets import Static

from ...i18n import get_string


class OfflineBanner(Static):
    """Display banner when offline."""

    is_offline: reactive[bool] = reactive(False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.update("")

    def watch_is_offline(self, value: bool) -> None:
        if value:
            self.update(f"[bold yellow on red] ⚠ {get_string('offline_mode')} [/]")
            self.display = True
        else:
            self.update("")
            self.display = False

    def set_offline(self, offline: bool) -> None:
        """Set offline status."""
        self.is_offline = offline

    def show_connection_restored(self) -> None:
        """Briefly show connection restored message."""
        self.update(f"[bold green] ✓ {get_string('connection_restored')} [/]")
        self.display = True
