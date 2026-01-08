"""Configuration settings for API service."""
from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API
    API_TITLE: str = "Club Pass Service API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "club_pass"
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 12 hours (720 minutes)
    
    # Admin credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    
    # YooKassa (will be configured later)
    YOOKASSA_SHOP_ID: Optional[str] = None
    YOOKASSA_SECRET_KEY: Optional[str] = None
    
    # Telegram Bot (for notifications)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Staff Bot Token (for Mini App validation)
    STAFF_BOT_TOKEN: Optional[str] = None
    
    # Temporary: Skip initData validation for debugging (ONLY FOR TESTING!)
    SKIP_INITDATA_VALIDATION: bool = False
    
    # Expiration Service
    EXPIRATION_SERVICE_URL: str = "http://expiration-service:8001"
    
    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins for admin panel, or "*" for all
    CORS_ORIGINS_MINI_APP: Optional[str] = None  # Comma-separated list of allowed origins for mini app
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_PHOTO_SIZE_MB: int = 10
    SUPPORT_PHOTOS_DIR: str = "uploads/support_photos"
    MENU_PHOTOS_DIR: str = "uploads/menu_photos"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Log admin credentials on startup (without exposing password)
logger.info(f"Admin credentials loaded: username='{settings.ADMIN_USERNAME}', password_length={len(settings.ADMIN_PASSWORD)}")
