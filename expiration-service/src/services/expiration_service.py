"""Service for checking and updating expired tickets and deactivating past events."""
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session, joinedload
from src.models.ticket import Ticket, TicketStatus
from src.models.event import Event

logger = logging.getLogger(__name__)


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
        
        # Only process tickets with ACTIVE status
        if ticket.status != TicketStatus.ACTIVE:
            return False
        
        # If event doesn't exist, ticket should be marked as expired
        if not ticket.event:
            logger.warning(f"Ticket {ticket.id} (token: {ticket.token}) has no associated event, marking as expired")
            return True
        
        expiration_dt = TicketExpirationService._calculate_expiration_datetime(
            ticket.event.date,
            ticket.event.time
        )
        
        return current_time >= expiration_dt
    
    @staticmethod
    def mark_expired_tickets(db: Session, current_time: datetime = None) -> int:
        """
        Find and mark expired tickets as expired.
        
        Only marks tickets with ACTIVE status. Tickets with other statuses
        (REFUNDED, CANCELLED, USED, EXPIRED) are skipped.
        
        Also marks tickets as expired if their associated event doesn't exist.
        
        Args:
            db: Database session
            current_time: Current datetime (defaults to now)
        
        Returns:
            Number of tickets marked as expired
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Get all active tickets with event relationship
        tickets = db.query(Ticket).options(
            joinedload(Ticket.event)
        ).filter(
            Ticket.status == TicketStatus.ACTIVE
        ).all()
        
        logger.debug(f"Checking {len(tickets)} active tickets for expiration...")
        
        expired_count = 0
        for ticket in tickets:
            # Double-check status is still ACTIVE (defensive programming)
            if ticket.status != TicketStatus.ACTIVE:
                logger.debug(f"Skipping ticket {ticket.id} - status is {ticket.status}, not ACTIVE")
                continue
            
            if TicketExpirationService.is_ticket_expired(ticket, current_time):
                logger.info(f"Marking ticket {ticket.id} (token: {ticket.token}) as expired")
                ticket.status = TicketStatus.EXPIRED
                expired_count += 1
        
        if expired_count > 0:
            db.commit()
            logger.info(f"Successfully marked {expired_count} ticket(s) as expired")
        else:
            logger.debug("No tickets found to expire")
        
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
    
    @staticmethod
    def deactivate_past_events(db: Session, current_time: datetime = None) -> int:
        """
        Deactivate events that have passed their expiration time.
        
        Logic: Same as ticket expiration - if event time is before 12:00, 
        deactivate at 12:00 same day; if at or after 12:00, deactivate at 12:00 next day.
        
        Args:
            db: Database session
            current_time: Current datetime (defaults to now)
        
        Returns:
            Number of events deactivated
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Get all active events
        events = db.query(Event).filter(Event.is_active == True).all()
        
        logger.debug(f"Checking {len(events)} active events for deactivation...")
        
        deactivated_count = 0
        for event in events:
            expiration_dt = TicketExpirationService._calculate_expiration_datetime(
                event.date,
                event.time
            )
            
            if current_time >= expiration_dt:
                logger.info(f"Deactivating event {event.id} ({event.name})")
                event.is_active = False
                deactivated_count += 1
        
        if deactivated_count > 0:
            db.commit()
            logger.info(f"Successfully deactivated {deactivated_count} event(s)")
        else:
            logger.debug("No events found to deactivate")
        
        return deactivated_count

