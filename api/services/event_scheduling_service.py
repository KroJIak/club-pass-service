"""Service for scheduling event deactivation."""
import httpx
import logging
from datetime import datetime
from typing import Optional
from api.core.config import settings
from api.repositories.club_settings_repository import ClubSettingsRepository
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def parse_datetime(date_str: str, time_str: str) -> datetime:
    """Parse date and time strings to datetime object."""
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    return datetime.combine(date_obj.date(), time_obj)


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
        # Parse end datetime
        deactivation_dt = parse_datetime(end_date, end_time)
        
        # Check if datetime is in the future
        if deactivation_dt <= datetime.now():
            logger.warning(f"End datetime for event {event_id} is in the past, skipping scheduling")
            return False
        
        # Call expiration service
        expiration_service_url = settings.EXPIRATION_SERVICE_URL
        url = f"{expiration_service_url}/schedule-event-deactivation"
        
        logger.info(f"Scheduling deactivation for event {event_id} at {deactivation_dt}")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                url,
                json={
                    "event_id": event_id,
                    "deactivation_datetime": deactivation_dt.isoformat()
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully scheduled deactivation for event {event_id}")
                return True
            else:
                logger.warning(f"Failed to schedule deactivation for event {event_id}: {response.status_code} - {response.text}")
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

