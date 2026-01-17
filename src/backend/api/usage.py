"""Anthropic Usage API client."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.settings import get_settings
from ..models.usage import UsageResponse
from ..utils.credentials import clear_credentials_cache, get_access_token


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class TokenExpiredError(Exception):
    """Raised when OAuth token is expired or invalid."""
    pass


@dataclass
class UsageCache:
    """Cache for usage API response."""

    data: UsageResponse | None
    timestamp: float
    token_expired: bool = False


_usage_cache: UsageCache | None = None


def _get_cache_duration() -> float:
    """Get cache duration in seconds."""
    return float(get_settings().cache_duration_seconds)


def _is_cache_valid() -> bool:
    """Check if cache is still valid."""
    if _usage_cache is None:
        return False
    return time.time() - _usage_cache.timestamp < _get_cache_duration()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def _fetch_usage_async(client: httpx.AsyncClient, token: str) -> UsageResponse | None:
    """Fetch usage from API with retry."""
    settings = get_settings()
    url = f"{settings.api_base_url}/api/oauth/usage"

    response = await client.get(
        url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "anthropic-beta": "oauth-2025-04-20",
            "User-Agent": "backend/0.1.0",
        },
        timeout=10.0,
    )

    if response.status_code == 401:
        logger.warning("Token expired or invalid")
        clear_credentials_cache()
        raise TokenExpiredError("OAuth token expired or invalid")

    if response.status_code == 429:
        logger.warning("Rate limit exceeded")
        raise RateLimitError("API rate limit exceeded")

    response.raise_for_status()
    return UsageResponse.model_validate(response.json())


async def get_usage_async() -> UsageResponse | None:
    """Get usage data (async), using cache if valid."""
    global _usage_cache

    if _is_cache_valid() and _usage_cache is not None:
        return _usage_cache.data

    token = get_access_token()
    if token is None:
        _usage_cache = UsageCache(data=None, timestamp=time.time(), token_expired=True)
        raise TokenExpiredError("No OAuth token available")

    try:
        async with httpx.AsyncClient() as client:
            data = await _fetch_usage_async(client, token)
            _usage_cache = UsageCache(data=data, timestamp=time.time(), token_expired=False)
            return data
    except TokenExpiredError:
        _usage_cache = UsageCache(data=None, timestamp=time.time(), token_expired=True)
        raise
    except RateLimitError:
        _usage_cache = UsageCache(data=None, timestamp=time.time())
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            _usage_cache = UsageCache(data=None, timestamp=time.time(), token_expired=True)
            raise TokenExpiredError("OAuth token expired or invalid") from e
        elif e.response.status_code == 429:
            _usage_cache = UsageCache(data=None, timestamp=time.time())
            raise RateLimitError("API rate limit exceeded") from e
        else:
            _usage_cache = UsageCache(data=None, timestamp=time.time())
            logger.error(f"HTTP error fetching usage: {e}")
            raise
    except Exception as e:
        _usage_cache = UsageCache(data=None, timestamp=time.time())
        logger.error(f"Error fetching usage: {e}")
        raise


def get_usage_sync() -> UsageResponse | None:
    """Get usage data (sync), using cache if valid."""
    global _usage_cache

    if _is_cache_valid() and _usage_cache is not None:
        return _usage_cache.data

    token = get_access_token()
    if token is None:
        _usage_cache = UsageCache(data=None, timestamp=time.time(), token_expired=True)
        return None

    settings = get_settings()
    url = f"{settings.api_base_url}/api/oauth/usage"

    try:
        with httpx.Client() as client:
            response = client.get(
                url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                    "anthropic-beta": "oauth-2025-04-20",
                    "User-Agent": "backend/0.1.0",
                },
                timeout=10.0,
            )

            if response.status_code == 401:
                logger.warning("Token expired or invalid")
                clear_credentials_cache()
                _usage_cache = UsageCache(data=None, timestamp=time.time(), token_expired=True)
                return None

            response.raise_for_status()
            data = UsageResponse.model_validate(response.json())
            _usage_cache = UsageCache(data=data, timestamp=time.time(), token_expired=False)
            return data

    except Exception as e:
        _usage_cache = UsageCache(data=None, timestamp=time.time())
        logger.error(f"Error fetching usage: {e}")
        return None


def clear_usage_cache() -> None:
    """Clear usage cache."""
    global _usage_cache
    _usage_cache = None


def is_token_expired() -> bool:
    """Check if token is known to be expired."""
    return _usage_cache is not None and _usage_cache.token_expired


class UsageAPI:
    """Usage API client class for TUI/GUI integration."""

    async def get_usage(self) -> UsageResponse:
        """Get usage data asynchronously.

        Returns:
            UsageResponse with usage data

        Raises:
            RuntimeError: If no token or failed to fetch
        """
        result = await get_usage_async()
        if result is None:
            if is_token_expired():
                raise RuntimeError("Token expired. Please re-login to Claude.")
            raise RuntimeError("Failed to fetch usage data")
        return result

    def get_usage_sync_wrapped(self) -> UsageResponse:
        """Get usage data synchronously.

        Returns:
            UsageResponse with usage data

        Raises:
            RuntimeError: If no token or failed to fetch
        """
        result = get_usage_sync()
        if result is None:
            if is_token_expired():
                raise RuntimeError("Token expired. Please re-login to Claude.")
            raise RuntimeError("Failed to fetch usage data")
        return result
