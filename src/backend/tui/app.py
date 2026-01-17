"""Main TUI application using Textual."""
from datetime import datetime
from typing import TYPE_CHECKING

from filelock import SoftFileLock
from loguru import logger
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.timer import Timer
from textual.widgets import Footer, Header

from ..api.usage import UsageAPI
from ..core.config_manager import load_config
from ..core.goals_tracker import get_goals_tracker
from ..core.instance_lock import acquire_instance_lock, release_instance_lock
from ..i18n import get_string, set_language
from ..models.usage import UsageResponse
from ..scheduler import get_reminder_service
from .widgets import GoalsIndicator, OfflineBanner, ResetCountdown, UsageDisplay

if TYPE_CHECKING:
    pass


class ClaudiminderApp(App[None]):
    """Claudiminder TUI Application."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("h", "help", "Help"),
        Binding("t", "toggle_format", "Toggle time format"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._lock: SoftFileLock | None = None
        self._usage_api: UsageAPI | None = None
        self._poll_timer: Timer | None = None
        self._last_error: str | None = None

        # Load config and set language
        config = load_config()
        set_language(config.language)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield OfflineBanner(id="offline-banner")
        yield Container(
            Vertical(
                UsageDisplay(id="usage-display"),
                ResetCountdown(id="reset-countdown"),
                GoalsIndicator(id="goals-indicator"),
                id="main-content",
            ),
            id="app-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Check single instance
        self._lock = acquire_instance_lock()
        if self._lock is None:
            self.notify(
                "Another instance is already running",
                severity="error",
                timeout=3,
            )
            self.exit()
            return

        # Initialize API
        try:
            self._usage_api = UsageAPI()
        except Exception as e:
            logger.error(f"Failed to initialize API: {e}")
            self._show_offline()

        # Initial fetch
        await self._fetch_usage()

        # Start polling
        config = load_config()
        self._poll_timer = self.set_interval(
            config.poll_interval_seconds,
            self._fetch_usage,
        )

        logger.info("Claudiminder TUI started")

    async def on_unmount(self) -> None:
        """Called when app is unmounting."""
        if self._poll_timer:
            self._poll_timer.stop()
        release_instance_lock()
        logger.info("Claudiminder TUI stopped")

    async def _fetch_usage(self) -> None:
        """Fetch usage data from API."""
        if self._usage_api is None:
            return

        try:
            usage_data = await self._usage_api.get_usage()
            self._update_widgets(usage_data)
            self._hide_offline()
            self._last_error = None

            # Check reminders
            reminder_service = get_reminder_service()
            reset_time = None
            if usage_data.five_hour and usage_data.five_hour.resets_at:
                reset_time = datetime.fromisoformat(
                    usage_data.five_hour.resets_at.replace("Z", "+00:00")
                )

            reminder_service.check_and_trigger(
                current_usage=usage_data.five_hour.utilization if usage_data.five_hour else 0,
                reset_time=reset_time,
            )

        except Exception as e:
            error_msg = str(e)
            if error_msg != self._last_error:
                logger.error(f"Failed to fetch usage: {e}")
                self.notify(f"Error: {error_msg}", severity="error", timeout=5)
                self._last_error = error_msg
            self._show_offline()

    def _update_widgets(self, usage_data: UsageResponse) -> None:
        """Update all widgets with new data."""
        usage_display = self.query_one("#usage-display", UsageDisplay)
        reset_countdown = self.query_one("#reset-countdown", ResetCountdown)
        goals_indicator = self.query_one("#goals-indicator", GoalsIndicator)

        if usage_data.five_hour:
            five_hour = usage_data.five_hour.utilization

            # Get optional data
            seven_day = None
            extra = None
            if hasattr(usage_data, 'seven_day') and usage_data.seven_day:
                seven_day = getattr(usage_data.seven_day, 'utilization', None)
            if hasattr(usage_data, 'extra_usage') and usage_data.extra_usage:
                extra = getattr(usage_data.extra_usage, 'utilization', None)

            usage_display.update_usage(
                five_hour=five_hour,
                seven_day=seven_day,
                extra=extra,
            )

            # Update reset countdown
            if usage_data.five_hour.resets_at:
                reset_time = datetime.fromisoformat(
                    usage_data.five_hour.resets_at.replace("Z", "+00:00")
                )
                reset_countdown.set_reset_time(reset_time)

            # Update goals
            goals_indicator.update_usage(five_hour)
            goals_tracker = get_goals_tracker()
            if usage_data.five_hour.resets_at:
                reset_time = datetime.fromisoformat(
                    usage_data.five_hour.resets_at.replace("Z", "+00:00")
                )
                goals_tracker.set_reset_time(reset_time)

    def _show_offline(self) -> None:
        """Show offline banner."""
        banner = self.query_one("#offline-banner", OfflineBanner)
        banner.set_offline(True)

    def _hide_offline(self) -> None:
        """Hide offline banner."""
        banner = self.query_one("#offline-banner", OfflineBanner)
        if banner.is_offline:
            banner.show_connection_restored()
            self.set_timer(2.0, lambda: banner.set_offline(False))

    async def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    async def action_refresh(self) -> None:
        """Manually refresh usage data."""
        self.notify(get_string("refreshing"), timeout=1)
        await self._fetch_usage()

    def action_help(self) -> None:
        """Show help."""
        help_text = (
            f"{get_string('press_q_quit')}\n"
            f"{get_string('press_r_refresh')}\n"
            f"{get_string('press_h_help')}\n"
            "t - Toggle time format"
        )
        self.notify(help_text, timeout=5)

    def action_toggle_format(self) -> None:
        """Toggle countdown format."""
        countdown = self.query_one("#reset-countdown", ResetCountdown)
        countdown.toggle_format()


def run_tui() -> None:
    """Run the TUI application."""
    app = ClaudiminderApp()
    app.run()
