"""Main entry point for expiration service."""
import logging
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from src.config import settings
from src.db import SessionLocal
from src.services.expiration_service import TicketExpirationService
from src.services.settings_service import SettingsService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_and_mark_expired_tickets():
    """Check and mark expired tickets."""
    db: Session = SessionLocal()
    try:
        # Check if ticket expiration is enabled
        if not SettingsService.is_ticket_expiration_enabled(db):
            logger.debug("Ticket expiration is disabled, skipping check")
            return 0
        
        logger.info("Starting expired tickets check...")
        expired_count = TicketExpirationService.mark_expired_tickets(db)
        if expired_count > 0:
            logger.info(f"Marked {expired_count} ticket(s) as expired.")
        else:
            logger.debug("No expired tickets found.")
        return expired_count
    except Exception as e:
        logger.error(f"Error checking expired tickets: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def check_and_deactivate_events():
    """Check and deactivate past events."""
    db: Session = SessionLocal()
    try:
        # Check if event deactivation is enabled
        if not SettingsService.is_event_deactivation_enabled(db):
            logger.debug("Event deactivation is disabled, skipping check")
            return 0
        
        logger.info("Starting events deactivation check...")
        deactivated_count = TicketExpirationService.deactivate_past_events(db)
        if deactivated_count > 0:
            logger.info(f"Deactivated {deactivated_count} event(s).")
        else:
            logger.debug("No events found to deactivate.")
        return deactivated_count
    except Exception as e:
        logger.error(f"Error deactivating events: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def run_all_checks():
    """Run all expiration and deactivation checks."""
    logger.info("=" * 50)
    logger.info("Running all expiration checks...")
    
    tickets_count = check_and_mark_expired_tickets()
    events_count = check_and_deactivate_events()
    
    logger.info(f"Checks completed: {tickets_count} tickets expired, {events_count} events deactivated")
    logger.info("=" * 50)


def update_scheduler_interval(scheduler: BlockingScheduler):
    """Update scheduler interval from database settings."""
    db: Session = SessionLocal()
    try:
        interval = SettingsService.get_check_interval_minutes(db)
        job = scheduler.get_job('check_expirations')
        
        if job:
            # Check if interval has changed
            current_interval = job.trigger.interval.total_seconds() / 60
            if current_interval != interval:
                logger.info(f"Updating check interval from {current_interval} to {interval} minutes")
                scheduler.reschedule_job(
                    'check_expirations',
                    trigger=IntervalTrigger(minutes=interval)
                )
        else:
            # Job doesn't exist, create it
            logger.info(f"Creating check job with interval {interval} minutes")
            scheduler.add_job(
                run_all_checks,
                trigger=IntervalTrigger(minutes=interval),
                id='check_expirations',
                name='Check expired tickets and deactivate past events',
                replace_existing=True
            )
    except Exception as e:
        logger.error(f"Error updating scheduler interval: {e}", exc_info=True)
    finally:
        db.close()


def main():
    """Main function to run the scheduler."""
    logger.info("Starting Expiration Service...")
    logger.info(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    # Get initial interval from database
    db: Session = SessionLocal()
    try:
        initial_interval = SettingsService.get_check_interval_minutes(db)
        logger.info(f"Initial check interval: {initial_interval} minutes")
    except Exception as e:
        logger.warning(f"Could not get interval from database, using default: {e}")
        initial_interval = settings.CHECK_INTERVAL_MINUTES
    finally:
        db.close()
    
    # Run initial check
    logger.info("Running initial check...")
    try:
        run_all_checks()
    except Exception as e:
        logger.error(f"Initial check failed: {e}", exc_info=True)
        sys.exit(1)
    
    # Setup scheduler
    scheduler = BlockingScheduler()
    
    # Schedule periodic checks for tickets and events with initial interval
    scheduler.add_job(
        run_all_checks,
        trigger=IntervalTrigger(minutes=initial_interval),
        id='check_expirations',
        name='Check expired tickets and deactivate past events',
        replace_existing=True
    )
    
    # Schedule a job to periodically check and update the interval from database
    # Check every 5 minutes if interval has changed
    scheduler.add_job(
        update_scheduler_interval,
        trigger=IntervalTrigger(minutes=5),
        args=[scheduler],
        id='update_interval',
        name='Update check interval from database',
        replace_existing=True
    )
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        scheduler.shutdown()


if __name__ == "__main__":
    main()

