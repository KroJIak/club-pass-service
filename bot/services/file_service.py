"""File service for downloading and saving photos from Telegram."""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Tuple
from aiogram import Bot

logger = logging.getLogger(__name__)

SUPPORT_PHOTOS_DIR = "uploads/support_photos"


def ensure_upload_directory() -> str:
    """Ensure upload directory exists. Returns the directory path."""
    upload_dir = os.path.join(os.getcwd(), SUPPORT_PHOTOS_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def _get_extension_from_mime_type(mime_type: str) -> str:
    """Get file extension from MIME type."""
    mime_to_ext = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
    }
    return mime_to_ext.get(mime_type.lower(), '.jpg')


async def download_and_save_photo(bot: Bot, file_id: str) -> Optional[str]:
    """
    Download photo from Telegram and save it locally.
    
    Args:
        bot: Bot instance
        file_id: Telegram file_id
        
    Returns:
        Relative file path from project root (e.g., "uploads/support_photos/uuid.jpg") or None if error
    """
    try:
        # Get file info
        file = await bot.get_file(file_id)
        if not file:
            logger.error(f"Failed to get file info for file_id: {file_id}")
            return None
        
        # Download file
        file_content = await bot.download_file(file.file_path)
        if not file_content:
            logger.error(f"Failed to download file: {file_id}")
            return None
        
        # Read file content
        file_bytes = await file_content.read()
        
        # Determine MIME type from file path
        file_path = file.file_path or ""
        mime_type = "image/jpeg"  # Default
        if file_path.endswith(".png"):
            mime_type = "image/png"
        elif file_path.endswith(".gif"):
            mime_type = "image/gif"
        elif file_path.endswith(".webp"):
            mime_type = "image/webp"
        
        # Generate unique filename
        file_ext = _get_extension_from_mime_type(mime_type)
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Ensure directory exists
        upload_dir = ensure_upload_directory()
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        # Return relative path
        relative_path = os.path.join(SUPPORT_PHOTOS_DIR, unique_filename)
        logger.info(f"Downloaded and saved photo: {relative_path} ({len(file_bytes)} bytes)")
        return relative_path
        
    except Exception as e:
        logger.error(f"Error downloading and saving photo {file_id}: {e}", exc_info=True)
        return None

