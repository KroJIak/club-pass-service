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
            joinedload(Ticket.ticket_type),
            joinedload(Ticket.user)
        ).filter(Ticket.token == token).first()
    
    @staticmethod
    def get_all(db: Session) -> List[Ticket]:
        """Get all tickets."""
        return db.query(Ticket).options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type),
            joinedload(Ticket.user)
        ).order_by(Ticket.created_at.desc()).all()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int, active_only: bool = False) -> List[Ticket]:
        """Get tickets for a user."""
        query = db.query(Ticket).options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type)
        ).filter(Ticket.user_id == user_id)
        
        if active_only:
            # Only return active tickets (exclude expired, refunded, cancelled, and used)
            query = query.filter(Ticket.status == TicketStatus.ACTIVE)
        
        return query.order_by(Ticket.created_at.desc()).all()
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
        token: Optional[str] = None,
        status: Optional[TicketStatus] = None,
    ) -> Ticket:
        """Create a new ticket."""
        # Generate unique token if not provided
        if token is None:
            token = TicketRepository._generate_token()
            # Ensure token is unique
            while TicketRepository.get_by_token(db, token):
                token = TicketRepository._generate_token()
        else:
            # Check if provided token is unique
            if TicketRepository.get_by_token(db, token):
                raise ValueError(f"Token {token} already exists")
        
        # Use provided status or default to ACTIVE
        if status is None:
            status = TicketStatus.ACTIVE
        
        ticket = Ticket(
            user_id=user_id,
            event_id=event_id,
            ticket_type_id=ticket_type_id,
            token=token,
            status=status,
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
        
        if ticket.status == TicketStatus.USED:
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
        
        if ticket.status == TicketStatus.USED:
            return ticket  # Already used
        
        ticket.status = TicketStatus.USED
        ticket.used_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        return ticket
