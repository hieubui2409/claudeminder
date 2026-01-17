"""Tests for sidecar module."""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.sidecar import (
    _deep_merge,
    _json_response,
    check_reminders,
    check_token,
    clear_snooze,
    get_config,
    get_usage,
    refresh_usage,
    set_config,
    snooze,
)


class TestJsonResponse:
    """Tests for _json_response helper."""

    def test_empty_response(self):
        """Test empty response."""
        result = _json_response()
        assert json.loads(result) == {}

    def test_data_response(self):
        """Test response with data."""
        result = _json_response(data={"key": "value"})
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_error_response(self):
        """Test response with error."""
        result = _json_response(error="Test error")
        parsed = json.loads(result)
        assert parsed["error"] == "Test error"

    def test_data_and_error(self):
        """Test response with both data and error."""
        result = _json_response(data={"status": "partial"}, error="Warning")
        parsed = json.loads(result)
        assert parsed["status"] == "partial"
        assert parsed["error"] == "Warning"


class TestDeepMerge:
    """Tests for _deep_merge helper."""

    def test_simple_merge(self):
        """Test simple merge."""
        base = {"a": 1, "b": 2}
        updates = {"b": 3, "c": 4}
        _deep_merge(base, updates)
        assert base == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self):
        """Test nested dict merge."""
        base = {"a": {"x": 1, "y": 2}}
        updates = {"a": {"y": 3, "z": 4}}
        _deep_merge(base, updates)
        assert base == {"a": {"x": 1, "y": 3, "z": 4}}

    def test_replace_non_dict(self):
        """Test replacing non-dict values."""
        base = {"a": {"x": 1}}
        updates = {"a": "string"}
        _deep_merge(base, updates)
        assert base == {"a": "string"}


class TestGetUsage:
    """Tests for get_usage function."""

    @pytest.mark.asyncio
    async def test_returns_error_when_no_token(self):
        """Test returns error when no token available."""
        with patch("backend.sidecar.is_token_available", return_value=False):
            result = await get_usage()
            parsed = json.loads(result)
            assert "error" in parsed
            assert parsed["token_expired"] is True

    @pytest.mark.asyncio
    async def test_returns_usage_data(self):
        """Test returns usage data on success."""
        mock_usage = MagicMock()
        mock_usage.five_hour = MagicMock()
        mock_usage.five_hour.utilization = 0.45
        mock_usage.five_hour.resets_at = "2026-01-17T12:00:00Z"

        with patch("backend.sidecar.is_token_available", return_value=True):
            with patch(
                "backend.sidecar.get_usage_async",
                new_callable=AsyncMock,
                return_value=mock_usage,
            ):
                with patch("backend.sidecar.get_goals_tracker") as mock_tracker:
                    mock_pace = MagicMock()
                    mock_pace.is_on_track = True
                    mock_pace.current_usage = 0.45
                    mock_pace.expected_usage = 0.5
                    mock_pace.message = "On track"
                    mock_tracker.return_value.calculate_pace.return_value = mock_pace

                    with patch("backend.sidecar.load_config") as mock_config:
                        mock_config.return_value.goals.enabled = True

                        with patch(
                            "backend.sidecar.get_focus_mode_service"
                        ) as mock_focus:
                            mock_focus_instance = MagicMock()
                            mock_focus_instance.is_snoozed.return_value = False
                            mock_focus_instance.get_snooze_remaining.return_value = 0
                            mock_focus_instance.is_in_quiet_hours.return_value = False
                            mock_focus_instance.is_dnd_by_usage.return_value = False
                            mock_focus_instance.should_suppress_notification.return_value = (
                                False
                            )
                            mock_focus.return_value = mock_focus_instance

                            result = await get_usage()
                            parsed = json.loads(result)

                            assert "five_hour" in parsed
                            assert parsed["five_hour"]["utilization"] == 0.45

    @pytest.mark.asyncio
    async def test_handles_token_expired_error(self):
        """Test handles TokenExpiredError."""
        from backend.api.usage import TokenExpiredError

        with patch("backend.sidecar.is_token_available", return_value=True):
            with patch(
                "backend.sidecar.get_usage_async",
                new_callable=AsyncMock,
                side_effect=TokenExpiredError("Token expired"),
            ):
                result = await get_usage()
                parsed = json.loads(result)
                assert parsed["token_expired"] is True

    @pytest.mark.asyncio
    async def test_handles_rate_limit_error(self):
        """Test handles RateLimitError."""
        from backend.api.usage import RateLimitError

        with patch("backend.sidecar.is_token_available", return_value=True):
            with patch(
                "backend.sidecar.get_usage_async",
                new_callable=AsyncMock,
                side_effect=RateLimitError("Rate limited"),
            ):
                result = await get_usage()
                parsed = json.loads(result)
                assert parsed["rate_limited"] is True

    @pytest.mark.asyncio
    async def test_handles_network_error(self):
        """Test handles network error for offline mode."""
        with patch("backend.sidecar.is_token_available", return_value=True):
            with patch(
                "backend.sidecar.get_usage_async",
                new_callable=AsyncMock,
                side_effect=Exception("Connection timeout"),
            ):
                result = await get_usage()
                parsed = json.loads(result)
                assert parsed["offline"] is True


