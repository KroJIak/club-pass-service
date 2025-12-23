"""Script to check and mark expired tickets."""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.core.db import SessionLocal
from api.services.ticket_expiration_service import TicketExpirationService


def check_expired_tickets():
    """Check and mark expired tickets."""
    db = SessionLocal()
    try:
        print(f"[{datetime.utcnow()}] Checking for expired tickets...")
        expired_count = TicketExpirationService.mark_expired_tickets(db)
        print(f"[{datetime.utcnow()}] Marked {expired_count} tickets as expired.")
        return expired_count
    except Exception as e:
        print(f"[{datetime.utcnow()}] Error checking expired tickets: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    check_expired_tickets()

