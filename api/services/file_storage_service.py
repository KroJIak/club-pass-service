"""File storage service for support photos."""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from api.core.config import settings

logger = logging.getLogger(__name__)


def ensure_upload_directory() -> str:
    """Ensure upload directory exists. Returns the directory path."""
    upload_dir = os.path.join(os.getcwd(), settings.SUPPORT_PHOTOS_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def save_support_photo(file_content: bytes, filename: str, mime_type: str) -> str:
    """
    Save support photo to disk.
    
    Args:
        file_content: Photo file content as bytes
        filename: Original filename
        mime_type: MIME type of the file
        
    Returns:
        Relative file path from project root
    """
    # Ensure directory exists
    upload_dir = ensure_upload_directory()
    
    # Generate unique filename
    file_ext = Path(filename).suffix or _get_extension_from_mime_type(mime_type)
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Return relative path
    relative_path = os.path.join(settings.SUPPORT_PHOTOS_DIR, unique_filename)
    logger.info(f"Saved support photo: {relative_path} ({len(file_content)} bytes)")
    return relative_path


def get_support_photo_path(photo_id: int) -> Optional[str]:
    """
    Get full file path for a photo by ID.
    Note: This requires a database query, so it's better to use file_path directly.
    """
    # This is a helper function, but usually you'll use file_path from the database
    return None


def get_full_file_path(relative_path: str) -> str:
    """Get full absolute file path from relative path."""
    return os.path.join(os.getcwd(), relative_path)


def delete_support_photo(file_path: str) -> bool:
    """
    Delete support photo file from disk.
    
    Args:
        file_path: Relative file path from project root
        
    Returns:
        True if file was deleted, False if not found
    """
    full_path = get_full_file_path(file_path)
    
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            logger.info(f"Deleted support photo: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete support photo {file_path}: {e}")
            return False
    else:
        logger.warning(f"Support photo not found: {file_path}")
        return False


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


