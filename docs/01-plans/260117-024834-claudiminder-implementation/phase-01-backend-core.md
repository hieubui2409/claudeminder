---
title: "Phase 1: Backend Core"
status: pending
priority: P1
effort: 6h
updated: 2026-01-17
---

# Phase 1: Backend Core

## Context Links

- [Python TUI Research](../reports/researcher-260117-024702-python-tui-libraries.md)
- [Requirements Summary](./requirements-summary.md)
- [Python Rules](../../02-general/rules/01-python.md)
- Existing: `src/backend/api/usage.py`, `src/backend/models/`

## Overview

Implement Textual-based TUI (simple ANSI), reminder system with all presets, focus mode, usage goals, and i18n (En + Vi).

## Key Insights (from interview)

- **TUI style**: Simple terminal ANSI colors (not full themes like GUI)
- **Polling**: Hybrid (60s auto + manual refresh)
- **Reminders**: All presets (before reset, on reset, percentage thresholds)
- **Custom action**: Shell command OR URL
- **Notification**: System native + in-app toast + TUI bell
- **Snooze**: 5/15/30 min options
- **Focus mode**: DND when >80% + scheduled quiet hours
- **Goals**: Daily budget + pace indicator
- **i18n**: English + Vietnamese
- **Config**: TOML at ~/.config/claudeminder/
- **Logging**: User configurable level, stdout + file

## Requirements

### Functional

- Real-time usage % display (all metrics: 5h, 7d, extra usage)
- Countdown: HH:MM:SS + human readable toggle
- Keyboard shortcuts: q=quit, r=refresh, h=help
- Reminders: before reset (15/30/60m), on reset, percentage (50/75/90/100%)
- Custom actions: execute shell command OR open URL
- Snooze: 5/15/30 min dismiss options
- Focus mode: auto DND when usage >80%, scheduled quiet hours
- Goals: daily budget setting, pace indicator (on track/too fast)
- i18n: English + Vietnamese
- Single instance enforcement
- Offline mode: cached data + warning
- JSON sidecar output for Tauri

### Non-Functional

- <100ms UI response time
- Poll API every 60s (not every frame)
- Retry → toast → degraded mode on errors
- User configurable log level
- Logs to stdout + ~/.config/claudeminder/logs/

## Architecture

```
src/backend/
├── tui/
│   ├── __init__.py
│   ├── app.py                    # Main Textual App
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── usage-display.py      # All metrics widget
│   │   ├── reset-countdown.py    # Timer (both formats)
│   │   ├── goals-indicator.py    # Budget + pace
│   │   └── offline-banner.py     # Offline mode UI
│   └── styles.tcss
├── scheduler/
│   ├── __init__.py
│   ├── reminder-service.py       # All reminder logic
│   ├── focus-mode.py             # DND + quiet hours
│   └── notifier.py               # Multi-channel notify
├── i18n/
│   ├── __init__.py
│   ├── en.py                     # English strings
│   └── vi.py                     # Vietnamese strings
├── core/
│   ├── __init__.py
│   ├── instance-lock.py          # Single instance
│   ├── goals-tracker.py          # Budget + pace calc
│   └── config-manager.py         # TOML config R/W
└── sidecar.py                    # JSON output for Tauri
```

## Related Code Files

### Create

- `src/backend/tui/__init__.py`
- `src/backend/tui/app.py`
- `src/backend/tui/widgets/__init__.py`
- `src/backend/tui/widgets/usage-display.py`
- `src/backend/tui/widgets/reset-countdown.py`
- `src/backend/tui/widgets/goals-indicator.py`
- `src/backend/tui/widgets/offline-banner.py`
- `src/backend/tui/styles.tcss`
- `src/backend/scheduler/__init__.py`
- `src/backend/scheduler/reminder-service.py`
- `src/backend/scheduler/focus-mode.py`
- `src/backend/scheduler/notifier.py`
- `src/backend/i18n/__init__.py`
- `src/backend/i18n/en.py`
- `src/backend/i18n/vi.py`
- `src/backend/core/__init__.py`
- `src/backend/core/instance-lock.py`
- `src/backend/core/goals-tracker.py`
- `src/backend/core/config-manager.py`
- `src/backend/sidecar.py`

### Modify

- `src/backend/cli.py` - Add `tui` command
- `src/backend/models/settings.py` - Add focus mode, goals, i18n settings
- `pyproject.toml` - Add dependencies

