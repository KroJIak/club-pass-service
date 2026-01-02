"""File service for downloading and saving photos from Telegram."""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO
from PIL import Image
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
        
        # Download file - bot.download() returns BytesIO
        from io import BytesIO
        file_content: BytesIO = await bot.download(file)
        if not file_content:
            logger.error(f"Failed to download file: {file_id}")
            return None
        
        # Read file content
        file_bytes = file_content.read()
        
        # Compress image before saving
        file_bytes = compress_image(file_bytes)
        
        # Determine MIME type (always JPEG after compression)
        mime_type = "image/jpeg"
        
        # Generate unique filename (always .jpg for compressed images)
        unique_filename = f"{uuid.uuid4()}.jpg"
        
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

