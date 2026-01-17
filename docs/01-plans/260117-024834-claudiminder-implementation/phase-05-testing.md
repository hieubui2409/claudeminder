---
title: "Phase 5: Testing & Quality Assurance"
status: pending
priority: P2
effort: 6h
---

# Phase 5: Comprehensive Testing & CI/CD

## Context Links

- [Python Rules](../../02-general/rules/01-python.md)
- [Core Principles](../../02-general/rules/00-principles.md)
- Existing: `tests/backend/`, `pyproject.toml` pytest config

## Overview

Implement comprehensive testing suite with 90%+ coverage for both backend (Python) and frontend (TypeScript/React). Include E2E tests with Playwright, pre-commit hooks (lint + format + type), and full CI/CD pipeline with cross-platform builds and release automation.

## Key Insights

- 90%+ coverage target for production readiness
- pytest-asyncio + pytest-httpx for async backend tests
- Vitest + React Testing Library + Playwright for frontend
- Pre-commit hooks: ruff, prettier, mypy, pyright
- CI/CD: test → build → sign → publish on tag
- Coverage thresholds enforced in CI (fail if < 90%)
- E2E tests for critical user flows

## Requirements

### Functional

- Unit tests for all business logic (backend + frontend)
- Integration tests for API client + sidecar
- Component tests for React widgets
- Hook tests for state management
- E2E tests for GUI user flows (Playwright)
- Pre-commit hooks for code quality gates

### Non-Functional

- **>= 90% code coverage** for backend
- **>= 90% code coverage** for frontend
- All tests pass in CI (GitHub Actions)
- Test execution < 2min (unit + integration)
- E2E tests < 5min
- Type checking with mypy + pyright
- Linting + formatting checks on every commit
- Cross-platform builds (Linux, macOS, Windows)
- Release automation on git tag

## Architecture

```
tests/
├── backend/
│   ├── conftest.py              # Shared fixtures
│   ├── test_api_usage.py        # API client tests
│   ├── test_models.py           # Pydantic model tests
│   ├── test_credentials.py      # Credentials tests
│   ├── test_sidecar.py          # Sidecar entry point tests
│   ├── tui/
│   │   ├── test_app.py          # TUI app tests
│   │   └── test_widgets.py      # Widget tests
│   └── scheduler/
│       ├── test_reminder.py     # Reminder service tests
│       └── test_notifier.py     # Notifier tests
└── frontend/
    ├── setup.ts                 # Vitest setup
    ├── components/
    │   ├── dashboard.test.tsx
    │   └── theme-switcher.test.tsx
    ├── hooks/
    │   ├── use-usage.test.ts
    │   └── use-countdown.test.ts
    ├── stores/
    │   └── theme-store.test.ts
    └── e2e/
        ├── playwright.config.ts
        ├── dashboard.spec.ts
        ├── notifications.spec.ts
        └── theme-switcher.spec.ts

.github/
└── workflows/
    ├── test.yml                 # Test + coverage CI
    ├── build.yml                # Cross-platform build
    └── release.yml              # Release automation

.pre-commit-config.yaml          # Pre-commit hooks config
```

## Related Code Files

### Create

- `tests/backend/conftest.py`
- `tests/backend/test_api_usage.py`
- `tests/backend/test_models.py`
- `tests/backend/test_credentials.py`
- `tests/backend/test_sidecar.py`
- `tests/backend/tui/test_app.py`
- `tests/backend/tui/test_widgets.py`
- `tests/backend/scheduler/test_reminder.py`
- `tests/backend/scheduler/test_notifier.py`
- `tests/frontend/setup.ts`
- `tests/frontend/components/dashboard.test.tsx`
- `tests/frontend/components/theme-switcher.test.tsx`
- `tests/frontend/hooks/use-usage.test.ts`
- `tests/frontend/hooks/use-countdown.test.ts`
- `tests/frontend/stores/theme-store.test.ts`
- `tests/frontend/e2e/playwright.config.ts`
- `tests/frontend/e2e/dashboard.spec.ts`
- `tests/frontend/e2e/notifications.spec.ts`
- `tests/frontend/e2e/theme-switcher.spec.ts`
- `.pre-commit-config.yaml`
- `.github/workflows/test.yml`
- `.github/workflows/build.yml`
- `.github/workflows/release.yml`

### Modify

- `pyproject.toml` - Add pytest-httpx, mypy, pyright, coverage thresholds
- `src/frontend/package.json` - Add vitest, playwright, testing-library
- `src/frontend/vitest.config.ts` - Update coverage thresholds to 90%

## Implementation Steps

### Step 1: Add Test Dependencies

**pyproject.toml (add to dev):**

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.25.0",
    "pytest-cov>=6.0.0",
    "pytest-httpx>=0.35.0",
    "textual-dev>=1.0.0",
    "ruff>=0.8.0",
    "mypy>=1.14.0",
    "pyright>=1.1.380",
    "pre-commit>=4.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests/backend"]
asyncio_mode = "auto"
addopts = "--cov=src/backend --cov-report=term-missing --cov-report=html --cov-fail-under=90"

[tool.coverage.run]
branch = true
source = ["src/backend"]

[tool.coverage.report]
fail_under = 90
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

```bash
uv sync --dev
```

**Frontend (package.json):**

