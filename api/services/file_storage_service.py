"""File storage service for support photos."""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from io import BytesIO
from PIL import Image
from api.core.config import settings

logger = logging.getLogger(__name__)


def ensure_upload_directory() -> str:
    """Ensure upload directory exists. Returns the directory path."""
    upload_dir = os.path.join(os.getcwd(), settings.SUPPORT_PHOTOS_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def compress_image(image_bytes: bytes, max_size_mb: float = 2.0, quality: int = 85) -> bytes:
    """
    Compress image to reduce file size while maintaining reasonable quality.
    
    Args:
        image_bytes: Original image bytes
        max_size_mb: Maximum file size in MB (default 2MB)
        quality: JPEG quality (1-100, default 85)
        
    Returns:
        Compressed image bytes
    """
    try:
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        
        # If image is already small enough, return as is
        if len(image_bytes) <= max_size_bytes:
            return image_bytes
        
        # Open image
        img = Image.open(BytesIO(image_bytes))
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate target dimensions (reduce if too large)
        max_dimension = 1920  # Max width or height
        if img.width > max_dimension or img.height > max_dimension:
            ratio = min(max_dimension / img.width, max_dimension / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compress to JPEG
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        compressed_bytes = output.getvalue()
        
        # If still too large, reduce quality further
        if len(compressed_bytes) > max_size_bytes:
            quality = 75
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_bytes = output.getvalue()
        
        logger.info(f"Compressed image: {len(image_bytes)} -> {len(compressed_bytes)} bytes ({len(compressed_bytes)/len(image_bytes)*100:.1f}%)")
        return compressed_bytes
    except Exception as e:
        logger.warning(f"Failed to compress image, using original: {e}")
        return image_bytes


def save_support_photo(file_content: bytes, filename: str, mime_type: str, compress: bool = True) -> str:
    """
    Save support photo to disk with optional compression.
    
    Args:
        file_content: Photo file content as bytes
        filename: Original filename
        mime_type: MIME type of the file
        compress: Whether to compress the image (default True)
        
    Returns:
        Relative file path from project root
    """
    # Compress image if enabled
    if compress:
        file_content = compress_image(file_content)
    
    # Ensure directory exists
    upload_dir = ensure_upload_directory()
    
    # Generate unique filename (always use .jpg for compressed images)
    if compress:
        file_ext = '.jpg'
    else:
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


