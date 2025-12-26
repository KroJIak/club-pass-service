"""Service for checking and updating expired tickets and deactivating past events."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
import pytz
from src.models.ticket import Ticket, TicketStatus
from src.models.event import Event
from src.services.settings_service import SettingsService

logger = logging.getLogger(__name__)


class TicketExpirationService:
    """Service for handling ticket expiration."""
    
    @staticmethod
    def _get_current_time(db: Session) -> datetime:
        """
        Get current time in the configured timezone.
        
        Args:
            db: Database session
        
        Returns:
            datetime object in the configured timezone
        """
        try:
            timezone_str = SettingsService.get_timezone(db)
            try:
                tz = pytz.timezone(timezone_str)
                return datetime.now(tz)
            except Exception as e:
                logger.warning(f"Invalid timezone {timezone_str}, using UTC: {e}")
                return datetime.utcnow()
        except Exception as e:
            logger.error(f"Error getting current time with timezone: {e}, using UTC")
            return datetime.utcnow()
    
    @staticmethod
    def _parse_event_datetime(event_date: str, event_time: str, db: Session) -> datetime:
        """
        Parse event date and time to datetime object in the configured timezone.
        
        Args:
            event_date: Date in format "DD.MM.YYYY"
            event_time: Time in format "HH:MM"
            db: Database session for getting timezone
        
        Returns:
            datetime object in the configured timezone
        """
        date_obj = datetime.strptime(event_date, "%d.%m.%Y")
        time_obj = datetime.strptime(event_time, "%H:%M").time()
        naive_dt = datetime.combine(date_obj.date(), time_obj)
        
        # Convert to configured timezone
        try:
            timezone_str = SettingsService.get_timezone(db)
            try:
                tz = pytz.timezone(timezone_str)
                return tz.localize(naive_dt)
            except Exception as e:
                logger.warning(f"Invalid timezone {timezone_str}, using naive datetime: {e}")
                return naive_dt
        except Exception as e:
            logger.error(f"Error getting timezone for datetime parsing: {e}, using naive datetime")
            return naive_dt
    
    @staticmethod
    def _calculate_expiration_datetime(event_date: str, event_time: str, db: Session) -> datetime:
        """
        Calculate expiration datetime for a ticket.
        
        Logic:
        - If event time is 00:00-11:59, ticket expires at 12:00 of the same day
        - If event time is 12:00-23:59, ticket expires at 12:00 of the next day
        
        Args:
            event_date: Date in format "DD.MM.YYYY"
            event_time: Time in format "HH:MM"
            db: Database session for getting timezone
        
        Returns:
            datetime when ticket expires (in configured timezone)
        """
        event_dt = TicketExpirationService._parse_event_datetime(event_date, event_time, db)
        hour = event_dt.hour
        
        if hour < 12:
            # Event before 12:00, expires at 12:00 same day
            expiration = event_dt.replace(hour=12, minute=0, second=0, microsecond=0)
        else:
            # Event at or after 12:00, expires at 12:00 next day
            expiration = event_dt.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return expiration
    
    @staticmethod
    def is_ticket_expired(ticket: Ticket, db: Session, current_time: datetime = None) -> bool:
        """
        Check if a ticket is expired.
        
        Args:
            ticket: Ticket object with event relationship loaded
            db: Database session for getting timezone
            current_time: Current datetime (defaults to now in configured timezone)
        
        Returns:
            True if ticket is expired, False otherwise
        """
        if current_time is None:
            current_time = TicketExpirationService._get_current_time(db)
        
        # Only process tickets with ACTIVE status
        if ticket.status != TicketStatus.ACTIVE:
            return False
        
        # If event doesn't exist, ticket should be marked as expired
        if not ticket.event:
            logger.warning(f"Ticket {ticket.id} (token: {ticket.token}) has no associated event, marking as expired")
            return True
        
        expiration_dt = TicketExpirationService._calculate_expiration_datetime(
            ticket.event.start_date,
            ticket.event.start_time,
            db
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
            current_time: Current datetime (defaults to now in configured timezone)
        
        Returns:
            Number of tickets marked as expired
        """
        if current_time is None:
            current_time = TicketExpirationService._get_current_time(db)
        
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
            
            if TicketExpirationService.is_ticket_expired(ticket, db, current_time):
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
            current_time: Current datetime (defaults to now in configured timezone)
        
        Returns:
            List of expired tickets
        """
        if current_time is None:
            current_time = TicketExpirationService._get_current_time(db)
        
        tickets = db.query(Ticket).options(
            joinedload(Ticket.event)
        ).filter(
            Ticket.status == TicketStatus.ACTIVE
        ).all()
        
        expired = []
        for ticket in tickets:
            if TicketExpirationService.is_ticket_expired(ticket, db, current_time):
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
            current_time: Current datetime (defaults to now in configured timezone)
        
        Returns:
            Number of events deactivated
        """
        if current_time is None:
            current_time = TicketExpirationService._get_current_time(db)
        
        # Get all active events
        events = db.query(Event).filter(Event.is_active == True).all()
        
        logger.debug(f"Checking {len(events)} active events for deactivation...")
        
        deactivated_count = 0
        for event in events:
            expiration_dt = TicketExpirationService._calculate_expiration_datetime(
                event.start_date,
                event.start_time,
                db
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