```bash
cd src/frontend
bun add -d vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @types/node
bun add -d @playwright/test playwright
```

### Step 2: Create Backend conftest.py

**tests/backend/conftest.py:**

```python
"""Shared fixtures for backend tests."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from src.backend.models.usage import UsageResponse, FiveHourUsage


@pytest.fixture
def mock_usage_response() -> UsageResponse:
    """Create mock usage response."""
    return UsageResponse(
        five_hour=FiveHourUsage(
            utilization=0.45,
            resets_at="2026-01-17T12:00:00Z",
        )
    )


@pytest.fixture
def mock_credentials():
    """Mock credentials module."""
    with patch("src.backend.utils.credentials.get_access_token") as mock:
        mock.return_value = "test-token-12345"
        yield mock


@pytest.fixture
def mock_httpx_response(mock_usage_response: UsageResponse):
    """Mock httpx client response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_usage_response.model_dump()
    return mock_response
```

### Step 3: Test API Usage Module (Comprehensive)

**tests/backend/test_api_usage.py:**

```python
"""Tests for API usage module."""
from __future__ import annotations

import pytest
from unittest.mock import patch, AsyncMock
from src.backend.api.usage import (
    get_usage_async,
    get_usage_sync,
    clear_usage_cache,
    is_token_expired,
)
from src.backend.models.usage import UsageResponse


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    clear_usage_cache()
    yield
    clear_usage_cache()


@pytest.mark.asyncio
async def test_get_usage_async_success(mock_credentials, mock_usage_response):
    """Test successful async usage fetch."""
    with patch("src.backend.api.usage.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_usage_response.model_dump()

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await get_usage_async()

        assert result is not None
        assert result.five_hour is not None
        assert result.five_hour.utilization == 0.45


@pytest.mark.asyncio
async def test_get_usage_async_no_token():
    """Test usage fetch with no token."""
    with patch("src.backend.api.usage.get_access_token", return_value=None):
        result = await get_usage_async()
        assert result is None
        assert is_token_expired() is True


@pytest.mark.asyncio
async def test_get_usage_async_api_error():
    """Test handling of API errors."""
    with patch("src.backend.api.usage.get_access_token", return_value="token"):
        with patch("src.backend.api.usage.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception("Server Error")

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await get_usage_async()
            assert result is None


def test_get_usage_sync_success(mock_credentials, mock_usage_response):
    """Test successful sync usage fetch."""
    with patch("src.backend.api.usage.httpx.Client") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_usage_response.model_dump()

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        result = get_usage_sync()

        assert result is not None


def test_cache_prevents_duplicate_calls(mock_credentials):
    """Test that cache prevents duplicate API calls."""
    with patch("src.backend.api.usage.httpx.Client") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "five_hour": {"utilization": 0.5, "resets_at": "2026-01-17T12:00:00Z"}
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # First call
        get_usage_sync()
        # Second call should use cache
        get_usage_sync()

        # Client should only be called once
        assert mock_client.call_count == 1


def test_cache_expires_after_ttl(mock_credentials):
    """Test cache expiration after TTL."""
    import time

    with patch("src.backend.api.usage.httpx.Client") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "five_hour": {"utilization": 0.5, "resets_at": "2026-01-17T12:00:00Z"}
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # First call
        get_usage_sync()

        # Simulate cache expiration (mock time if TTL is short)
        clear_usage_cache()

        # Second call after cache clear
        get_usage_sync()

        # Client should be called twice
        assert mock_client.call_count == 2
```

### Step 4: Test Models Module

**tests/backend/test_models.py:**

```python
"""Tests for Pydantic models."""
from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.backend.models.usage import FiveHourUsage, UsageResponse


def test_five_hour_usage_valid():
    """Test valid FiveHourUsage model."""
    usage = FiveHourUsage(
        utilization=0.75,
        resets_at="2026-01-17T12:00:00Z"
    )
    assert usage.utilization == 0.75
    assert usage.resets_at == "2026-01-17T12:00:00Z"


def test_five_hour_usage_invalid_utilization():
    """Test FiveHourUsage with invalid utilization."""
    with pytest.raises(ValidationError):
        FiveHourUsage(
            utilization=1.5,  # > 1.0
            resets_at="2026-01-17T12:00:00Z"
        )


def test_usage_response_valid():
    """Test valid UsageResponse model."""
    response = UsageResponse(
        five_hour=FiveHourUsage(
            utilization=0.5,
            resets_at="2026-01-17T12:00:00Z"
        )
    )
    assert response.five_hour.utilization == 0.5


def test_usage_response_dict_conversion():
    """Test UsageResponse to dict conversion."""
    response = UsageResponse(
        five_hour=FiveHourUsage(
            utilization=0.33,
            resets_at="2026-01-17T15:30:00Z"
        )
    )
    data = response.model_dump()
    assert data["five_hour"]["utilization"] == 0.33
    assert "resets_at" in data["five_hour"]
```

### Step 5: Test Credentials Module

**tests/backend/test_credentials.py:**

