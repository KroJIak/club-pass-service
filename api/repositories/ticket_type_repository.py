"""TicketType repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.ticket_type import TicketType


class TicketTypeRepository:
    """Repository for ticket type operations."""
    
    @staticmethod
    def get_by_event_id(db: Session, event_id: int, active_only: bool = True) -> List[TicketType]:
        """Get ticket types for an event."""
        query = db.query(TicketType).filter(TicketType.event_id == event_id)
        if active_only:
            query = query.filter(TicketType.is_active == True)
        return query.order_by(TicketType.price).all()
    
    @staticmethod
    def get_by_id(db: Session, ticket_type_id: int) -> Optional[TicketType]:
        """Get ticket type by ID."""
        return db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    
    @staticmethod
    def get_active_by_id(db: Session, ticket_type_id: int) -> Optional[TicketType]:
        """Get active ticket type by ID."""
        return db.query(TicketType).filter(
            TicketType.id == ticket_type_id,
            TicketType.is_active == True
        ).first()
    
    @staticmethod
    def check_availability(db: Session, ticket_type_id: int, quantity: int) -> bool:
        """Check if ticket type has enough available quantity."""
        ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
        if not ticket_type:
            return False
        return ticket_type.available_quantity >= quantity
    
    @staticmethod
    def decrease_availability(db: Session, ticket_type_id: int, quantity: int) -> None:
        """Decrease available quantity for ticket type."""
        ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
        if ticket_type:
            ticket_type.available_quantity = max(0, ticket_type.available_quantity - quantity)
            db.commit()
    
    @staticmethod
    def increase_availability(db: Session, ticket_type_id: int, quantity: int) -> None:
        """Increase available quantity for ticket type."""
        ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
        if ticket_type:
            ticket_type.available_quantity += quantity
            db.commit()
    
    @staticmethod
    def increase_total_quantity(db: Session, ticket_type_id: int, quantity: int) -> None:
        """Increase total quantity for ticket type."""
        ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
        if ticket_type:
            ticket_type.total_quantity += quantity
            db.commit()
    
    @staticmethod
    def decrease_total_quantity(db: Session, ticket_type_id: int, quantity: int) -> None:
        """Decrease total quantity for ticket type."""
        ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
        if ticket_type:
            ticket_type.total_quantity = max(0, ticket_type.total_quantity - quantity)
            db.commit()
    
    @staticmethod
    def get_all(db: Session) -> List[TicketType]:
        """Get all ticket types (including inactive)."""
        return db.query(TicketType).order_by(TicketType.id.desc()).all()

