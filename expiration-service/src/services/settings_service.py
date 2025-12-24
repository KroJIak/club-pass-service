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