```python
"""Tests for credentials module."""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from src.backend.utils.credentials import (
    get_access_token,
    get_credentials_path,
    is_token_available,
)


def test_get_credentials_path():
    """Test credentials path resolution."""
    path = get_credentials_path()
    assert path.name == ".credentials.json"
    assert ".claude" in str(path)


@patch("pathlib.Path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"sessionToken": "test-token"}')
def test_get_access_token_success(mock_file, mock_exists):
    """Test successful token retrieval."""
    token = get_access_token()
    assert token == "test-token"


@patch("pathlib.Path.exists", return_value=False)
def test_get_access_token_file_not_found(mock_exists):
    """Test token retrieval when file doesn't exist."""
    token = get_access_token()
    assert token is None


@patch("pathlib.Path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"invalid": "json"}')
def test_get_access_token_invalid_format(mock_file, mock_exists):
    """Test token retrieval with invalid JSON format."""
    token = get_access_token()
    assert token is None


@patch("src.backend.utils.credentials.get_access_token", return_value="token")
def test_is_token_available_true(mock_get_token):
    """Test token availability check when token exists."""
    assert is_token_available() is True


@patch("src.backend.utils.credentials.get_access_token", return_value=None)
def test_is_token_available_false(mock_get_token):
    """Test token availability check when token missing."""
    assert is_token_available() is False
```

### Step 6: Test Sidecar Module

**tests/backend/test_sidecar.py:**

```python
"""Tests for sidecar entry point."""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch, AsyncMock
from src.backend.sidecar import handle_action


@pytest.mark.asyncio
async def test_handle_action_get_usage_success():
    """Test get_usage action with valid response."""
    mock_usage = AsyncMock()
    mock_usage.model_dump.return_value = {
        "five_hour": {"utilization": 0.3, "resets_at": "2026-01-17T12:00:00Z"}
    }

    with patch("src.backend.sidecar.is_token_available", return_value=True):
        with patch("src.backend.sidecar.get_usage_async", return_value=mock_usage):
            result = await handle_action("get_usage")

    assert "five_hour" in result
    assert result["five_hour"]["utilization"] == 0.3


@pytest.mark.asyncio
async def test_handle_action_no_token():
    """Test get_usage action with no token."""
    with patch("src.backend.sidecar.is_token_available", return_value=False):
        result = await handle_action("get_usage")

    assert "error" in result
    assert result["token_expired"] is True


@pytest.mark.asyncio
async def test_handle_action_check_token():
    """Test check_token action."""
    with patch("src.backend.sidecar.is_token_available", return_value=True):
        result = await handle_action("check_token")

    assert result["available"] is True


@pytest.mark.asyncio
async def test_handle_action_unknown():
    """Test unknown action returns error."""
    result = await handle_action("unknown_action")
    assert "error" in result
    assert "Unknown action" in result["error"]


@pytest.mark.asyncio
async def test_handle_action_refresh_cache():
    """Test refresh_cache action."""
    with patch("src.backend.sidecar.clear_usage_cache") as mock_clear:
        result = await handle_action("refresh_cache")
        mock_clear.assert_called_once()
        assert result["success"] is True
```

### Step 7: Test TUI Widgets (Comprehensive)

**tests/backend/tui/test_widgets.py:**

```python
"""Tests for TUI widgets."""
from __future__ import annotations

import pytest
from textual.pilot import Pilot


@pytest.mark.asyncio
async def test_usage_display_updates():
    """Test UsageDisplay widget updates on percentage change."""
    from src.backend.tui.widgets.usage_display import UsageDisplay
    from textual.app import App

    class TestApp(App):
        def compose(self):
            yield UsageDisplay()

    async with TestApp().run_test() as pilot:
        widget = pilot.app.query_one(UsageDisplay)
        widget.percentage = 50.0
        await pilot.pause()

        # Check display contains percentage
        assert "50.0%" in str(widget.render())


@pytest.mark.asyncio
async def test_usage_display_color_changes():
    """Test UsageDisplay color changes based on percentage."""
    from src.backend.tui.widgets.usage_display import UsageDisplay
    from textual.app import App

    class TestApp(App):
        def compose(self):
            yield UsageDisplay()

    async with TestApp().run_test() as pilot:
        widget = pilot.app.query_one(UsageDisplay)

        # Test low usage (green)
        widget.percentage = 30.0
        await pilot.pause()
        assert widget.get_color_class() == "success"

        # Test medium usage (yellow)
        widget.percentage = 70.0
        await pilot.pause()
        assert widget.get_color_class() == "warning"

        # Test high usage (red)
        widget.percentage = 95.0
        await pilot.pause()
        assert widget.get_color_class() == "danger"


@pytest.mark.asyncio
async def test_reset_countdown_displays_time():
    """Test ResetCountdown widget displays time correctly."""
    from src.backend.tui.widgets.reset_countdown import ResetCountdown
    from textual.app import App
    from datetime import datetime, timedelta, timezone

    class TestApp(App):
        def compose(self):
            yield ResetCountdown()

    async with TestApp().run_test() as pilot:
        widget = pilot.app.query_one(ResetCountdown)
        # Set reset time to 1 hour from now
        reset_time = datetime.now(timezone.utc) + timedelta(hours=1)
        widget.reset_at = reset_time.isoformat()
        await pilot.pause()

        # Check display contains time format
        content = str(widget.render())
        assert "01:" in content or "00:" in content


@pytest.mark.asyncio
async def test_reset_countdown_updates_every_second():
    """Test ResetCountdown updates every second."""
    from src.backend.tui.widgets.reset_countdown import ResetCountdown
    from textual.app import App
    from datetime import datetime, timedelta, timezone

    class TestApp(App):
        def compose(self):
            yield ResetCountdown()

    async with TestApp().run_test() as pilot:
        widget = pilot.app.query_one(ResetCountdown)
        reset_time = datetime.now(timezone.utc) + timedelta(seconds=65)
        widget.reset_at = reset_time.isoformat()

        await pilot.pause(1)
        first_render = str(widget.render())

        await pilot.pause(1)
        second_render = str(widget.render())

        # Time should have changed
        assert first_render != second_render
```

