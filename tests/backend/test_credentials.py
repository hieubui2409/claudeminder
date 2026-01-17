"""Tests for credentials module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.utils.credentials import (
    CredentialsFile,
    OAuthCredentials,
    clear_credentials_cache,
    get_access_token,
    get_credentials_path,
    is_token_available,
    load_credentials,
)


class TestOAuthCredentials:
    """Tests for OAuthCredentials model."""

    def test_create_minimal(self):
        """Test creating with only required fields."""
        creds = OAuthCredentials(access_token="test-token")
        assert creds.access_token.get_secret_value() == "test-token"
        assert creds.refresh_token is None
        assert creds.expires_at is None

    def test_create_full(self):
        """Test creating with all fields."""
        creds = OAuthCredentials(
            access_token="test-token",
            refresh_token="refresh-token",
            expires_at=1234567890,
            subscription_type="pro",
            rate_limit_tier="tier1",
        )
        assert creds.access_token.get_secret_value() == "test-token"
        assert creds.refresh_token is not None
        assert creds.refresh_token.get_secret_value() == "refresh-token"
        assert creds.expires_at == 1234567890
        assert creds.subscription_type == "pro"
        assert creds.rate_limit_tier == "tier1"

    def test_secret_str_hidden(self):
        """Test that SecretStr hides token in repr."""
        creds = OAuthCredentials(access_token="secret-value")
        repr_str = repr(creds.access_token)
        assert "secret-value" not in repr_str
        assert "**********" in repr_str


class TestCredentialsFile:
    """Tests for CredentialsFile model."""

    def test_empty_file(self):
        """Test parsing empty credentials file."""
        creds_file = CredentialsFile.model_validate({})
        assert creds_file.claudeAiOauth is None

    def test_with_oauth(self):
        """Test parsing file with OAuth credentials."""
        data = {
            "claudeAiOauth": {
                "access_token": "test-token",
                "subscription_type": "pro",
            }
        }
        creds_file = CredentialsFile.model_validate(data)
        assert creds_file.claudeAiOauth is not None
        assert creds_file.claudeAiOauth.access_token.get_secret_value() == "test-token"


class TestLoadCredentials:
    """Tests for load_credentials function."""

    def test_returns_none_when_file_missing(self, tmp_path: Path):
        """Test returns None when file doesn't exist."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=tmp_path / "nonexistent.json",
        ):
            result = load_credentials()
            assert result is None

    def test_loads_valid_credentials(self, mock_credentials_file: Path):
        """Test loads valid credentials from file."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=mock_credentials_file,
        ):
            result = load_credentials()
            assert result is not None
            assert result.access_token.get_secret_value() == "test-token-12345"

    def test_returns_none_for_empty_oauth(self, mock_empty_credentials_file: Path):
        """Test returns None when no OAuth in file."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=mock_empty_credentials_file,
        ):
            result = load_credentials()
            assert result is None

    def test_returns_none_for_invalid_json(self, tmp_path: Path):
        """Test returns None for invalid JSON."""
        clear_credentials_cache()
        invalid_file = tmp_path / ".credentials.json"
        invalid_file.write_text("not valid json{")

        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=invalid_file,
        ):
            result = load_credentials()
            assert result is None

    def test_uses_cache_on_second_call(self, mock_credentials_file: Path):
        """Test uses cache on second call."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=mock_credentials_file,
        ):
            result1 = load_credentials()
            result2 = load_credentials()
            assert result1 is result2


class TestGetAccessToken:
    """Tests for get_access_token function."""

    def test_returns_token_when_available(self, mock_credentials_file: Path):
        """Test returns token when credentials available."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=mock_credentials_file,
        ):
            token = get_access_token()
            assert token == "test-token-12345"

    def test_returns_none_when_no_credentials(self, tmp_path: Path):
        """Test returns None when no credentials."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=tmp_path / "nonexistent.json",
        ):
            token = get_access_token()
            assert token is None


class TestIsTokenAvailable:
    """Tests for is_token_available function."""

    def test_returns_true_when_token_exists(self, mock_credentials_file: Path):
        """Test returns True when token exists."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=mock_credentials_file,
        ):
            assert is_token_available() is True

    def test_returns_false_when_no_token(self, tmp_path: Path):
        """Test returns False when no token."""
        clear_credentials_cache()
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=tmp_path / "nonexistent.json",
        ):
            assert is_token_available() is False


class TestClearCredentialsCache:
    """Tests for clear_credentials_cache function."""

    def test_clears_cache(self, mock_credentials_file: Path):
        """Test cache is cleared."""
        with patch(
            "backend.utils.credentials.get_credentials_path",
            return_value=mock_credentials_file,
        ):
            load_credentials()  # Load into cache
            clear_credentials_cache()

            # Modify file
            mock_credentials_file.write_text(
                json.dumps(
                    {
                        "claudeAiOauth": {
                            "access_token": "new-token",
                        }
                    }
                )
            )

            result = load_credentials()
            assert result is not None
            assert result.access_token.get_secret_value() == "new-token"
