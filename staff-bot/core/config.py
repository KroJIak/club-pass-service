"""Staff Bot configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Staff Bot settings loaded from environment variables."""
    
    # Telegram Bot
    STAFF_BOT_TOKEN: str
    
    # API
    API_URL: str = "http://api:8000"
    API_PREFIX: str = "/api"
    
    # Mini App URL
    MINI_APP_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

