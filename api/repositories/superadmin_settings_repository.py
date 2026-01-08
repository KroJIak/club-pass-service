"""Superadmin settings repository."""
from typing import Optional
from sqlalchemy.orm import Session
from api.models.superadmin_settings import SuperadminSettings


class SuperadminSettingsRepository:
    """Repository for superadmin settings operations."""
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[SuperadminSettings]:
        """Get settings by username."""
        return db.query(SuperadminSettings).filter(
            SuperadminSettings.username == username
        ).first()
    
    @staticmethod
    def get_or_create(db: Session, username: str, default_language: str = 'ru') -> SuperadminSettings:
        """Get settings by username or create if not exists."""
        settings = SuperadminSettingsRepository.get_by_username(db, username)
        if not settings:
            settings = SuperadminSettings(
                username=username,
                language=default_language
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings
    
    @staticmethod
    def update_language(db: Session, username: str, language: str) -> Optional[SuperadminSettings]:
        """Update language for superadmin."""
        settings = SuperadminSettingsRepository.get_or_create(db, username)
        settings.language = language
        db.commit()
        db.refresh(settings)
        return settings

