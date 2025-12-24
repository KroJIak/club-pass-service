"""Background worker service for checking expired tickets."""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional

from api.core.db import SessionLocal
from api.services.ticket_expiration_service import TicketExpirationService

logger = logging.getLogger(__name__)

# Import settings only when needed to avoid circular imports
try:
    from api.core.config import settings
    CHECK_INTERVAL = settings.EXPIRATION_CHECK_INTERVAL_MINUTES
except:
    CHECK_INTERVAL = 30  # Default to 30 minutes

class TicketExpirationWorker:
    """Background worker that periodically checks and marks expired tickets."""
    
    def __init__(self, check_interval_minutes: int = 30):
        """
        Initialize the worker.
        
        Args:
            check_interval_minutes: Interval between checks in minutes (default: 30)
        """
        self.check_interval_minutes = check_interval_minutes
        self.running = False
        self._task: Optional[asyncio.Task] = None
    
    async def check_expired_tickets(self):
        """Check and mark expired tickets."""
        db = SessionLocal()
        try:
            logger.info("Checking for expired tickets...")
            expired_count = TicketExpirationService.mark_expired_tickets(db)
            if expired_count > 0:
                logger.info(f"Marked {expired_count} tickets as expired.")
            else:
                logger.debug("No expired tickets found.")
            return expired_count
        except Exception as e:
            logger.error(f"Error checking expired tickets: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def run_loop(self):
        """Main loop that runs periodic checks."""
        logger.info(f"Ticket expiration worker started. Check interval: {self.check_interval_minutes} minutes")
        
        while self.running:
            try:
                await self.check_expired_tickets()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
            
            # Wait for the next check interval
            await asyncio.sleep(self.check_interval_minutes * 60)
    
    def start(self):
        """Start the worker."""
        if self.running:
            logger.warning("Worker is already running")
            return
        
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal, stopping worker...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the async loop
        try:
            asyncio.run(self.run_loop())
        except KeyboardInterrupt:
            logger.info("Worker interrupted by user")
            self.stop()
    
    def stop(self):
        """Stop the worker."""
        logger.info("Stopping ticket expiration worker...")
        self.running = False
        if self._task:
            self._task.cancel()


def main():
    """Main entry point for the worker."""
    # Import settings here to ensure config is loaded
    from api.core.config import settings
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create and start worker
    check_interval = getattr(settings, 'EXPIRATION_CHECK_INTERVAL_MINUTES', 30)
    logger.info(f"Starting ticket expiration worker with check interval: {check_interval} minutes")
    worker = TicketExpirationWorker(check_interval_minutes=check_interval)
    worker.start()


if __name__ == "__main__":
    main()

