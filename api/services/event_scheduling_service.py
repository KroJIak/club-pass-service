"""Service for scheduling event deactivation."""
import httpx
import logging
from datetime import datetime
from typing import Optional
import pytz
from api.core.config import settings
from api.repositories.club_settings_repository import ClubSettingsRepository
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def parse_datetime(date_str: str, time_str: str, timezone_str: str = "Europe/Moscow") -> datetime:
    """
    Parse date and time strings to datetime object in specified timezone.
    
    Args:
        date_str: Date in format "DD.MM.YYYY"
        time_str: Time in format "HH:MM"
        timezone_str: Timezone string (default: "Europe/Moscow")
    
    Returns:
        datetime object in the specified timezone
    """
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    naive_dt = datetime.combine(date_obj.date(), time_obj)
    
    # Convert to specified timezone
    try:
        tz = pytz.timezone(timezone_str)
        return tz.localize(naive_dt)
    except Exception as e:
        logger.warning(f"Invalid timezone {timezone_str}, using naive datetime: {e}")
        return naive_dt


async def schedule_event_deactivation(
    db: Session,
    event_id: int,
    end_date: Optional[str],
    end_time: Optional[str]
) -> bool:
    """
    Schedule event deactivation in expiration service.
    
    Args:
        db: Database session
        event_id: Event ID
        end_date: End date in format "DD.MM.YYYY" (optional)
        end_time: End time in format "HH:MM" (optional)
    
    Returns:
        True if scheduled successfully, False otherwise
    """
    # Check if auto deactivation is enabled
    club_settings = ClubSettingsRepository.get_settings(db)
    if not club_settings.auto_deactivate_events:
        logger.debug(f"Auto deactivation is disabled, skipping scheduling for event {event_id}")
        return False
    
    # If no end date/time provided, don't schedule
    if not end_date or not end_time:
        logger.debug(f"No end date/time provided for event {event_id}, skipping scheduling")
        return False
    
    try:
        # Get timezone from club settings
        timezone_str = getattr(club_settings, 'timezone', 'Europe/Moscow')
        if not timezone_str:
            timezone_str = 'Europe/Moscow'
        
        # Parse end datetime with timezone
        deactivation_dt = parse_datetime(end_date, end_time, timezone_str)
        
        # Check if datetime is in the future (compare with current time in same timezone)
        try:
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz)
        except Exception:
            current_time = datetime.now()
        
        if deactivation_dt <= current_time:
            logger.warning(f"End datetime for event {event_id} is in the past, skipping scheduling")
            return False
        
        # Call expiration service
        expiration_service_url = settings.EXPIRATION_SERVICE_URL
        url = f"{expiration_service_url}/schedule-event-deactivation"
        
        logger.info("=" * 60)
        logger.info(f"📤 SENDING REQUEST to expiration-service:")
        logger.info(f"   Event ID: {event_id}")
        logger.info(f"   End date: {end_date}")
        logger.info(f"   End time: {end_time}")
        logger.info(f"   Timezone: {timezone_str}")
        logger.info(f"   Deactivation datetime: {deactivation_dt}")
        logger.info(f"   URL: {url}")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                url,
                json={
                    "event_id": event_id,
                    "deactivation_datetime": deactivation_dt.isoformat()
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully scheduled deactivation for event {event_id}")
                logger.info(f"   Response: {response.json()}")
                logger.info("=" * 60)
                return True
            else:
                logger.warning(f"⚠️  Failed to schedule deactivation for event {event_id}")
                logger.warning(f"   Status code: {response.status_code}")
                logger.warning(f"   Response: {response.text}")
                logger.info("=" * 60)
                return False
    except Exception as e:
        logger.error(f"Error scheduling deactivation for event {event_id}: {e}", exc_info=True)
        return False


async def cancel_event_deactivation(event_id: int) -> bool:
    """
    Cancel scheduled event deactivation.
    
    Args:
        event_id: Event ID
    
    Returns:
        True if cancelled successfully, False otherwise
    """
    try:
        expiration_service_url = settings.EXPIRATION_SERVICE_URL
        url = f"{expiration_service_url}/cancel-event-deactivation/{event_id}"
        
        logger.info(f"Cancelling deactivation for event {event_id}")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(url)
            
            if response.status_code == 200:
                logger.info(f"Successfully cancelled deactivation for event {event_id}")
                return True
            else:
                logger.warning(f"Failed to cancel deactivation for event {event_id}: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logger.error(f"Error cancelling deactivation for event {event_id}: {e}", exc_info=True)
        return False