## Implementation Steps

### Step 1: Add Dependencies

```bash
uv add desktop-notifier tomli tomli-w filelock babel
```

### Step 2: Config Manager (TOML)

```python
# src/backend/core/config-manager.py
from pathlib import Path
import tomli
import tomli_w
from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".config" / "claudeminder"
CONFIG_FILE = CONFIG_DIR / "config.toml"

class ReminderConfig(BaseModel):
    enabled: bool = True
    before_reset_minutes: list[int] = [15, 30, 60]
    on_reset: bool = True
    percentage_thresholds: list[int] = [50, 75, 90, 100]
    snooze_minutes: list[int] = [5, 15, 30]
    custom_command: str | None = None
    custom_url: str | None = None

class FocusModeConfig(BaseModel):
    enabled: bool = False
    dnd_threshold: int = 80  # Auto DND when usage > 80%
    quiet_hours_start: str | None = None  # "22:00"
    quiet_hours_end: str | None = None    # "08:00"

class GoalsConfig(BaseModel):
    enabled: bool = False
    daily_budget_percent: int = 100
    warn_when_pace_exceeded: bool = True

class AppConfig(BaseModel):
    language: str = "en"  # en | vi
    log_level: str = "INFO"
    poll_interval_seconds: int = 60
    reminder: ReminderConfig = ReminderConfig()
    focus_mode: FocusModeConfig = FocusModeConfig()
    goals: GoalsConfig = GoalsConfig()

def load_config() -> AppConfig:
    if not CONFIG_FILE.exists():
        return AppConfig()
    with open(CONFIG_FILE, "rb") as f:
        data = tomli.load(f)
    return AppConfig.model_validate(data)

def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config.model_dump(), f)
```

### Step 3: Single Instance Lock

```python
# src/backend/core/instance-lock.py
from pathlib import Path
from filelock import FileLock, Timeout

LOCK_FILE = Path.home() / ".config" / "claudeminder" / ".lock"

def acquire_instance_lock() -> FileLock | None:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(LOCK_FILE), timeout=0)
    try:
        lock.acquire()
        return lock
    except Timeout:
        return None

def is_another_instance_running() -> bool:
    return acquire_instance_lock() is None
```

### Step 4: i18n Strings

```python
# src/backend/i18n/en.py
STRINGS = {
    "usage_title": "Claude Usage",
    "reset_in": "Reset in",
    "reset_complete": "Reset complete!",
    "offline_mode": "Offline - showing cached data",
    "reminder_soon": "Token reset in {minutes} minutes!",
    "reminder_reset": "Your token has reset!",
    "reminder_threshold": "Usage reached {percent}%",
    "pace_ok": "On track",
    "pace_exceeded": "Using too fast!",
    "budget_used": "Budget: {used}% of {total}%",
}

# src/backend/i18n/vi.py
STRINGS = {
    "usage_title": "Sử dụng Claude",
    "reset_in": "Reset sau",
    "reset_complete": "Đã reset xong!",
    "offline_mode": "Ngoại tuyến - hiển thị dữ liệu đã lưu",
    "reminder_soon": "Token sẽ reset trong {minutes} phút!",
    "reminder_reset": "Token của bạn đã reset!",
    "reminder_threshold": "Đã sử dụng {percent}%",
    "pace_ok": "Đúng tiến độ",
    "pace_exceeded": "Đang dùng quá nhanh!",
    "budget_used": "Ngân sách: {used}% / {total}%",
}
```

### Step 5: Focus Mode Service

```python
# src/backend/scheduler/focus-mode.py
from datetime import datetime, time
from ..core.config-manager import load_config

class FocusModeService:
    def __init__(self) -> None:
        self._snoozed_until: datetime | None = None

    def should_suppress_notification(self, current_usage: float) -> bool:
        config = load_config().focus_mode
        if not config.enabled:
            return False

        # Check snooze
        if self._snoozed_until and datetime.now() < self._snoozed_until:
            return True

        # Check DND threshold
        if current_usage > config.dnd_threshold:
            return True

        # Check quiet hours
        if config.quiet_hours_start and config.quiet_hours_end:
            now = datetime.now().time()
            start = time.fromisoformat(config.quiet_hours_start)
            end = time.fromisoformat(config.quiet_hours_end)
            if start <= now or now <= end:  # Handle overnight
                return True

        return False

    def snooze(self, minutes: int) -> None:
        from datetime import timedelta
        self._snoozed_until = datetime.now() + timedelta(minutes=minutes)
```

