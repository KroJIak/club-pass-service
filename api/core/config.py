"""Configuration settings for API service."""
from pydantic_settings import BaseSettings
from typing import Optional


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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    
    # YooKassa (will be configured later)
    YOOKASSA_SHOP_ID: Optional[str] = None
    YOOKASSA_SECRET_KEY: Optional[str] = None
    
    # Telegram Bot (for notifications)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Expiration Service
    EXPIRATION_SERVICE_URL: str = "http://expiration-service:8001"
    
    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins, or "*" for all
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
