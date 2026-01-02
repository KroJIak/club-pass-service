"""Service for interacting with Telegram Bot API."""
import httpx
import logging
from typing import Optional, Tuple
from api.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


async def download_file_from_telegram(file_id: str) -> Optional[Tuple[bytes, str, str]]:
    """
    Download file from Telegram by file_id.
    
    Args:
        file_id: Telegram file_id
        
    Returns:
        Tuple of (file_content, filename, mime_type) or None if error
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return None
    
    try:
        # First, get file path from Telegram
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get file info
            response = await client.get(
                f"{TELEGRAM_API_BASE}{settings.TELEGRAM_BOT_TOKEN}/getFile",
                params={"file_id": file_id}
            )
            response.raise_for_status()
            file_info = response.json()
            
            if not file_info.get("ok"):
                logger.error(f"Failed to get file info: {file_info}")
                return None
            
            file_path = file_info["result"]["file_path"]
            
            # Download file
            download_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
            file_response = await client.get(download_url, timeout=60.0)
            file_response.raise_for_status()
            
            file_content = file_response.content
            filename = file_path.split("/")[-1]
            
            # Determine MIME type from file extension
            mime_type = _get_mime_type_from_filename(filename)
            
            logger.info(f"Downloaded file from Telegram: {filename} ({len(file_content)} bytes)")
            return (file_content, filename, mime_type)
            
    except Exception as e:
        logger.error(f"Failed to download file from Telegram: {e}", exc_info=True)
        return None


def _get_mime_type_from_filename(filename: str) -> str:
    """Get MIME type from filename extension."""
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    return mime_types.get(ext, "image/jpeg")


