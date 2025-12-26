"""Simple JSON-based i18n."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Mapping, Optional


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def _parse_locales(value: str) -> tuple[str, ...]:
    parts = [p.strip().lower().replace("-", "_") for p in value.split(",") if p.strip()]
    # de-duplicate preserving order
    seen = set()
    out: list[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return tuple(out)


SUPPORTED_LOCALES = _parse_locales(_env("I18N_SUPPORTED_LOCALES", "ru_ru,en_us"))
DEFAULT_LOCALE = _env("I18N_DEFAULT_LOCALE", "ru_ru").lower().replace("-", "_")

if DEFAULT_LOCALE not in SUPPORTED_LOCALES:
    DEFAULT_LOCALE = SUPPORTED_LOCALES[0] if SUPPORTED_LOCALES else "ru_ru"


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
    if code.startswith("ru") and "ru_ru" in SUPPORTED_LOCALES:
        return "ru_ru"
    if code.startswith("en") and "en_us" in SUPPORTED_LOCALES:
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


def t(locale: str, key: str, default: str = None, **kwargs: Any) -> str:
    """
    Translate by key (dot-path). Falls back to DEFAULT_LOCALE, then to default value.
    Supports `.format(**kwargs)` placeholders.
    """
    try:
        template = _deep_get(_load_locale(locale), key)
    except KeyError:
        try:
            template = _deep_get(_load_locale(DEFAULT_LOCALE), key)
        except KeyError:
            if default is not None:
                template = default
            else:
                raise KeyError(key)

    if not isinstance(template, str):
        raise TypeError(f"i18n key {key} must be a string")
    return template.format(**kwargs) if kwargs else template