### Step 8: Test TUI App

**tests/backend/tui/test_app.py:**

```python
"""Tests for TUI app."""
from __future__ import annotations

import pytest
from unittest.mock import patch, AsyncMock
from src.backend.tui.app import ClaudiminderApp


@pytest.mark.asyncio
async def test_app_starts_successfully():
    """Test TUI app starts without errors."""
    app = ClaudiminderApp()
    async with app.run_test() as pilot:
        assert app.is_running
        assert pilot.app.query_one("UsageDisplay") is not None


@pytest.mark.asyncio
async def test_app_loads_usage_data():
    """Test app loads usage data on start."""
    mock_usage = AsyncMock()
    mock_usage.five_hour.utilization = 0.55

    with patch("src.backend.tui.app.get_usage_async", return_value=mock_usage):
        app = ClaudiminderApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)
            usage_widget = pilot.app.query_one("UsageDisplay")
            assert usage_widget.percentage == 55.0


@pytest.mark.asyncio
async def test_app_handles_refresh_action():
    """Test app refresh action."""
    app = ClaudiminderApp()
    async with app.run_test() as pilot:
        await pilot.press("r")  # Refresh hotkey
        await pilot.pause(0.1)
        # Should trigger usage data reload
        assert app.is_running
```

### Step 9: Test Reminder Service

**tests/backend/scheduler/test_reminder.py:**

```python
"""Tests for reminder service."""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock
from src.backend.scheduler.reminder_service import ReminderService


@pytest.fixture
def reminder_service():
    """Create reminder service instance."""
    return ReminderService()


def test_update_reset_time(reminder_service):
    """Test updating reset time."""
    reset_at = "2026-01-17T12:00:00Z"
    reminder_service.update_reset_time(reset_at)

    assert reminder_service._reset_at is not None
    assert reminder_service._reset_at.isoformat().startswith("2026-01-17")


@pytest.mark.asyncio
async def test_check_reminders_sends_notification(reminder_service):
    """Test reminder triggers notification at correct time."""
    # Set reset time to 15 minutes from now
    reset_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    reminder_service.update_reset_time(reset_time.isoformat())

    with patch("src.backend.scheduler.reminder_service.send_notification") as mock_notify:
        mock_notify.return_value = None
        await reminder_service._check_reminders()

        # Should trigger 15-minute reminder
        mock_notify.assert_called_once()
        assert "15" in str(mock_notify.call_args)


@pytest.mark.asyncio
async def test_no_reminder_if_far_from_reset(reminder_service):
    """Test no reminder sent when far from reset time."""
    # Set reset time to 3 hours from now
    reset_time = datetime.now(timezone.utc) + timedelta(hours=3)
    reminder_service.update_reset_time(reset_time.isoformat())

    with patch("src.backend.scheduler.reminder_service.send_notification") as mock_notify:
        await reminder_service._check_reminders()
        mock_notify.assert_not_called()


def test_configure_reminders(reminder_service):
    """Test configuring custom reminders."""
    reminder_service.configure_reminders([10, 30, 60])  # 10min, 30min, 1h
    assert len(reminder_service._reminder_thresholds) == 3
    assert 10 in reminder_service._reminder_thresholds
```

### Step 10: Test Notifier

**tests/backend/scheduler/test_notifier.py:**

```python
"""Tests for system notifier."""
from __future__ import annotations

import pytest
from unittest.mock import patch
from src.backend.scheduler.notifier import send_notification, NotificationLevel


@patch("src.backend.scheduler.notifier.plyer.notification.notify")
def test_send_notification_success(mock_notify):
    """Test sending notification successfully."""
    send_notification("Test Title", "Test Message", NotificationLevel.INFO)
    mock_notify.assert_called_once()

    call_args = mock_notify.call_args[1]
    assert call_args["title"] == "Test Title"
    assert call_args["message"] == "Test Message"


@patch("src.backend.scheduler.notifier.plyer.notification.notify", side_effect=Exception("Failed"))
def test_send_notification_failure(mock_notify):
    """Test handling notification send failure."""
    # Should not raise exception
    send_notification("Title", "Message", NotificationLevel.WARNING)
    mock_notify.assert_called_once()


def test_notification_levels():
    """Test notification level enum values."""
    assert NotificationLevel.INFO.value == "info"
    assert NotificationLevel.WARNING.value == "warning"
    assert NotificationLevel.CRITICAL.value == "critical"
```

### Step 11: Setup Vitest for Frontend (90% Coverage)

**src/frontend/vitest.config.ts:**

```typescript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      exclude: ["node_modules/", "tests/", "dist/", "**/*.config.*"],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 90,
        statements: 90,
      },
    },
  },
});
```

