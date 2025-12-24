"""Repository for ExpirationSettings model."""
from sqlalchemy.orm import Session
from api.models.expiration_settings import ExpirationSettings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExpirationSettingsRepository:
    """Repository for expiration settings operations."""
    
    @staticmethod
    def get_settings(db: Session) -> ExpirationSettings:
        """
        Get expiration settings.
        Creates default settings if they don't exist.
        """
        settings = db.query(ExpirationSettings).filter(ExpirationSettings.id == 1).first()
        
        if not settings:
            # Create default settings
            settings = ExpirationSettings(
                id=1,
                ticket_expiration_enabled=True,
                event_deactivation_enabled=True,
                check_interval_minutes=30
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
            logger.info("Created default expiration settings")
        
        return settings
    
    @staticmethod
    def update_settings(
        db: Session,
        ticket_expiration_enabled: bool = None,
        event_deactivation_enabled: bool = None,
        check_interval_minutes: int = None
    ) -> ExpirationSettings:
        """
        Update expiration settings.
        
        Args:
            db: Database session
            ticket_expiration_enabled: Enable/disable ticket expiration
            event_deactivation_enabled: Enable/disable event deactivation
            check_interval_minutes: Check interval in minutes (minimum 1)
        
        Returns:
            Updated settings
        """
        settings = ExpirationSettingsRepository.get_settings(db)
        
        if ticket_expiration_enabled is not None:
            settings.ticket_expiration_enabled = ticket_expiration_enabled
        
        if event_deactivation_enabled is not None:
            settings.event_deactivation_enabled = event_deactivation_enabled
        
        if check_interval_minutes is not None:
            if check_interval_minutes < 1:
                raise ValueError("check_interval_minutes must be at least 1")
            settings.check_interval_minutes = check_interval_minutes
        
        settings.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(settings)
        
        logger.info(
            f"Updated expiration settings: "
            f"ticket_expiration={settings.ticket_expiration_enabled}, "
            f"event_deactivation={settings.event_deactivation_enabled}, "
            f"check_interval={settings.check_interval_minutes} minutes"
        )
        
        return settings

