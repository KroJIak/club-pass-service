"""Asset path helpers (images, etc.)."""

from __future__ import annotations

import os


def get_locale_image_path(locale: str, filename: str) -> str:
    """
    Build an absolute path to an image located under:
      bot/assets/images/{locale}/{filename}
    """
    base = os.path.join(os.path.dirname(__file__), "..", "assets", "images", locale)
    return os.path.abspath(os.path.join(base, filename))