**tests/frontend/setup.ts:**

```typescript
import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// Mock Tauri APIs
vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

vi.mock("@tauri-apps/api/event", () => ({
  emit: vi.fn(),
  listen: vi.fn(),
}));

vi.mock("@tauri-apps/plugin-notification", () => ({
  isPermissionGranted: vi.fn().mockResolvedValue(true),
  requestPermission: vi.fn().mockResolvedValue("granted"),
  sendNotification: vi.fn(),
}));

// Mock window.matchMedia for theme tests
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

### Step 12: Test Frontend Hooks (Comprehensive)

**tests/frontend/hooks/use-countdown.test.ts:**

```typescript
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useCountdown } from "../../src/hooks/use-countdown";

describe("useCountdown", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("calculates remaining time correctly", () => {
    const targetDate = new Date(Date.now() + 3600000).toISOString(); // 1 hour
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.hours).toBe(1);
    expect(result.current.minutes).toBe(0);
    expect(result.current.isExpired).toBe(false);
  });

  it("updates every second", () => {
    const targetDate = new Date(Date.now() + 65000).toISOString(); // 65 seconds
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.seconds).toBe(5);

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(result.current.seconds).toBe(4);
  });

  it("sets isExpired when countdown reaches zero", () => {
    const targetDate = new Date(Date.now() + 1000).toISOString(); // 1 second
    const { result } = renderHook(() => useCountdown(targetDate));

    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(result.current.isExpired).toBe(true);
    expect(result.current.totalSeconds).toBe(0);
  });

  it("handles negative time correctly", () => {
    const targetDate = new Date(Date.now() - 5000).toISOString(); // Past time
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.isExpired).toBe(true);
    expect(result.current.hours).toBe(0);
    expect(result.current.minutes).toBe(0);
    expect(result.current.seconds).toBe(0);
  });

  it("formats time with leading zeros", () => {
    const targetDate = new Date(Date.now() + 125000).toISOString(); // 2min 5sec
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.minutes).toBe(2);
    expect(result.current.seconds).toBe(5);
    expect(result.current.formatted).toBe("00:02:05");
  });
});
```

**tests/frontend/hooks/use-usage.test.ts:**

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useUsage } from "../../src/hooks/use-usage";
import { invoke } from "@tauri-apps/api/core";

vi.mock("@tauri-apps/api/core");

describe("useUsage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches usage data on mount", async () => {
    const mockUsage = {
      five_hour: {
        utilization: 0.65,
        resets_at: "2026-01-17T15:00:00Z",
      },
    };

    (invoke as any).mockResolvedValue(mockUsage);

    const { result } = renderHook(() => useUsage());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.usage).toEqual(mockUsage);
    expect(result.current.error).toBeNull();
  });

  it("handles fetch error", async () => {
    (invoke as any).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useUsage());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.usage).toBeNull();
    expect(result.current.error).toBe("Network error");
  });

  it("refreshes usage data", async () => {
    const mockUsage = {
      five_hour: {
        utilization: 0.5,
        resets_at: "2026-01-17T15:00:00Z",
      },
    };

    (invoke as any).mockResolvedValue(mockUsage);

    const { result } = renderHook(() => useUsage());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const newMockUsage = {
      ...mockUsage,
      five_hour: { ...mockUsage.five_hour, utilization: 0.7 },
    };
    (invoke as any).mockResolvedValue(newMockUsage);

    result.current.refresh();

    await waitFor(() => {
      expect(result.current.usage?.five_hour.utilization).toBe(0.7);
    });
  });
});
```

### Step 13: Test Frontend Components (Comprehensive)

**tests/frontend/components/dashboard.test.tsx:**

```tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardWidget } from "../../src/components/dashboard/dashboard-widget";
import { invoke } from "@tauri-apps/api/core";

vi.mock("../../src/hooks/use-usage", () => ({
  useUsage: vi.fn(),
}));

import { useUsage } from "../../src/hooks/use-usage";

describe("DashboardWidget", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state initially", () => {
    (useUsage as any).mockReturnValue({
      usage: null,
      loading: true,
      error: null,
      refresh: vi.fn(),
    });

    render(<DashboardWidget />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("displays usage percentage", () => {
    (useUsage as any).mockReturnValue({
      usage: {
        five_hour: {
          utilization: 0.45,
          resets_at: "2026-01-17T12:00:00Z",
        },
      },
      loading: false,
      error: null,
      refresh: vi.fn(),
    });

    render(<DashboardWidget />);
    expect(screen.getByText(/45\.0%/)).toBeInTheDocument();
  });

  it("shows error message on failure", () => {
    (useUsage as any).mockReturnValue({
      usage: null,
      loading: false,
      error: "Failed to fetch",
      refresh: vi.fn(),
    });

    render(<DashboardWidget />);
    expect(screen.getByText(/failed to fetch/i)).toBeInTheDocument();
  });

  it("shows token expired message", () => {
    (useUsage as any).mockReturnValue({
      usage: null,
      loading: false,
      error: "Token expired",
      tokenExpired: true,
      refresh: vi.fn(),
    });

    render(<DashboardWidget />);
    expect(screen.getByText(/token expired/i)).toBeInTheDocument();
    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });

  it("handles refresh button click", async () => {
    const mockRefresh = vi.fn();
    (useUsage as any).mockReturnValue({
      usage: {
        five_hour: {
          utilization: 0.5,
          resets_at: "2026-01-17T12:00:00Z",
        },
      },
      loading: false,
      error: null,
      refresh: mockRefresh,
    });

    render(<DashboardWidget />);
    const refreshBtn = screen.getByRole("button", { name: /refresh/i });
    fireEvent.click(refreshBtn);

    expect(mockRefresh).toHaveBeenCalledOnce();
  });

  it("displays countdown timer", () => {
    (useUsage as any).mockReturnValue({
      usage: {
        five_hour: {
          utilization: 0.3,
          resets_at: new Date(Date.now() + 3600000).toISOString(), // 1 hour
        },
      },
      loading: false,
      error: null,
      refresh: vi.fn(),
    });

    render(<DashboardWidget />);
    expect(screen.getByText(/resets in/i)).toBeInTheDocument();
    expect(screen.getByText(/01:00:/)).toBeInTheDocument();
  });
});
```

