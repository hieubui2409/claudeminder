"""Multi-channel notification system."""
import subprocess
import webbrowser
from enum import Enum
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from desktop_notifier import DesktopNotifier

from ..core.config_manager import load_config


class NotificationChannel(Enum):
    """Available notification channels."""
    SYSTEM = "system"
    BELL = "bell"
    COMMAND = "command"
    URL = "url"


_notifier: "DesktopNotifier | None" = None


def _get_notifier() -> "DesktopNotifier":
    """Get or create desktop notifier instance."""
    global _notifier
    if _notifier is None:
        from desktop_notifier import DesktopNotifier
        _notifier = DesktopNotifier(app_name="Claudiminder")
    return _notifier


async def send_notification(
    title: str,
    body: str,
    channels: list[NotificationChannel] | None = None,
) -> list[NotificationChannel]:
    """Send notification through configured channels.

    Args:
        title: Notification title
        body: Notification body text
        channels: Specific channels to use, or None for all configured

    Returns:
        List of channels that successfully sent
    """
    config = load_config()
    sent_channels: list[NotificationChannel] = []

    # Default to system notification
    if channels is None:
        channels = [NotificationChannel.SYSTEM]

    for channel in channels:
        try:
            if channel == NotificationChannel.SYSTEM:
                notifier = _get_notifier()
                await notifier.send(title=title, message=body)
                sent_channels.append(channel)
                logger.debug(f"System notification sent: {title}")

            elif channel == NotificationChannel.BELL:
                print("\a", end="", flush=True)
                sent_channels.append(channel)
                logger.debug("Terminal bell sent")

            elif channel == NotificationChannel.COMMAND:
                if config.reminder.custom_command:
                    subprocess.Popen(
                        config.reminder.custom_command,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    sent_channels.append(channel)
                    logger.debug(f"Custom command executed: {config.reminder.custom_command}")

            elif channel == NotificationChannel.URL:
                if config.reminder.custom_url:
                    webbrowser.open(config.reminder.custom_url)
                    sent_channels.append(channel)
                    logger.debug(f"URL opened: {config.reminder.custom_url}")

        except Exception as e:
            logger.warning(f"Failed to send {channel.value} notification: {e}")
            # Try fallback to bell on system notification failure
            if channel == NotificationChannel.SYSTEM and NotificationChannel.BELL not in sent_channels:
                try:
                    print("\a", end="", flush=True)
                    sent_channels.append(NotificationChannel.BELL)
                except Exception:
                    pass

    return sent_channels


def send_notification_sync(title: str, body: str) -> None:
    """Synchronous wrapper for send_notification (system + bell fallback)."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(send_notification(title, body))
        else:
            loop.run_until_complete(send_notification(title, body))
    except RuntimeError:
        asyncio.run(send_notification(title, body))
