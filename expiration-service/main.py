"""Ticket expiration service - periodically checks and marks expired tickets."""
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from api
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from api.core.db import SessionLocal
from api.services.ticket_expiration_service import TicketExpirationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))
CHECK_INTERVAL_SECONDS = CHECK_INTERVAL_MINUTES * 60


def check_expired_tickets():
    """Check and mark expired tickets."""
    db: Session = None
    try:
        db = SessionLocal()
        logger.info("Starting expired tickets check...")
        expired_count = TicketExpirationService.mark_expired_tickets(db)
        logger.info(f"Check completed. Marked {expired_count} tickets as expired.")
        return expired_count
    except Exception as e:
        logger.error(f"Error checking expired tickets: {e}", exc_info=True)
        raise
    finally:
        if db:
            db.close()


def main():
    """Main service loop."""
    logger.info("Ticket Expiration Service started")
    logger.info(f"Check interval: {CHECK_INTERVAL_MINUTES} minutes")
    
    while True:
        try:
            check_expired_tickets()
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}", exc_info=True)
            # Continue running even if there's an error
            time.sleep(60)  # Wait 1 minute before retrying on error
            continue
        
        # Wait for next check
        logger.info(f"Waiting {CHECK_INTERVAL_MINUTES} minutes until next check...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