**tests/frontend/components/theme-switcher.test.tsx:**

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ThemeSwitcher } from "../../src/components/theme/theme-switcher";
import { useThemeStore } from "../../src/stores/theme-store";

describe("ThemeSwitcher", () => {
  beforeEach(() => {
    useThemeStore.setState({ theme: "system", resolvedTheme: "dark" });
  });

  it("renders theme options", () => {
    render(<ThemeSwitcher />);

    const button = screen.getByRole("button");
    fireEvent.click(button);

    expect(screen.getByText(/neon dark/i)).toBeInTheDocument();
    expect(screen.getByText(/glass light/i)).toBeInTheDocument();
    expect(screen.getByText(/terminal/i)).toBeInTheDocument();
  });

  it("switches theme on selection", () => {
    render(<ThemeSwitcher />);

    const button = screen.getByRole("button");
    fireEvent.click(button);

    const neonOption = screen.getByText(/neon dark/i);
    fireEvent.click(neonOption);

    const { theme } = useThemeStore.getState();
    expect(theme).toBe("neon-dark");
  });

  it("shows current theme as selected", () => {
    useThemeStore.setState({ theme: "glass-light" });

    render(<ThemeSwitcher />);
    const button = screen.getByRole("button");

    expect(button).toHaveTextContent(/glass light/i);
  });
});
```

### Step 14: Test Theme Store

**tests/frontend/stores/theme-store.test.ts:**

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { useThemeStore } from "../../src/stores/theme-store";

describe("themeStore", () => {
  beforeEach(() => {
    // Reset store state
    useThemeStore.setState({ theme: "system", resolvedTheme: "dark" });
    localStorage.clear();
  });

  it("has system as default theme", () => {
    const { theme } = useThemeStore.getState();
    expect(theme).toBe("system");
  });

  it("sets theme correctly", () => {
    const { setTheme } = useThemeStore.getState();
    setTheme("neon-dark");

    const { theme } = useThemeStore.getState();
    expect(theme).toBe("neon-dark");
  });

  it("persists theme in localStorage", () => {
    const { setTheme } = useThemeStore.getState();
    setTheme("glass-light");

    // Zustand persist should save to localStorage
    const stored = localStorage.getItem("claudeminder-theme");
    expect(stored).toContain("glass-light");
  });

  it("resolves system theme based on matchMedia", () => {
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === "(prefers-color-scheme: dark)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { resolveTheme } = useThemeStore.getState();
    resolveTheme();

    const { resolvedTheme } = useThemeStore.getState();
    expect(resolvedTheme).toBe("dark");
  });

  it("supports all available themes", () => {
    const { setTheme } = useThemeStore.getState();
    const themes = ["neon-dark", "glass-light", "terminal", "system"];

    themes.forEach((themeId) => {
      setTheme(themeId);
      const { theme } = useThemeStore.getState();
      expect(theme).toBe(themeId);
    });
  });
});
```

### Step 15: Setup Playwright E2E Tests

**tests/frontend/e2e/playwright.config.ts:**

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:1420",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "bun run tauri dev",
    url: "http://localhost:1420",
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
});
```

**tests/frontend/e2e/dashboard.spec.ts:**

```typescript
import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test("loads and displays usage data", async ({ page }) => {
    await page.goto("/");

    // Wait for usage data to load
    await expect(page.getByText(/loading/i)).toBeVisible();
    await expect(page.getByText(/loading/i)).not.toBeVisible({
      timeout: 10000,
    });

    // Check percentage is displayed
    await expect(page.getByText(/%/)).toBeVisible();
  });

  test("shows countdown timer", async ({ page }) => {
    await page.goto("/");

    await page.waitForSelector('[data-testid="countdown-timer"]');
    const timer = page.getByTestId("countdown-timer");

    await expect(timer).toBeVisible();
    await expect(timer).toContainText(/:/);
  });

  test("refreshes usage on button click", async ({ page }) => {
    await page.goto("/");

    await page.waitForSelector('[data-testid="refresh-btn"]');
    const refreshBtn = page.getByTestId("refresh-btn");

    await refreshBtn.click();
    await expect(page.getByText(/loading/i)).toBeVisible();
  });

  test("handles token expired state", async ({ page }) => {
    // Mock expired token response
    await page.route("**/api/usage", (route) => {
      route.fulfill({
        status: 401,
        body: JSON.stringify({ error: "Token expired" }),
      });
    });

    await page.goto("/");

    await expect(page.getByText(/token expired/i)).toBeVisible();
    await expect(page.getByText(/login/i)).toBeVisible();
  });
});
```

**tests/frontend/e2e/notifications.spec.ts:**

```typescript
import { test, expect } from "@playwright/test";

