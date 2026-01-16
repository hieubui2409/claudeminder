"""Credentials management for Claude OAuth."""

from __future__ import annotations

import json
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field, SecretStr

from ..models.settings import get_settings


class OAuthCredentials(BaseModel):
    """OAuth credentials from Claude."""

    access_token: SecretStr = Field(..., description="OAuth access token")
    refresh_token: SecretStr | None = Field(None, description="OAuth refresh token")
    expires_at: int | None = Field(None, description="Token expiration timestamp")
    subscription_type: str | None = Field(None, description="Subscription type")
    rate_limit_tier: str | None = Field(None, description="Rate limit tier")


class CredentialsFile(BaseModel):
    """Structure of ~/.claude/.credentials.json."""

    claudeAiOauth: OAuthCredentials | None = Field(None, description="OAuth credentials")


_credentials_cache: OAuthCredentials | None = None


def get_credentials_path() -> Path:
    """Get path to credentials file."""
    return get_settings().credentials_path


def load_credentials() -> OAuthCredentials | None:
    """Load OAuth credentials from file."""
    global _credentials_cache

    if _credentials_cache is not None:
        return _credentials_cache

    path = get_credentials_path()

    if not path.exists():
        logger.warning(f"Credentials file not found: {path}")
        return None

    try:
        content = path.read_text()
        data = json.loads(content)
        creds_file = CredentialsFile.model_validate(data)

        if creds_file.claudeAiOauth is None:
            logger.warning("No OAuth credentials in file")
            return None

        _credentials_cache = creds_file.claudeAiOauth
        return _credentials_cache

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in credentials file: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        return None


def get_access_token() -> str | None:
    """Get access token from credentials."""
    creds = load_credentials()
    if creds is None:
        return None
    return creds.access_token.get_secret_value()


def clear_credentials_cache() -> None:
    """Clear cached credentials."""
    global _credentials_cache
    _credentials_cache = None


def is_token_available() -> bool:
    """Check if OAuth token is available."""
    return get_access_token() is not None
