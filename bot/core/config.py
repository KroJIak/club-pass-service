"""Bot configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Bot settings loaded from environment variables."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    
    # API
    API_URL: str = "http://api:8000"
    API_PREFIX: str = "/api"
    
    # Club info - these should be configured in admin panel, not in .env
    # Keeping as optional for backward compatibility until API endpoint is implemented
    CLUB_ADDRESS: Optional[str] = None
    CLUB_PHONE: Optional[str] = None
    CLUB_EMAIL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
