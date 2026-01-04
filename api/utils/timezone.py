"""Utility functions for timezone handling."""
import pytz
from datetime import datetime
from sqlalchemy.orm import Session
from api.repositories.club_settings_repository import ClubSettingsRepository
import logging

logger = logging.getLogger(__name__)


def get_current_time_in_timezone(db: Session) -> datetime:
    """
    Get current time in the configured timezone.
    
    Args:
        db: Database session
        
    Returns:
        datetime object in the configured timezone (naive, but represents local time)
    """
    try:
        settings = ClubSettingsRepository.get_settings(db)
        timezone_str = settings.timezone or "Europe/Moscow"
        
        try:
            tz = pytz.timezone(timezone_str)
            # Get current time in the timezone
            now_utc = datetime.utcnow()
            # Convert to timezone-aware
            now_aware = pytz.UTC.localize(now_utc)
            # Convert to target timezone
            now_in_tz = now_aware.astimezone(tz)
            # Return as naive datetime (represents local time)
            return now_in_tz.replace(tzinfo=None)
        except Exception as e:
            logger.warning(f"Invalid timezone {timezone_str}, using UTC: {e}")
            return datetime.utcnow()
    except Exception as e:
        logger.error(f"Error getting current time with timezone: {e}, using UTC")
        return datetime.utcnow()