class TestRefreshUsage:
    """Tests for refresh_usage function."""

    @pytest.mark.asyncio
    async def test_clears_cache_and_fetches(self):
        """Test clears cache before fetching."""
        with patch("backend.sidecar.clear_usage_cache") as mock_clear:
            with patch(
                "backend.sidecar.get_usage",
                new_callable=AsyncMock,
                return_value='{"five_hour": null}',
            ):
                await refresh_usage()
                mock_clear.assert_called_once()


class TestCheckToken:
    """Tests for check_token function."""

    def test_returns_true_when_available(self):
        """Test returns True when token available."""
        with patch("backend.sidecar.is_token_available", return_value=True):
            result = check_token()
            parsed = json.loads(result)
            assert parsed["available"] is True

    def test_returns_false_when_not_available(self):
        """Test returns False when token not available."""
        with patch("backend.sidecar.is_token_available", return_value=False):
            result = check_token()
            parsed = json.loads(result)
            assert parsed["available"] is False


class TestSnooze:
    """Tests for snooze function."""

    def test_snoozes_notifications(self):
        """Test snoozes notifications for specified minutes."""
        with patch("backend.sidecar.get_focus_mode_service") as mock_focus:
            mock_instance = MagicMock()
            mock_instance.get_snooze_remaining.return_value = 15 * 60
            mock_focus.return_value = mock_instance

            result = snooze(15)
            parsed = json.loads(result)

            assert parsed["success"] is True
            mock_instance.snooze.assert_called_once_with(15)


class TestClearSnooze:
    """Tests for clear_snooze function."""

    def test_clears_snooze(self):
        """Test clears active snooze."""
        with patch("backend.sidecar.get_focus_mode_service") as mock_focus:
            mock_instance = MagicMock()
            mock_focus.return_value = mock_instance

            result = clear_snooze()
            parsed = json.loads(result)

            assert parsed["success"] is True
            mock_instance.clear_snooze.assert_called_once()


class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_config(self):
        """Test returns current config."""
        with patch("backend.sidecar.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.model_dump.return_value = {"language": "en"}
            mock_load.return_value = mock_config

            result = get_config()
            parsed = json.loads(result)

            assert "config" in parsed
            assert parsed["config"]["language"] == "en"


class TestSetConfig:
    """Tests for set_config function."""

    def test_updates_config(self):
        """Test updates config with new values."""
        with patch("backend.sidecar.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.model_dump.return_value = {"language": "en", "theme": "dark"}
            mock_load.return_value = mock_config

            with patch("backend.sidecar.save_config"):
                with patch("backend.sidecar.AppConfig") as mock_app_config:
                    mock_new_config = MagicMock()
                    mock_new_config.model_dump.return_value = {
                        "language": "vi",
                        "theme": "dark",
                    }
                    mock_app_config.model_validate.return_value = mock_new_config

                    result = set_config('{"language": "vi"}')
                    parsed = json.loads(result)

                    assert parsed["success"] is True

    def test_handles_invalid_json(self):
        """Test handles invalid JSON input."""
        result = set_config("not valid json")
        parsed = json.loads(result)
        assert "error" in parsed


class TestCheckReminders:
    """Tests for check_reminders function."""

    def test_triggers_reminders(self):
        """Test triggers reminders based on state."""
        with patch("backend.sidecar.get_reminder_service") as mock_service:
            from backend.scheduler.reminder_service import ReminderType

            mock_instance = MagicMock()
            mock_instance.check_and_trigger.return_value = [
                (ReminderType.PERCENTAGE, "90% usage reached")
            ]
            mock_service.return_value = mock_instance

            result = check_reminders(0.9, "2026-01-17T12:00:00Z")
            parsed = json.loads(result)

            assert "triggered" in parsed
            assert len(parsed["triggered"]) == 1
            assert parsed["triggered"][0]["type"] == "percentage"

    def test_handles_no_reset_time(self):
        """Test handles missing reset time."""
        with patch("backend.sidecar.get_reminder_service") as mock_service:
            mock_instance = MagicMock()
            mock_instance.check_and_trigger.return_value = []
            mock_service.return_value = mock_instance

            result = check_reminders(0.5, None)
            parsed = json.loads(result)

            assert parsed["triggered"] == []
