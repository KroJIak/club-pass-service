"""Service for checking and updating expired tickets."""
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from api.models.ticket import Ticket, TicketStatus
from api.repositories.ticket_repository import TicketRepository


class TicketExpirationService:
    """Service for handling ticket expiration."""
    
    @staticmethod
    def _parse_event_datetime(event_date: str, event_time: str) -> datetime:
        """
        Parse event date and time to datetime object.
        
        Args:
            event_date: Date in format "DD.MM.YYYY"
            event_time: Time in format "HH:MM"
        
        Returns:
            datetime object
        """
        date_obj = datetime.strptime(event_date, "%d.%m.%Y")
        time_obj = datetime.strptime(event_time, "%H:%M").time()
        return datetime.combine(date_obj.date(), time_obj)
    
    @staticmethod
    def _calculate_expiration_datetime(event_date: str, event_time: str) -> datetime:
        """
        Calculate expiration datetime for a ticket.
        
        Logic:
        - If event time is 00:00-11:59, ticket expires at 12:00 of the same day
        - If event time is 12:00-23:59, ticket expires at 12:00 of the next day
        
        Args:
            event_date: Date in format "DD.MM.YYYY"
            event_time: Time in format "HH:MM"
        
        Returns:
            datetime when ticket expires
        """
        event_dt = TicketExpirationService._parse_event_datetime(event_date, event_time)
        hour = event_dt.hour
        
        if hour < 12:
            # Event before 12:00, expires at 12:00 same day
            expiration = event_dt.replace(hour=12, minute=0, second=0, microsecond=0)
        else:
            # Event at or after 12:00, expires at 12:00 next day
            expiration = event_dt.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return expiration
    
    @staticmethod
    def is_ticket_expired(ticket: Ticket, current_time: datetime = None) -> bool:
        """
        Check if a ticket is expired.
        
        Args:
            ticket: Ticket object with event relationship loaded
            current_time: Current datetime (defaults to now)
        
        Returns:
            True if ticket is expired, False otherwise
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Skip if already expired, refunded, cancelled, or used
        if ticket.status in [TicketStatus.EXPIRED, TicketStatus.REFUNDED, TicketStatus.CANCELLED, TicketStatus.USED]:
            return False
        
        # Check if event is loaded
        if not ticket.event:
            return False
        
        expiration_dt = TicketExpirationService._calculate_expiration_datetime(
            ticket.event.start_date,
            ticket.event.start_time
        )
        
        return current_time >= expiration_dt
    
    @staticmethod
    def mark_expired_tickets(db: Session, current_time: datetime = None) -> int:
        """
        Find and mark expired tickets as expired.
        
        Args:
            db: Database session
            current_time: Current datetime (defaults to now)
        
        Returns:
            Number of tickets marked as expired
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Get all active tickets with event relationship
        from sqlalchemy.orm import joinedload
        tickets = db.query(Ticket).options(
            joinedload(Ticket.event)
        ).filter(
            Ticket.status == TicketStatus.ACTIVE
        ).all()
        
        expired_count = 0
        for ticket in tickets:
            if TicketExpirationService.is_ticket_expired(ticket, current_time):
                ticket.status = TicketStatus.EXPIRED
                expired_count += 1
        
        if expired_count > 0:
            db.commit()
        
        return expired_count
    
    @staticmethod
    def get_expired_tickets(db: Session, current_time: datetime = None) -> List[Ticket]:
        """
        Get list of tickets that should be expired (but not yet marked).
        
        Args:
            db: Database session
            current_time: Current datetime (defaults to now)
        
        Returns:
            List of expired tickets
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        from sqlalchemy.orm import joinedload
        tickets = db.query(Ticket).options(
            joinedload(Ticket.event)
        ).filter(
            Ticket.status == TicketStatus.ACTIVE
        ).all()
        
        expired = []
        for ticket in tickets:
            if TicketExpirationService.is_ticket_expired(ticket, current_time):
                expired.append(ticket)
        
        return expired

