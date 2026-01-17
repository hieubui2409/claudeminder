"""Tests for API usage module."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend.api.usage import (
    RateLimitError,
    TokenExpiredError,
    UsageAPI,
    UsageCache,
    clear_usage_cache,
    get_usage_async,
    get_usage_sync,
    is_token_expired,
)
from backend.models.usage import UsageResponse


class TestGetUsageAsync:
    """Tests for get_usage_async function."""

    @pytest.mark.asyncio
    async def test_returns_cached_data_when_valid(
        self,
        mock_usage_response: UsageResponse,
    ):
        """Test cached data is returned when still valid."""
        with patch("backend.api.usage._usage_cache") as mock_cache:
            mock_cache.data = mock_usage_response
            mock_cache.timestamp = 9999999999  # Far future
            mock_cache.token_expired = False

            with patch("backend.api.usage._is_cache_valid", return_value=True):
                result = await get_usage_async()
                assert result == mock_usage_response

    @pytest.mark.asyncio
    async def test_raises_token_expired_when_no_token(self):
        """Test TokenExpiredError when no token available."""
        with patch("backend.api.usage.get_access_token", return_value=None):
            with pytest.raises(TokenExpiredError, match="No OAuth token"):
                await get_usage_async()

    @pytest.mark.asyncio
    async def test_fetches_fresh_data_when_cache_invalid(
        self,
        mock_usage_json: dict[str, Any],
    ):
        """Test fetches fresh data when cache is invalid."""
        clear_usage_cache()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_usage_json

        with patch("backend.api.usage.get_access_token", return_value="test-token"):
            with patch("backend.api.usage.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_instance

                result = await get_usage_async()

                assert result is not None
                assert result.five_hour is not None
                assert result.five_hour.utilization == 0.45

    @pytest.mark.asyncio
    async def test_raises_token_expired_on_401(self):
        """Test TokenExpiredError on 401 response."""
        with patch("backend.api.usage.get_access_token", return_value="test-token"):
            with patch(
                "backend.api.usage._fetch_usage_async",
                new_callable=AsyncMock,
                side_effect=TokenExpiredError("Token expired"),
            ):
                with pytest.raises(TokenExpiredError):
                    await get_usage_async()

    @pytest.mark.asyncio
    async def test_raises_rate_limit_on_429(self):
        """Test RateLimitError on 429 response."""
        with patch("backend.api.usage.get_access_token", return_value="test-token"):
            with patch(
                "backend.api.usage._fetch_usage_async",
                new_callable=AsyncMock,
                side_effect=RateLimitError("Rate limited"),
            ):
                with pytest.raises(RateLimitError):
                    await get_usage_async()


class TestGetUsageSync:
    """Tests for get_usage_sync function."""

    def test_returns_none_when_no_token(self):
        """Test returns None when no token available."""
        with patch("backend.api.usage.get_access_token", return_value=None):
            result = get_usage_sync()
            assert result is None

    def test_returns_cached_data_when_valid(
        self,
        mock_usage_response: UsageResponse,
    ):
        """Test cached data is returned when still valid."""
        with patch("backend.api.usage._usage_cache") as mock_cache:
            mock_cache.data = mock_usage_response
            mock_cache.timestamp = 9999999999

            with patch("backend.api.usage._is_cache_valid", return_value=True):
                result = get_usage_sync()
                assert result == mock_usage_response

    def test_returns_none_on_401(self):
        """Test returns None on 401 response."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("backend.api.usage.get_access_token", return_value="test-token"):
            with patch("backend.api.usage.httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.get.return_value = mock_response
                mock_client.return_value.__enter__.return_value = mock_instance

                result = get_usage_sync()
                assert result is None
                assert is_token_expired() is True

    def test_returns_none_on_http_error(self):
        """Test returns None on HTTP error."""
        with patch("backend.api.usage.get_access_token", return_value="test-token"):
            with patch("backend.api.usage.httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.get.side_effect = httpx.HTTPError("Network error")
                mock_client.return_value.__enter__.return_value = mock_instance

                result = get_usage_sync()
                assert result is None


class TestUsageCache:
    """Tests for UsageCache class."""

    def test_cache_creation(self, mock_usage_response: UsageResponse):
        """Test cache creation with data."""
        cache = UsageCache(
            data=mock_usage_response,
            timestamp=1234567890.0,
            token_expired=False,
        )
        assert cache.data == mock_usage_response
        assert cache.timestamp == 1234567890.0
        assert cache.token_expired is False

    def test_cache_with_token_expired(self):
        """Test cache with token expired flag."""
        cache = UsageCache(
            data=None,
            timestamp=1234567890.0,
            token_expired=True,
        )
        assert cache.data is None
        assert cache.token_expired is True


class TestIsTokenExpired:
    """Tests for is_token_expired function."""

    def test_returns_false_when_no_cache(self):
        """Test returns False when no cache exists."""
        clear_usage_cache()
        assert is_token_expired() is False

    def test_returns_true_when_token_expired_in_cache(self):
        """Test returns True when token is expired in cache."""
        import backend.api.usage as usage_module

        usage_module._usage_cache = UsageCache(
            data=None,
            timestamp=1234567890.0,
            token_expired=True,
        )
        assert is_token_expired() is True


class TestUsageAPI:
    """Tests for UsageAPI class."""

    @pytest.mark.asyncio
    async def test_get_usage_success(self, mock_usage_response: UsageResponse):
        """Test successful usage fetch."""
        api = UsageAPI()

        with patch(
            "backend.api.usage.get_usage_async",
            new_callable=AsyncMock,
            return_value=mock_usage_response,
        ):
            result = await api.get_usage()
            assert result == mock_usage_response

    @pytest.mark.asyncio
    async def test_get_usage_raises_on_token_expired(self):
        """Test raises RuntimeError on token expiry."""
        api = UsageAPI()

        with patch(
            "backend.api.usage.get_usage_async",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with patch("backend.api.usage.is_token_expired", return_value=True):
                with pytest.raises(RuntimeError, match="Token expired"):
                    await api.get_usage()

    def test_get_usage_sync_wrapped_success(self, mock_usage_response: UsageResponse):
        """Test successful sync usage fetch."""
        api = UsageAPI()

        with patch(
            "backend.api.usage.get_usage_sync",
            return_value=mock_usage_response,
        ):
            result = api.get_usage_sync_wrapped()
            assert result == mock_usage_response

    def test_get_usage_sync_wrapped_raises_on_failure(self):
        """Test raises RuntimeError on failure."""
        api = UsageAPI()

        with patch("backend.api.usage.get_usage_sync", return_value=None):
            with patch("backend.api.usage.is_token_expired", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to fetch"):
                    api.get_usage_sync_wrapped()
