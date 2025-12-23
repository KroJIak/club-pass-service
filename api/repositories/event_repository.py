"""Event repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.event import Event


class EventRepository:
    """Repository for event operations."""
    
    @staticmethod
    def get_all_active(db: Session) -> List[Event]:
        """Get all active events."""
        return db.query(Event).filter(Event.is_active == True).order_by(Event.date, Event.time).all()
    
    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        return db.query(Event).filter(Event.id == event_id).first()
    
    @staticmethod
    def get_active_by_id(db: Session, event_id: int) -> Optional[Event]:
        """Get active event by ID."""
        return db.query(Event).filter(
            Event.id == event_id,
            Event.is_active == True
        ).first()