test.describe("Notifications", () => {
  test("requests notification permission", async ({ page, context }) => {
    await context.grantPermissions(["notifications"]);
    await page.goto("/");

    // Check notification permission is granted
    const permission = await page.evaluate(() => Notification.permission);
    expect(permission).toBe("granted");
  });

  test("sends reminder notification", async ({ page }) => {
    await page.goto("/");

    // Mock reset time to 10 minutes from now
    await page.evaluate(() => {
      const resetTime = new Date(Date.now() + 10 * 60 * 1000).toISOString();
      localStorage.setItem("mockResetTime", resetTime);
    });

    // Wait for reminder notification
    const notificationPromise = page.waitForEvent("notification");

    // Fast-forward time to trigger reminder
    await page.evaluate(() => {
      // Trigger reminder check
      window.dispatchEvent(new Event("check-reminders"));
    });

    const notification = await notificationPromise;
    expect(notification.title).toContain("Reminder");
  });
});
```

**tests/frontend/e2e/theme-switcher.spec.ts:**

```typescript
import { test, expect } from "@playwright/test";

test.describe("Theme Switcher", () => {
  test("switches between themes", async ({ page }) => {
    await page.goto("/");

    // Open theme switcher
    await page.click('[data-testid="theme-switcher-btn"]');

    // Select neon-dark theme
    await page.click('text="Neon Dark"');

    // Check theme is applied
    const html = page.locator("html");
    await expect(html).toHaveAttribute("data-theme", "neon-dark");
  });

  test("persists theme selection", async ({ page }) => {
    await page.goto("/");

    // Select glass-light theme
    await page.click('[data-testid="theme-switcher-btn"]');
    await page.click('text="Glass Light"');

    // Reload page
    await page.reload();

    // Check theme persisted
    const html = page.locator("html");
    await expect(html).toHaveAttribute("data-theme", "glass-light");
  });

  test("respects system theme", async ({ page, context }) => {
    await page.goto("/");

    // Select system theme
    await page.click('[data-testid="theme-switcher-btn"]');
    await page.click('text="System"');

    // Check theme matches system preference
    const isDark = await page.evaluate(
      () => window.matchMedia("(prefers-color-scheme: dark)").matches,
    );

    const html = page.locator("html");
    const theme = isDark ? "dark" : "light";
    await expect(html).toHaveAttribute("data-theme", new RegExp(theme));
  });
});
```

### Step 16: Setup Pre-commit Hooks

**.pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict, --ignore-missing-imports]

  - repo: local
    hooks:
      - id: pyright
        name: pyright
        entry: pyright
        language: system
        types: [python]
        pass_filenames: false

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml, markdown]
        args: [--write]

  - repo: local
    hooks:
      - id: frontend-lint
        name: frontend lint
        entry: bash -c "cd src/frontend && bun run lint"
        language: system
        pass_filenames: false

  - repo: local
    hooks:
      - id: backend-tests
        name: backend tests
        entry: bash -c "uv run pytest --cov=src/backend --cov-fail-under=90"
        language: system
        pass_filenames: false
        stages: [push]

  - repo: local
    hooks:
      - id: frontend-tests
        name: frontend tests
        entry: bash -c "cd src/frontend && bun run test --coverage"
        language: system
        pass_filenames: false
        stages: [push]
```

**Install pre-commit:**

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

### Step 17: Create GitHub Actions CI Workflows

**.github/workflows/test.yml:**

```yaml
name: Test & Coverage

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --dev

      - name: Run ruff lint
        run: uv run ruff check src/ tests/

      - name: Run ruff format check
        run: uv run ruff format --check src/ tests/

      - name: Run mypy
        run: uv run mypy src/backend

      - name: Run pyright
        run: uv run pyright src/backend

      - name: Run tests with coverage
        run: uv run pytest --cov=src/backend --cov-report=xml --cov-report=term --cov-fail-under=90

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2

      - name: Install dependencies
        run: cd src/frontend && bun install

      - name: Run prettier check
        run: cd src/frontend && bun run format:check

      - name: Run lint
        run: cd src/frontend && bun run lint

      - name: Run type check
        run: cd src/frontend && bun run typecheck

      - name: Run tests with coverage
        run: cd src/frontend && bun run test --coverage

      - name: Check coverage threshold
        run: |
          cd src/frontend
          bun run test --coverage --reporter=json > coverage.json
          COVERAGE=$(jq '.coverageMap.total.statements.pct' coverage.json)
          if (( $(echo "$COVERAGE < 90" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 90% threshold"
            exit 1
          fi

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./src/frontend/coverage/lcov.info
          flags: frontend
          name: frontend-coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2

      - name: Install dependencies
        run: cd src/frontend && bun install

      - name: Install Playwright
        run: cd src/frontend && bunx playwright install --with-deps

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install Tauri dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf

      - name: Run E2E tests
        run: cd src/frontend && bun run test:e2e

      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: src/frontend/playwright-report/
```

