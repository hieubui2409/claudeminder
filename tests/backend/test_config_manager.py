"""Tests for config manager module."""
import pytest
from pathlib import Path
import tempfile
import os

from backend.core.config_manager import (
    AppConfig,
    ReminderConfig,
    FocusModeConfig,
    GoalsConfig,
    load_config,
    save_config,
    CONFIG_DIR,
    CONFIG_FILE,
)


class TestConfigModels:
    """Test configuration Pydantic models."""

    def test_reminder_config_defaults(self):
        """Test ReminderConfig has correct defaults."""
        config = ReminderConfig()
        assert config.enabled is True
        assert config.before_reset_minutes == [15, 30, 60]
        assert config.on_reset is True
        assert config.percentage_thresholds == [50, 75, 90, 100]
        assert config.snooze_minutes == [5, 15, 30]
        assert config.custom_command is None
        assert config.custom_url is None

    def test_focus_mode_config_defaults(self):
        """Test FocusModeConfig has correct defaults."""
        config = FocusModeConfig()
        assert config.enabled is False
        assert config.dnd_threshold == 80
        assert config.quiet_hours_start is None
        assert config.quiet_hours_end is None

    def test_goals_config_defaults(self):
        """Test GoalsConfig has correct defaults."""
        config = GoalsConfig()
        assert config.enabled is False
        assert config.daily_budget_percent == 100
        assert config.warn_when_pace_exceeded is True

    def test_app_config_defaults(self):
        """Test AppConfig has correct defaults."""
        config = AppConfig()
        assert config.language == "en"
        assert config.log_level == "INFO"
        assert config.poll_interval_seconds == 60
        assert isinstance(config.reminder, ReminderConfig)
        assert isinstance(config.focus_mode, FocusModeConfig)
        assert isinstance(config.goals, GoalsConfig)

    def test_app_config_custom_values(self):
        """Test AppConfig with custom values."""
        config = AppConfig(
            language="vi",
            log_level="DEBUG",
            poll_interval_seconds=30,
            reminder=ReminderConfig(enabled=False),
            focus_mode=FocusModeConfig(enabled=True, dnd_threshold=90),
            goals=GoalsConfig(enabled=True, daily_budget_percent=80),
        )
        assert config.language == "vi"
        assert config.log_level == "DEBUG"
        assert config.poll_interval_seconds == 30
        assert config.reminder.enabled is False
        assert config.focus_mode.enabled is True
        assert config.focus_mode.dnd_threshold == 90
        assert config.goals.enabled is True
        assert config.goals.daily_budget_percent == 80


class TestConfigIO:
    """Test config file I/O operations."""

    def test_load_config_no_file(self, monkeypatch, tmp_path):
        """Test loading config when file doesn't exist returns defaults."""
        # Point to non-existent file
        fake_config = tmp_path / "nonexistent" / "config.toml"
        monkeypatch.setattr("backend.core.config_manager.CONFIG_FILE", fake_config)

        config = load_config()
        assert isinstance(config, AppConfig)
        assert config.language == "en"

    def test_save_and_load_config(self, monkeypatch, tmp_path):
        """Test saving and loading config round-trip."""
        fake_dir = tmp_path / "backend"
        fake_file = fake_dir / "config.toml"
        monkeypatch.setattr("backend.core.config_manager.CONFIG_DIR", fake_dir)
        monkeypatch.setattr("backend.core.config_manager.CONFIG_FILE", fake_file)

        # Create and save config
        original = AppConfig(
            language="vi",
            poll_interval_seconds=120,
            focus_mode=FocusModeConfig(enabled=True),
        )
        save_config(original)

        # Verify file exists
        assert fake_file.exists()

        # Load and verify
        loaded = load_config()
        assert loaded.language == "vi"
        assert loaded.poll_interval_seconds == 120
        assert loaded.focus_mode.enabled is True
