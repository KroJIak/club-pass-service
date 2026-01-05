"""Repository for music request limits."""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from api.models.music_request_limit import MusicRequestLimit


class MusicRequestLimitRepository:
    """Repository for music request limit operations."""
    
    @staticmethod
    def get_last_request(db: Session, user_id: int, event_id: int) -> Optional[MusicRequestLimit]:
        """Get last request time for a user and event."""
        return db.query(MusicRequestLimit).filter(
            MusicRequestLimit.user_id == user_id,
            MusicRequestLimit.event_id == event_id
        ).first()
    
    @staticmethod
    def can_make_request(db: Session, user_id: int, event_id: int, cooldown_minutes: int = 5) -> bool:
        """Check if user can make a request (5 minutes cooldown).
        
        Args:
            db: Database session
            user_id: User ID
            event_id: Event ID
            cooldown_minutes: Cooldown period in minutes (default: 5)
        
        Returns:
            True if user can make a request, False otherwise
        """
        limit = MusicRequestLimitRepository.get_last_request(db, user_id, event_id)
        if not limit:
            return True
        
        cooldown_delta = timedelta(minutes=cooldown_minutes)
        time_since_last_request = datetime.utcnow() - limit.last_request_at.replace(tzinfo=None)
        
        return time_since_last_request >= cooldown_delta
    
    @staticmethod
    def update_last_request(db: Session, user_id: int, event_id: int) -> MusicRequestLimit:
        """Update or create last request time for a user and event."""
        limit = MusicRequestLimitRepository.get_last_request(db, user_id, event_id)
        
        if limit:
            limit.last_request_at = datetime.utcnow()
        else:
            limit = MusicRequestLimit(
                user_id=user_id,
                event_id=event_id,
                last_request_at=datetime.utcnow()
            )
            db.add(limit)
        
        db.commit()
        db.refresh(limit)
        return limit

