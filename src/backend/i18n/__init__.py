"""Internationalization module for Claudiminder."""
from .en import STRINGS as EN_STRINGS
from .vi import STRINGS as VI_STRINGS

_current_language = "en"

LANGUAGES = {
    "en": EN_STRINGS,
    "vi": VI_STRINGS,
}


def set_language(lang: str) -> None:
    """Set current language (en or vi)."""
    global _current_language
    if lang not in LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}. Available: {list(LANGUAGES.keys())}")
    _current_language = lang


def get_language() -> str:
    """Get current language code."""
    return _current_language


def get_string(key: str, **kwargs: str | int | float) -> str:
    """Get localized string by key with optional formatting."""
    strings = LANGUAGES.get(_current_language, EN_STRINGS)
    template = strings.get(key, EN_STRINGS.get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template


def get_all_strings() -> dict[str, str]:
    """Get all strings for current language."""
    return LANGUAGES.get(_current_language, EN_STRINGS).copy()


__all__ = [
    "set_language",
    "get_language",
    "get_string",
    "get_all_strings",
    "LANGUAGES",
]
