"""Event repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.event import Event


class EventRepository:
    """Repository for event operations."""
    
    @staticmethod
    def get_all_active(db: Session) -> List[Event]:
        """Get all active events."""
        return db.query(Event).filter(
            Event.is_active == True,
            Event.is_deleted == False
        ).order_by(Event.start_date, Event.start_time).all()
    
    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        return db.query(Event).filter(
            Event.id == event_id,
            Event.is_deleted == False
        ).first()
    
    @staticmethod
    def get_active_by_id(db: Session, event_id: int) -> Optional[Event]:
        """Get active event by ID."""
        return db.query(Event).filter(
            Event.id == event_id,
            Event.is_active == True,
            Event.is_deleted == False
        ).first()
    
    @staticmethod
    def get_all(db: Session) -> List[Event]:
        """Get all events (including inactive)."""
        return db.query(Event).filter(Event.is_deleted == False).order_by(Event.created_at.desc()).all()
    
    @staticmethod
    def soft_delete(db: Session, event_id: int) -> bool:
        """Soft delete an event."""
        from datetime import datetime
        event = EventRepository.get_by_id(db, event_id)
        if not event or event.is_deleted:
            return False
        event.is_deleted = True
        event.deleted_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, event_id: int, hard: bool = False) -> bool:
        """Delete an event."""
        if not hard:
            return EventRepository.soft_delete(db, event_id)
        
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return False
        db.delete(event)
        db.commit()
        return True