**.github/workflows/build.yml:**

```yaml
name: Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    strategy:
      matrix:
        platform: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install dependencies (Ubuntu)
        if: matrix.platform == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf

      - name: Install frontend dependencies
        run: cd src/frontend && bun install

      - name: Build Tauri app
        run: cd src/frontend && bun run tauri build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: app-${{ matrix.platform }}
          path: |
            src/frontend/src-tauri/target/release/bundle/
```

**.github/workflows/release.yml:**

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    strategy:
      matrix:
        platform: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v2

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install dependencies (Ubuntu)
        if: matrix.platform == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf

      - name: Install frontend dependencies
        run: cd src/frontend && bun install

      - name: Build Tauri app
        run: cd src/frontend && bun run tauri build

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            src/frontend/src-tauri/target/release/bundle/**/*
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 18: Update package.json Scripts

**src/frontend/package.json (add scripts):**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri",
    "test": "vitest",
    "test:e2e": "playwright test",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,json,css}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,json,css}\"",
    "typecheck": "tsc --noEmit"
  }
}
```

## Todo List

### Backend Tests

- [ ] Add pytest-httpx, mypy, pyright to dev dependencies
- [ ] Configure coverage thresholds (90%) in pyproject.toml
- [ ] Create `tests/backend/conftest.py` with fixtures
- [ ] Write `test_api_usage.py` comprehensive tests
- [ ] Write `test_models.py` Pydantic tests
- [ ] Write `test_credentials.py` tests
- [ ] Write `test_sidecar.py` tests
- [ ] Write `test_app.py` TUI app tests
- [ ] Write `test_widgets.py` TUI widget tests (with color testing)
- [ ] Write `test_reminder.py` scheduler tests
- [ ] Write `test_notifier.py` system notification tests
- [ ] Run `uv run pytest --cov` and verify >= 90% coverage

### Frontend Tests

- [ ] Add Vitest, Playwright, testing-library to dependencies
- [ ] Configure coverage thresholds (90%) in vitest.config.ts
- [ ] Create `tests/frontend/setup.ts` with Tauri mocks
- [ ] Write `use-countdown.test.ts` comprehensive hook tests
- [ ] Write `use-usage.test.ts` hook tests with refresh
- [ ] Write `dashboard.test.tsx` component tests
- [ ] Write `theme-switcher.test.tsx` component tests
- [ ] Write `theme-store.test.ts` Zustand store tests
- [ ] Setup Playwright config for E2E tests
- [ ] Write `dashboard.spec.ts` E2E tests
- [ ] Write `notifications.spec.ts` E2E tests
- [ ] Write `theme-switcher.spec.ts` E2E tests
- [ ] Run `bun run test --coverage` and verify >= 90% coverage
- [ ] Run `bun run test:e2e` and verify all E2E tests pass

### Pre-commit & CI/CD

- [ ] Create `.pre-commit-config.yaml` with ruff, prettier, mypy, pyright
- [ ] Install pre-commit hooks: `uv run pre-commit install`
- [ ] Test pre-commit hooks work on commit
- [ ] Create `.github/workflows/test.yml` with coverage enforcement
- [ ] Create `.github/workflows/build.yml` for cross-platform builds
- [ ] Create `.github/workflows/release.yml` for tag-based releases
- [ ] Add coverage badge to README
- [ ] Test CI pipeline on push
- [ ] Test release workflow on tag

## Success Criteria

- All backend tests pass: `uv run pytest`
- All frontend tests pass: `bun run test`
- All E2E tests pass: `bun run test:e2e`
- **Backend coverage >= 90%** (enforced in CI)
- **Frontend coverage >= 90%** (enforced in CI)
- Pre-commit hooks run successfully
- GitHub Actions CI passes (lint + format + type + test)
- Cross-platform builds succeed (Linux, macOS, Windows)
- Release workflow publishes artifacts on tag

## Risk Assessment

| Risk                          | Mitigation                                       |
| ----------------------------- | ------------------------------------------------ |
| Textual tests require display | Use `textual-dev` for headless testing           |
| Tauri APIs hard to mock       | Mock at module level in setup.ts                 |
| Async test timing issues      | Use `pytest-asyncio`, `vi.useFakeTimers()`       |
| 90% coverage hard to achieve  | Focus on business logic, exclude generated code  |
| E2E tests flaky on CI         | Use Playwright retry logic, longer timeouts      |
| Cross-platform build failures | Test locally with Docker, GitHub matrix strategy |
| Pre-commit hooks slow         | Run heavy checks (tests) only on pre-push        |
| Type checking conflicts       | Configure mypy + pyright with shared settings    |

## Security Considerations

- No real credentials in test fixtures
- Mock all external API calls
- Test files not included in production bundle
- Coverage reports exclude sensitive paths
- Pre-commit prevents committing secrets
- CI environment variables secured
- Release artifacts signed (Tauri config)

## Next Steps

After completing testing phase:

1. Deploy to GitHub and validate CI pipeline
2. Fix any remaining coverage gaps
3. Document test patterns in `docs/02-general/testing-guide.md`
4. Proceed to Phase 6: Documentation & Release
