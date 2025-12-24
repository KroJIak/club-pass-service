"""Main entry point for ticket expiration service."""
import logging
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from src.config import settings
from src.db import SessionLocal
from src.services.expiration_service import TicketExpirationService

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


def main():
    """Main function to run the scheduler."""
    logger.info("Starting Expiration Service...")
    logger.info(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info(f"Check interval: {settings.CHECK_INTERVAL_MINUTES} minutes")
    
    # Run initial check
    logger.info("Running initial check...")
    try:
        run_all_checks()
    except Exception as e:
        logger.error(f"Initial check failed: {e}", exc_info=True)
        sys.exit(1)
    
    # Setup scheduler
    scheduler = BlockingScheduler()
    
    # Schedule periodic checks for tickets and events
    scheduler.add_job(
        run_all_checks,
        trigger=IntervalTrigger(minutes=settings.CHECK_INTERVAL_MINUTES),
        id='check_expirations',
        name='Check expired tickets and deactivate past events',
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

