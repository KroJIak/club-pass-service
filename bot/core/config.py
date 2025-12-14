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
    
    # Bot settings
    DEBUG: bool = False
    
    # Club info
    CLUB_NAME: str = "Night Club"
    CLUB_ADDRESS: str = "Москва, ул. Примерная, 1"
    CLUB_PHONE: Optional[str] = None
    CLUB_EMAIL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
