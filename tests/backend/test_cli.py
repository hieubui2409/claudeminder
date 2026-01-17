"""Tests for CLI commands."""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from backend.cli import app, setup_logging


runner = CliRunner()


class TestSetupLogging:
    """Test logging setup."""

    def test_setup_logging_info_level(self):
        """Test logging setup with INFO level."""
        setup_logging(debug=False)

    def test_setup_logging_debug_level(self):
        """Test logging setup with DEBUG level."""
        setup_logging(debug=True)


class TestStatusCommand:
    """Test status command."""

    def test_status_no_token(self):
        """Test status when no token available."""
        with patch("backend.cli.is_token_available", return_value=False):
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 1
            assert "No OAuth token" in result.output

    def test_status_fetch_failed(self):
        """Test status when usage fetch fails."""
        with patch("backend.cli.is_token_available", return_value=True):
            with patch("backend.cli.get_usage_sync", return_value=None):
                with patch("backend.cli.is_token_expired", return_value=False):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 1
                    assert "Failed to fetch" in result.output

    def test_status_token_expired(self):
        """Test status when token expired."""
        with patch("backend.cli.is_token_available", return_value=True):
            with patch("backend.cli.get_usage_sync", return_value=None):
                with patch("backend.cli.is_token_expired", return_value=True):
                    result = runner.invoke(app, ["status"])
                    assert result.exit_code == 1
                    # Could be either text or JSON depending on flag
                    assert "expired" in result.output.lower() or "error" in result.output.lower()

    def test_status_success(self):
        """Test successful status."""
        from backend.models.usage import FiveHourUsage, UsageResponse

        mock_usage = UsageResponse(
            five_hour=FiveHourUsage(utilization=0.75, resets_at="2024-01-17T12:00:00Z")
        )
        with patch("backend.cli.is_token_available", return_value=True):
            with patch("backend.cli.get_usage_sync", return_value=mock_usage):
                result = runner.invoke(app, ["status"])
                assert result.exit_code == 0
                # Either percentage or JSON with utilization
                assert "75" in result.output or "0.75" in result.output

    def test_status_no_five_hour_data(self):
        """Test status when no five_hour data."""
        from backend.models.usage import UsageResponse

        mock_usage = UsageResponse(five_hour=None)
        with patch("backend.cli.is_token_available", return_value=True):
            with patch("backend.cli.get_usage_sync", return_value=mock_usage):
                result = runner.invoke(app, ["status"])
                assert result.exit_code == 0
                # Either text message or JSON with null
                assert "No usage data" in result.output or "null" in result.output


class TestVersionCommand:
    """Test version command."""

    def test_version(self):
        """Test version output."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "backend" in result.output


class TestMain:
    """Test main entry point."""

    def test_main_function_exists(self):
        """Test main function can be imported."""
        from backend.cli import main
        assert callable(main)