### Step 6: Goals Tracker

```python
# src/backend/core/goals-tracker.py
from datetime import datetime
from ..core.config-manager import load_config

class GoalsTracker:
    def __init__(self) -> None:
        self._session_start = datetime.now()

    def calculate_pace(self, current_usage: float) -> tuple[bool, str]:
        """Returns (is_on_track, message)."""
        config = load_config().goals
        if not config.enabled:
            return True, ""

        # Calculate expected usage at this time of day
        hours_elapsed = (datetime.now() - self._session_start.replace(
            hour=0, minute=0, second=0
        )).total_seconds() / 3600
        expected_usage = (hours_elapsed / 24) * config.daily_budget_percent

        is_on_track = current_usage <= expected_usage * 1.1  # 10% buffer
        return is_on_track, f"{current_usage:.1f}% / {expected_usage:.1f}% expected"
```

### Step 7: Multi-channel Notifier

```python
# src/backend/scheduler/notifier.py
import subprocess
import webbrowser
from desktop_notifier import DesktopNotifier
from ..core.config-manager import load_config

_notifier: DesktopNotifier | None = None

def _get_notifier() -> DesktopNotifier:
    global _notifier
    if _notifier is None:
        _notifier = DesktopNotifier(app_name="claudeminder")
    return _notifier

async def send_notification(title: str, body: str) -> None:
    config = load_config()

    # System notification
    try:
        notifier = _get_notifier()
        await notifier.send(title=title, message=body)
    except Exception:
        # Fallback to terminal bell
        print("\a", end="", flush=True)

    # Execute custom action if configured
    if config.reminder.custom_command:
        try:
            subprocess.Popen(config.reminder.custom_command, shell=True)
        except Exception:
            pass

    if config.reminder.custom_url:
        try:
            webbrowser.open(config.reminder.custom_url)
        except Exception:
            pass
```

### Step 8: TUI App with All Features

```python
# src/backend/tui/app.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from ..core.instance-lock import is_another_instance_running
from ..i18n import get_string
from .widgets.usage_display import UsageDisplay
from .widgets.reset_countdown import ResetCountdown
from .widgets.goals_indicator import GoalsIndicator
from .widgets.offline_banner import OfflineBanner

class ClaudiminderApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("h", "help", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__()
        if is_another_instance_running():
            raise RuntimeError("Another instance is already running")

    def compose(self) -> ComposeResult:
        yield Header()
        yield OfflineBanner()
        yield UsageDisplay()
        yield ResetCountdown()
        yield GoalsIndicator()
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(UsageDisplay).refresh_usage()
```

## Todo List

- [ ] Add dependencies (desktop-notifier, tomli, tomli-w, filelock, babel)
- [ ] Create config manager with TOML R/W
- [ ] Create single instance lock
- [ ] Create i18n module (en + vi)
- [ ] Create focus mode service (DND + quiet hours)
- [ ] Create goals tracker (budget + pace)
- [ ] Create multi-channel notifier (system + command + URL + bell)
- [ ] Create TUI widgets (usage, countdown, goals, offline)
- [ ] Create reminder service with all presets
- [ ] Create sidecar.py for Tauri
- [ ] Update CLI with tui command
- [ ] Test manually: `uv run claudeminder tui`

## Success Criteria

- Single instance enforcement works
- All metrics displayed (5h, 7d, extra usage)
- Countdown shows both formats
- All reminder presets trigger correctly
- Custom command/URL executes
- Snooze works (5/15/30 min)
- Focus mode suppresses notifications
- Goals tracker shows pace
- i18n switches between En/Vi
- Offline mode shows cached data
- `python -m src.backend.sidecar get_usage` outputs JSON

## Risk Assessment

| Risk                   | Mitigation                       |
| ---------------------- | -------------------------------- |
| desktop-notifier fails | Fallback to terminal bell        |
| Nuitka compile issues  | Document C compiler requirements |
| filelock on Windows    | Test cross-platform              |

## Security Considerations

- No credentials stored in TUI code
- Use existing `get_access_token()` from credentials module
- Log errors without exposing tokens
- Custom command execution is user-configured (trusted)
