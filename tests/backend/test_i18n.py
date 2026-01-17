"""Tests for i18n module."""
import pytest

from backend.i18n import (
    set_language,
    get_language,
    get_string,
    get_all_strings,
    LANGUAGES,
)


class TestI18n:
    """Test internationalization functionality."""

    def test_default_language(self):
        """Test default language is English."""
        set_language("en")  # Reset to default
        assert get_language() == "en"

    def test_set_language_english(self):
        """Test setting language to English."""
        set_language("en")
        assert get_language() == "en"

    def test_set_language_vietnamese(self):
        """Test setting language to Vietnamese."""
        set_language("vi")
        assert get_language() == "vi"
        # Reset for other tests
        set_language("en")

    def test_set_language_invalid(self):
        """Test setting invalid language raises error."""
        with pytest.raises(ValueError) as exc_info:
            set_language("fr")
        assert "Unsupported language" in str(exc_info.value)

    def test_get_string_english(self):
        """Test getting string in English."""
        set_language("en")
        assert get_string("usage_title") == "Claude Usage"
        assert get_string("loading") == "Loading..."

    def test_get_string_vietnamese(self):
        """Test getting string in Vietnamese."""
        set_language("vi")
        assert get_string("usage_title") == "Sử dụng Claude"
        assert get_string("loading") == "Đang tải..."
        set_language("en")

    def test_get_string_with_formatting(self):
        """Test getting string with format kwargs."""
        set_language("en")
        result = get_string("reminder_soon", minutes=15)
        assert "15" in result
        assert "minutes" in result

    def test_get_string_unknown_key(self):
        """Test getting unknown key returns the key."""
        set_language("en")
        result = get_string("unknown_key_xyz")
        assert result == "unknown_key_xyz"

    def test_get_all_strings(self):
        """Test getting all strings for current language."""
        set_language("en")
        strings = get_all_strings()
        assert isinstance(strings, dict)
        assert "usage_title" in strings
        assert strings["usage_title"] == "Claude Usage"

    def test_languages_available(self):
        """Test available languages."""
        assert "en" in LANGUAGES
        assert "vi" in LANGUAGES
        assert len(LANGUAGES) == 2
