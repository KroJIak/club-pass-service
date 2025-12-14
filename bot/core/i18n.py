"""Simple JSON-based i18n."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Mapping, Optional


SUPPORTED_LOCALES = ("ru_ru", "en_us")
DEFAULT_LOCALE = "en_us"


def _normalize_language_code(language_code: Optional[str]) -> str:
    if not language_code:
        return ""
    return language_code.strip().lower().replace("-", "_")


def get_user_locale(language_code: Optional[str]) -> str:
    """
    Resolve locale from Telegram `from_user.language_code`.

    Telegram examples: "ru", "en", "en-US", "ru-RU".
    """
    code = _normalize_language_code(language_code)
    if code.startswith("ru"):
        return "ru_ru"
    if code.startswith("en"):
        return "en_us"
    return DEFAULT_LOCALE


def _deep_get(data: Mapping[str, Any], key: str) -> Any:
    cur: Any = data
    for part in key.split("."):
        if not isinstance(cur, Mapping) or part not in cur:
            raise KeyError(key)
        cur = cur[part]
    return cur


@lru_cache(maxsize=16)
def _load_locale(locale: str) -> dict[str, Any]:
    locale = locale.lower()
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE
    base_dir = os.path.join(os.path.dirname(__file__), "..", "lang")
    path = os.path.join(base_dir, f"{locale}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def t(locale: str, key: str, **kwargs: Any) -> str:
    """
    Translate by key (dot-path). Falls back to DEFAULT_LOCALE.
    Supports `.format(**kwargs)` placeholders.
    """
    try:
        template = _deep_get(_load_locale(locale), key)
    except KeyError:
        template = _deep_get(_load_locale(DEFAULT_LOCALE), key)

    if not isinstance(template, str):
        raise TypeError(f"i18n key {key} must be a string")
    return template.format(**kwargs) if kwargs else template


