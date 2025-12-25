"""Repository for ClubSettings model."""
from sqlalchemy.orm import Session
from api.models.club_settings import ClubSettings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ClubSettingsRepository:
    """Repository for club settings operations."""
    
    @staticmethod
    def get_settings(db: Session) -> ClubSettings:
        """
        Get club settings.
        Creates default settings if they don't exist.
        """
        settings = db.query(ClubSettings).filter(ClubSettings.id == 1).first()
        
        if not settings:
            # Create default settings
            settings = ClubSettings(
                id=1,
                address=None,
                phone=None,
                email=None,
                auto_deactivate_events=True
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
            logger.info("Created default club settings")
        
        return settings
    
    @staticmethod
    def update_settings(
        db: Session,
        address: str = None,
        phone: str = None,
        email: str = None,
        auto_deactivate_events: bool = None
    ) -> ClubSettings:
        """
        Update club settings.
        
        Args:
            db: Database session
            address: Club address
            phone: Club phone
            email: Club email
            auto_deactivate_events: Enable/disable automatic event deactivation
        
        Returns:
            Updated settings
        """
        settings = ClubSettingsRepository.get_settings(db)
        
        if address is not None:
            settings.address = address.strip() if address and address.strip() else None
        
        if phone is not None:
            settings.phone = phone.strip() if phone and phone.strip() else None
        
        if email is not None:
            settings.email = email.strip() if email and email.strip() else None
        
        if auto_deactivate_events is not None:
            settings.auto_deactivate_events = auto_deactivate_events
        
        settings.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(settings)
        
        logger.info(
            f"Updated club settings: "
            f"address={settings.address}, "
            f"phone={settings.phone}, "
            f"email={settings.email}, "
            f"auto_deactivate_events={settings.auto_deactivate_events}"
        )
        
        return settings

