"""Script to run the ticket expiration worker as a standalone service."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.services.ticket_expiration_worker import main

if __name__ == "__main__":
    main()

