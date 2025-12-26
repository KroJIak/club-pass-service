"""Service for checking expiration settings from database."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for checking expiration settings."""
    
    @staticmethod
    def is_ticket_expiration_enabled(db: Session) -> bool:
        """
        Check if ticket expiration is enabled.
        
        Args:
            db: Database session
        
        Returns:
            True if enabled, False otherwise (defaults to True if settings don't exist)
        """
        try:
            result = db.execute(
                text("SELECT ticket_expiration_enabled FROM expiration_settings WHERE id = 1")
            ).first()
            
            if result:
                return bool(result[0])
            
            # Default to enabled if settings don't exist
            logger.warning("Expiration settings not found, defaulting to enabled")
            return True
        except Exception as e:
            logger.error(f"Error checking ticket expiration setting: {e}")
            # Default to enabled on error
            return True
    
    @staticmethod
    def is_event_deactivation_enabled(db: Session) -> bool:
        """
        Check if event deactivation is enabled.
        
        Args:
            db: Database session
        
        Returns:
            True if enabled, False otherwise (defaults to True if settings don't exist)
        """
        try:
            result = db.execute(
                text("SELECT event_deactivation_enabled FROM expiration_settings WHERE id = 1")
            ).first()
            
            if result:
                return bool(result[0])
            
            # Default to enabled if settings don't exist
            logger.warning("Expiration settings not found, defaulting to enabled")
            return True
        except Exception as e:
            logger.error(f"Error checking event deactivation setting: {e}")
            # Default to enabled on error
            return True
    
    @staticmethod
    def get_check_interval_minutes(db: Session) -> int:
        """
        Get check interval in minutes.
        
        Args:
            db: Database session
        
        Returns:
            Check interval in minutes (defaults to 30 if settings don't exist)
        """
        try:
            result = db.execute(
                text("SELECT check_interval_minutes FROM expiration_settings WHERE id = 1")
            ).first()
            
            if result:
                interval = int(result[0])
                if interval < 1:
                    logger.warning(f"Invalid check_interval_minutes value: {interval}, using default 30")
                    return 30
                return interval
            
            # Default to 30 minutes if settings don't exist
            logger.warning("Expiration settings not found, defaulting to 30 minutes")
            return 30
        except Exception as e:
            logger.error(f"Error checking check_interval_minutes setting: {e}")
            # Default to 30 minutes on error
            return 30
    
    @staticmethod
    def get_timezone(db: Session) -> str:
        """
        Get timezone from club settings.
        
        Args:
            db: Database session
        
        Returns:
            Timezone string (defaults to "Europe/Moscow" if settings don't exist)
        """
        try:
            result = db.execute(
                text("SELECT timezone FROM club_settings WHERE id = 1")
            ).first()
            
            if result and result[0]:
                return str(result[0])
            
            # Default to Europe/Moscow if settings don't exist
            logger.warning("Club settings not found, defaulting to Europe/Moscow timezone")
            return "Europe/Moscow"
        except Exception as e:
            logger.error(f"Error getting timezone setting: {e}")
            # Default to Europe/Moscow on error
            return "Europe/Moscow"

