"""Image cache - loads all images into memory at startup for fast access."""

from __future__ import annotations

import logging
import os
from io import BytesIO
from typing import Dict, Optional

from bot.core.i18n import SUPPORTED_LOCALES, t

logger = logging.getLogger(__name__)

# Cache: {locale: {filename: bytes}}
_image_cache: Dict[str, Dict[str, bytes]] = {}

# Cache: {locale: {filename: file_id}}
_file_id_cache: Dict[str, Dict[str, str]] = {}


def _load_image_bytes(filepath: str) -> bytes:
    """Load image file into memory as bytes."""
    with open(filepath, "rb") as f:
        return f.read()


def _get_all_screen_images() -> Dict[str, list[str]]:
    """
    Get all screen image filenames from lang files.
    Returns: {locale: [filename1, filename2, ...]}
    """
    images = {}
    for locale in SUPPORTED_LOCALES:
        try:
            # Get all screen images from lang file
            screen_images = []
            # Collect all unique image filenames from screens
            screen_keys = ["main_menu", "buy_ticket", "my_tickets", "events", "club_info", "support", "add_music"]
            for screen_key in screen_keys:
                try:
                    img_filename = t(locale, f"screens.{screen_key}.image")
                    screen_images.append(img_filename)
                except Exception:
                    pass
            # Remove duplicates
            images[locale] = list(set(screen_images))
        except Exception as e:
            logger.warning(f"Failed to get images for locale {locale}: {e}")
            images[locale] = []
    return images


def preload_images() -> None:
    """
    Preload all images into memory cache.
    Should be called once at bot startup.
    """
    from bot.core.assets import get_locale_image_path

    logger.info("Preloading images into memory cache...")
    
    all_images = _get_all_screen_images()
    total_loaded = 0
    
    for locale, filenames in all_images.items():
        _image_cache[locale] = {}
        for filename in filenames:
            try:
                filepath = get_locale_image_path(locale, filename)
                if not os.path.exists(filepath):
                    logger.warning(f"Image not found: {filepath}")
                    continue
                image_bytes = _load_image_bytes(filepath)
                _image_cache[locale][filename] = image_bytes
                total_loaded += 1
                file_size_kb = len(image_bytes) / 1024
                logger.debug(f"Loaded {locale}/{filename} ({file_size_kb:.1f} KB)")
            except Exception as e:
                logger.error(f"Failed to load image {locale}/{filename}: {e}")
    
    total_size_mb = sum(
        sum(len(b) for b in images.values())
        for images in _image_cache.values()
    ) / (1024 * 1024)
    
    logger.info(f"Preloaded {total_loaded} images ({total_size_mb:.2f} MB total)")


def get_cached_image(locale: str, filename: str) -> Optional[BytesIO]:
    """
    Get cached image as BytesIO.
    Returns None if image not found in cache.
    """
    if locale not in _image_cache:
        return None
    
    if filename not in _image_cache[locale]:
        return None
    
    # Return BytesIO wrapper around cached bytes
    return BytesIO(_image_cache[locale][filename])


def get_cached_file_id(locale: str, filename: str) -> Optional[str]:
    """
    Get cached file_id for an image.
    """
    return _file_id_cache.get(locale, {}).get(filename)


def set_cached_file_id(locale: str, filename: str, file_id: str) -> None:
    """
    Set cached file_id for an image.
    """
    if locale not in _file_id_cache:
        _file_id_cache[locale] = {}
    
    if _file_id_cache[locale].get(filename) != file_id:
        _file_id_cache[locale][filename] = file_id
        logger.debug(f"Cached file_id for {locale}/{filename}: {file_id}")


def clear_cache() -> None:
    """Clear image cache (useful for testing or memory management)."""
    global _image_cache
    _image_cache.clear()
    logger.info("Image cache cleared")

