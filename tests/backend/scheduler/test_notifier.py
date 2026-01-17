"""Tests for notification system."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.scheduler.notifier import (
    NotificationChannel,
    _get_notifier,
    send_notification,
    send_notification_sync,
)


class TestNotificationChannel:
    """Test notification channel enum."""

    def test_channel_values(self):
        """Test channel enum values."""
        assert NotificationChannel.SYSTEM.value == "system"
        assert NotificationChannel.BELL.value == "bell"
        assert NotificationChannel.COMMAND.value == "command"
        assert NotificationChannel.URL.value == "url"


class TestGetNotifier:
    """Test notifier singleton."""

    def test_get_notifier_is_callable(self):
        """Test that _get_notifier function exists."""
        assert callable(_get_notifier)


class TestSendNotification:
    """Test async notification sending."""

    @pytest.mark.asyncio
    async def test_send_system_notification(self):
        """Test sending system notification."""
        mock_notifier = MagicMock()
        mock_notifier.send = AsyncMock()

        with patch("backend.scheduler.notifier._get_notifier", return_value=mock_notifier):
            result = await send_notification(
                "Test Title",
                "Test Body",
                [NotificationChannel.SYSTEM],
            )
            assert NotificationChannel.SYSTEM in result
            mock_notifier.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_bell_notification(self):
        """Test sending bell notification."""
        with patch("builtins.print") as mock_print:
            result = await send_notification(
                "Test",
                "Body",
                [NotificationChannel.BELL],
            )
            assert NotificationChannel.BELL in result
            mock_print.assert_called_once_with("\a", end="", flush=True)

    @pytest.mark.asyncio
    async def test_send_command_notification(self):
        """Test sending custom command notification."""
        mock_config = MagicMock()
        mock_config.reminder.custom_command = "echo test"

        with patch("backend.scheduler.notifier.load_config", return_value=mock_config):
            with patch("subprocess.Popen") as mock_popen:
                result = await send_notification(
                    "Test",
                    "Body",
                    [NotificationChannel.COMMAND],
                )
                assert NotificationChannel.COMMAND in result
                mock_popen.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_command_notification_no_command(self):
        """Test command notification when no command configured."""
        mock_config = MagicMock()
        mock_config.reminder.custom_command = None

        with patch("backend.scheduler.notifier.load_config", return_value=mock_config):
            result = await send_notification(
                "Test",
                "Body",
                [NotificationChannel.COMMAND],
            )
            assert NotificationChannel.COMMAND not in result

    @pytest.mark.asyncio
    async def test_send_url_notification(self):
        """Test opening URL notification."""
        mock_config = MagicMock()
        mock_config.reminder.custom_url = "https://example.com"

        with patch("backend.scheduler.notifier.load_config", return_value=mock_config):
            with patch("webbrowser.open") as mock_open:
                result = await send_notification(
                    "Test",
                    "Body",
                    [NotificationChannel.URL],
                )
                assert NotificationChannel.URL in result
                mock_open.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_send_url_notification_no_url(self):
        """Test URL notification when no URL configured."""
        mock_config = MagicMock()
        mock_config.reminder.custom_url = None

        with patch("backend.scheduler.notifier.load_config", return_value=mock_config):
            result = await send_notification(
                "Test",
                "Body",
                [NotificationChannel.URL],
            )
            assert NotificationChannel.URL not in result

    @pytest.mark.asyncio
    async def test_default_channels(self):
        """Test default channel is system."""
        mock_notifier = MagicMock()
        mock_notifier.send = AsyncMock()

        with patch("backend.scheduler.notifier._get_notifier", return_value=mock_notifier):
            result = await send_notification("Test", "Body")
            assert NotificationChannel.SYSTEM in result

    @pytest.mark.asyncio
    async def test_system_notification_fallback_to_bell(self):
        """Test fallback to bell when system notification fails."""
        mock_notifier = MagicMock()
        mock_notifier.send = AsyncMock(side_effect=Exception("Failed"))

        with patch("backend.scheduler.notifier._get_notifier", return_value=mock_notifier):
            with patch("builtins.print"):
                result = await send_notification(
                    "Test",
                    "Body",
                    [NotificationChannel.SYSTEM],
                )
                # Should fallback to bell
                assert NotificationChannel.BELL in result
                assert NotificationChannel.SYSTEM not in result


class TestSendNotificationSync:
    """Test synchronous notification wrapper."""

    def test_send_notification_sync_new_loop(self):
        """Test sync notification with new event loop."""
        with patch("backend.scheduler.notifier.send_notification", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = [NotificationChannel.SYSTEM]
            send_notification_sync("Test", "Body")
            mock_send.assert_called()

    def test_send_notification_sync_running_loop(self):
        """Test sync notification with running event loop."""
        async def test_with_running_loop():
            with patch("backend.scheduler.notifier.send_notification", new_callable=AsyncMock) as mock_send:
                mock_send.return_value = [NotificationChannel.SYSTEM]
                send_notification_sync("Test", "Body")

        asyncio.run(test_with_running_loop())
