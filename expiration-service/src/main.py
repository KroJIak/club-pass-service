"""Main entry point for expiration service."""
import logging
import sys
import threading
from apscheduler.schedulers.blocking import BlockingScheduler
import uvicorn

from src.config import settings
from src.api import app, set_scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_api_server():
    """Run FastAPI server in a separate thread."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


def main():
    """Main function to run the scheduler."""
    logger.info("Starting Expiration Service...")
    logger.info(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info("Service will only deactivate events on demand (when scheduled via API)")
    
    # Setup scheduler (only for on-demand event deactivation)
    scheduler = BlockingScheduler()
    
    # Set scheduler in API for endpoints
    set_scheduler(scheduler)
    
    # Start FastAPI server in a separate thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    logger.info(f"FastAPI server started on port {settings.API_PORT}")
    
    logger.info("Scheduler started. Waiting for event deactivation requests...")
    logger.info("Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        scheduler.shutdown()


if __name__ == "__main__":
    main()

