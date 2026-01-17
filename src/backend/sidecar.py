"""Sidecar module for Tauri integration.

This module provides a JSON interface for the Tauri GUI to communicate
with the Python backend. It can be invoked via CLI or as a standalone binary.

Usage:
    python -m claudeminder.sidecar get_usage
    python -m claudeminder.sidecar refresh_usage
    python -m claudeminder.sidecar check_token
    python -m claudeminder.sidecar get_config
    python -m claudeminder.sidecar set_config '{"language": "vi"}'
    python -m claudeminder.sidecar snooze 15
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from typing import Any

from loguru import logger

from .api.usage import RateLimitError, TokenExpiredError, clear_usage_cache, get_usage_async
from .core.config_manager import AppConfig, load_config, save_config
from .core.goals_tracker import get_goals_tracker
from .scheduler import get_focus_mode_service, get_reminder_service
from .utils.credentials import is_token_available


def _json_response(data: dict[str, Any] | None = None, error: str | None = None) -> str:
    """Create JSON response string."""
    response: dict[str, Any] = {}
    if data is not None:
        response.update(data)
    if error is not None:
        response["error"] = error
    return json.dumps(response)


async def get_usage() -> str:
    """Get current usage data as JSON."""
    try:
        # Check token availability first
        if not is_token_available():
            return _json_response(
                error="No OAuth token available",
                data={"token_expired": True}
            )

        usage = await get_usage_async()

        result: dict[str, Any] = {}

        if usage and usage.five_hour:
            result["five_hour"] = {
                "utilization": usage.five_hour.utilization,
                "resets_at": usage.five_hour.resets_at,
            }
        else:
            result["five_hour"] = None

        # Add goals status
        if usage and usage.five_hour:
            tracker = get_goals_tracker()
            pace = tracker.calculate_pace(usage.five_hour.utilization)
            result["goals"] = {
                "enabled": load_config().goals.enabled,
                "is_on_track": pace.is_on_track,
                "current_usage": pace.current_usage,
                "expected_usage": pace.expected_usage,
                "message": pace.message,
            }

        # Add focus mode status
        focus_service = get_focus_mode_service()
        current_usage = usage.five_hour.utilization if usage and usage.five_hour else 0
        result["focus_mode"] = {
            "is_snoozed": focus_service.is_snoozed(),
            "snooze_remaining": focus_service.get_snooze_remaining(),
            "is_quiet_hours": focus_service.is_in_quiet_hours(),
            "is_dnd": focus_service.is_dnd_by_usage(current_usage),
            "notifications_suppressed": focus_service.should_suppress_notification(current_usage),
        }

        return _json_response(result)

    except TokenExpiredError as e:
        logger.warning(f"Token expired: {e}")
        return _json_response(
            error="OAuth token expired",
            data={"token_expired": True}
        )
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        return _json_response(
            error="Rate limit exceeded",
            data={"rate_limited": True}
        )
    except Exception as e:
        error_msg = str(e).lower()
        # Detect network/connection errors for offline mode
        if any(keyword in error_msg for keyword in ["connection", "network", "timeout", "unreachable"]):
            logger.warning(f"Network error (offline): {e}")
            return _json_response(
                error="Network error",
                data={"offline": True}
            )
        logger.error(f"Sidecar get_usage error: {e}")
        return _json_response(error=str(e))


async def refresh_usage() -> str:
    """Force refresh usage data."""
    # Clear any cached data and fetch fresh
    clear_usage_cache()
    return await get_usage()


def check_token() -> str:
    """Check if OAuth token is available."""
    try:
        available = is_token_available()
        return _json_response({"available": available})
    except Exception as e:
        logger.error(f"Sidecar check_token error: {e}")
        return _json_response(error=str(e))


def get_config() -> str:
    """Get current configuration as JSON."""
    try:
        config = load_config()
        return _json_response({"config": config.model_dump()})
    except Exception as e:
        logger.error(f"Sidecar get_config error: {e}")
        return _json_response(error=str(e))


def set_config(config_json: str) -> str:
    """Update configuration from JSON."""
    try:
        updates = json.loads(config_json)
        current = load_config()

        # Merge updates into current config
        current_dict = current.model_dump()
        _deep_merge(current_dict, updates)

        new_config = AppConfig.model_validate(current_dict)
        save_config(new_config)

        return _json_response({"success": True, "config": new_config.model_dump()})
    except Exception as e:
        logger.error(f"Sidecar set_config error: {e}")
        return _json_response(error=str(e))


def _deep_merge(base: dict[str, Any], updates: dict[str, Any]) -> None:
    """Deep merge updates into base dict."""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def snooze(minutes: int) -> str:
    """Snooze notifications for specified minutes."""
    try:
        focus_service = get_focus_mode_service()
        focus_service.snooze(minutes)

        return _json_response(
            {
                "success": True,
                "snoozed_until": (datetime.now().timestamp() + minutes * 60),
                "snooze_remaining": focus_service.get_snooze_remaining(),
            }
        )
    except Exception as e:
        logger.error(f"Sidecar snooze error: {e}")
        return _json_response(error=str(e))


def clear_snooze() -> str:
    """Clear any active snooze."""
    try:
        focus_service = get_focus_mode_service()
        focus_service.clear_snooze()
        return _json_response({"success": True})
    except Exception as e:
        logger.error(f"Sidecar clear_snooze error: {e}")
        return _json_response(error=str(e))


def check_reminders(usage_percent: float, reset_time_iso: str | None) -> str:
    """Check and trigger reminders based on current state."""
    try:
        reminder_service = get_reminder_service()

        reset_time = None
        if reset_time_iso:
            reset_time = datetime.fromisoformat(reset_time_iso.replace("Z", "+00:00"))

        triggered = reminder_service.check_and_trigger(usage_percent, reset_time)

        return _json_response({
            "triggered": [
                {"type": t.value, "message": m}
                for t, m in triggered
            ]
        })
    except Exception as e:
        logger.error(f"Sidecar check_reminders error: {e}")
        return _json_response(error=str(e))


def main() -> None:
    """CLI entry point for sidecar."""
    if len(sys.argv) < 2:
        print(_json_response(error="Usage: sidecar <action> [args...]"))
        sys.exit(1)

    action = sys.argv[1]
    args = sys.argv[2:]

    # Configure minimal logging for sidecar
    logger.remove()
    logger.add(sys.stderr, level="ERROR")

    try:
        if action == "get_usage":
            result = asyncio.run(get_usage())
        elif action == "refresh_usage":
            result = asyncio.run(refresh_usage())
        elif action == "check_token":
            result = check_token()
        elif action == "get_config":
            result = get_config()
        elif action == "set_config":
            if not args:
                result = _json_response(error="set_config requires JSON argument")
            else:
                result = set_config(args[0])
        elif action == "snooze":
            if not args:
                result = _json_response(error="snooze requires minutes argument")
            else:
                result = snooze(int(args[0]))
        elif action == "clear_snooze":
            result = clear_snooze()
        elif action == "check_reminders":
            if len(args) < 1:
                result = _json_response(error="check_reminders requires usage_percent")
            else:
                usage = float(args[0])
                reset_time = args[1] if len(args) > 1 else None
                result = check_reminders(usage, reset_time)
        else:
            result = _json_response(error=f"Unknown action: {action}")

        print(result)

    except Exception as e:
        print(_json_response(error=str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
