"""Database initialization script.

This script checks if database tables exist and creates them if they don't.
It should be run on first startup to ensure the database is properly initialized.
"""
import sys
import time
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from api.core.db import engine, Base
from api.core.config import settings
from api.models import (
    User,
    Event,
    TicketType,
    Ticket,
    Payment,
    Promocode,
    Order,
    ExpirationSettings,
    ClubSettings,
)

# Import all models to ensure they are registered with Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_database_connection(max_retries=5, retry_delay=2):
    """Check if database is accessible with retries."""
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                return False
    return False


def check_tables_exist():
    """Check if any tables exist in the database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            logger.info(f"Found {len(tables)} existing tables: {', '.join(tables)}")
        else:
            logger.info("No tables found in database")
        return len(tables) > 0
    except Exception as e:
        logger.error(f"Error checking tables: {e}", exc_info=True)
        return False


def check_table_exists(table_name: str) -> bool:
    """Check if a specific table exists in the database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        logger.error(f"Error checking table {table_name}: {e}", exc_info=True)
        return False


def create_tables():
    """Create all tables defined in models."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}", exc_info=True)
        return False


def init_database():
    """Initialize database if tables don't exist."""
    logger.info("Starting database initialization...")
    logger.info(f"Database: {settings.DB_NAME} at {settings.DB_HOST}:{settings.DB_PORT}")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot connect to database. Exiting.")
        sys.exit(1)
    
    # Check if tables already exist
    if check_tables_exist():
        logger.info("Some tables already exist. Checking for missing tables...")
        
        # Check for critical tables that should exist
        required_tables = [
            "users", "events", "tickets", "payments", "orders", 
            "promocodes", "ticket_types", "expiration_settings", "club_settings"
        ]
        
        missing_tables = []
        for table in required_tables:
            if not check_table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            logger.info(f"Found missing tables: {', '.join(missing_tables)}. Creating them...")
            if create_tables():
                logger.info("Missing tables created successfully")
            else:
                logger.error("Failed to create missing tables")
                sys.exit(1)
        else:
            logger.info("All required tables exist. Skipping initialization.")
        return
    
    # Create tables
    logger.info("No tables found. Creating database schema...")
    if create_tables():
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    init_database()

