"""English language strings."""

STRINGS: dict[str, str] = {
    # General
    "app_name": "Claudiminder",
    "usage_title": "Claude Usage",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",

    # Reset countdown
    "reset_in": "Reset in",
    "reset_complete": "Reset complete!",
    "hours": "hours",
    "minutes": "minutes",
    "seconds": "seconds",

    # Offline mode
    "offline_mode": "Offline - showing cached data",
    "connection_restored": "Connection restored",

    # Reminders
    "reminder_soon": "Token reset in {minutes} minutes!",
    "reminder_reset": "Your token has reset!",
    "reminder_threshold": "Usage reached {percent}%",
    "reminder_snoozed": "Reminder snoozed for {minutes} minutes",

    # Goals & Pace
    "pace_ok": "On track",
    "pace_exceeded": "Using too fast!",
    "budget_used": "Budget: {used}% of {total}%",
    "daily_goal": "Daily Goal",

    # Focus mode
    "focus_mode_active": "Focus mode active",
    "quiet_hours_active": "Quiet hours active",
    "dnd_active": "Do Not Disturb active (usage > {threshold}%)",

    # TUI
    "press_q_quit": "Press 'q' to quit",
    "press_r_refresh": "Press 'r' to refresh",
    "press_h_help": "Press 'h' for help",
    "refreshing": "Refreshing...",
    "last_updated": "Last updated: {time}",

    # Usage metrics
    "five_hour_usage": "5-Hour Usage",
    "seven_day_usage": "7-Day Usage",
    "extra_usage": "Extra Usage",
    "utilization": "Utilization",
}
