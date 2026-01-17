"""Tests for instance lock module."""
import pytest
from pathlib import Path

from backend.core.instance_lock import (
    acquire_instance_lock,
    release_instance_lock,
    is_another_instance_running,
)


class TestInstanceLock:
    """Test single instance lock functionality."""

    def test_acquire_lock_success(self, monkeypatch, tmp_path):
        """Test acquiring lock when no other instance."""
        fake_lock = tmp_path / ".lock"
        monkeypatch.setattr("backend.core.instance_lock.LOCK_FILE", fake_lock)
        # Reset global state
        monkeypatch.setattr("backend.core.instance_lock._current_lock", None)

        lock = acquire_instance_lock()
        assert lock is not None

        # Clean up
        release_instance_lock()

    def test_is_another_instance_running_false(self, monkeypatch, tmp_path):
        """Test detecting no other instance running."""
        fake_lock = tmp_path / ".lock"
        monkeypatch.setattr("backend.core.instance_lock.LOCK_FILE", fake_lock)

        result = is_another_instance_running()
        assert result is False

    def test_release_lock(self, monkeypatch, tmp_path):
        """Test releasing acquired lock."""
        fake_lock = tmp_path / ".lock"
        monkeypatch.setattr("backend.core.instance_lock.LOCK_FILE", fake_lock)
        monkeypatch.setattr("backend.core.instance_lock._current_lock", None)

        # Acquire first
        lock = acquire_instance_lock()
        assert lock is not None

        # Release
        release_instance_lock()

        # Should be able to acquire again
        assert is_another_instance_running() is False
