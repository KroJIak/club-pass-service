"""Ticket repository."""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import secrets
import string
from api.models.ticket import Ticket, TicketStatus


class TicketRepository:
    """Repository for ticket operations."""
    
    @staticmethod
    def _generate_token() -> str:
        """Generate unique ticket token."""
        # Format: TKT-XXXXX-XXXXX
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        random_part2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        return f"TKT-{random_part}-{random_part2}"
    
    @staticmethod
    def get_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
        """Get ticket by ID with related data."""
        return db.query(Ticket).options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type)
        ).filter(Ticket.id == ticket_id).first()
    
    @staticmethod
    def get_by_token(db: Session, token: str) -> Optional[Ticket]:
        """Get ticket by token."""
        return db.query(Ticket).options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type)
        ).filter(Ticket.token == token).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int, active_only: bool = False) -> List[Ticket]:
        """Get tickets for a user."""
        query = db.query(Ticket).options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type)
        ).filter(Ticket.user_id == user_id)
        
        if active_only:
            query = query.filter(Ticket.status == TicketStatus.ACTIVE)
        
        return query.order_by(Ticket.created_at.desc()).all()
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
    ) -> Ticket:
        """Create a new ticket."""
        # Generate unique token
        token = TicketRepository._generate_token()
        # Ensure token is unique
        while TicketRepository.get_by_token(db, token):
            token = TicketRepository._generate_token()
        
        ticket = Ticket(
            user_id=user_id,
            event_id=event_id,
            ticket_type_id=ticket_type_id,
            token=token,
            status=TicketStatus.ACTIVE,
            is_used=False,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def create_batch(
        db: Session,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
        quantity: int,
    ) -> List[Ticket]:
        """Create multiple tickets."""
        tickets = []
        for _ in range(quantity):
            ticket = TicketRepository.create(db, user_id, event_id, ticket_type_id)
            tickets.append(ticket)
        return tickets
    
    @staticmethod
    def refund_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
        """Refund a ticket (mark as refunded)."""
        ticket = TicketRepository.get_by_id(db, ticket_id)
        if not ticket:
            return None
        
        if ticket.is_used:
            raise ValueError("Cannot refund a used ticket")
        
        if ticket.status == TicketStatus.REFUNDED:
            raise ValueError("Ticket is already refunded")
        
        ticket.status = TicketStatus.REFUNDED
        ticket.refunded_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def mark_as_used(db: Session, ticket_id: int) -> Optional[Ticket]:
        """Mark ticket as used."""
        ticket = TicketRepository.get_by_id(db, ticket_id)
        if not ticket:
            return None
        
        if ticket.is_used:
            return ticket  # Already used
        
        ticket.is_used = True
        ticket.used_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        return ticket
