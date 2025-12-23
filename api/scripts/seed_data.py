"""Script to seed database with test data."""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from api.core.db import SessionLocal, engine, Base
from api.models import Event, TicketType, User
from decimal import Decimal


def seed_data():
    """Seed database with test data."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        existing_events = db.query(Event).count()
        if existing_events > 0:
            print("Database already has data. Skipping seed.")
            return
        
        # Create test events
        event1 = Event(
            name="Новогодняя вечеринка",
            description="Грандиозная новогодняя вечеринка с лучшими диджеями",
            date="31.12.2024",
            time="22:00",
            djs=["DJ. DIMSY", "EMPYZ", "JEWGEN", "ZIPSI"],
            is_active=True,
        )
        db.add(event1)
        db.flush()
        
        event2 = Event(
            name="House Music Night",
            description="Вечер качественной хаус музыки",
            date="05.01.2025",
            time="23:00",
            djs=["DJ. DIMSY", "EMPYZ"],
            is_active=True,
        )
        db.add(event2)
        db.flush()
        
        # Create ticket types for event1
        ticket_type1_1 = TicketType(
            event_id=event1.id,
            name="Обычный",
            price=Decimal("1500.00"),
            available_quantity=50,
            total_quantity=50,
            is_active=True,
        )
        db.add(ticket_type1_1)
        
        ticket_type1_2 = TicketType(
            event_id=event1.id,
            name="VIP",
            price=Decimal("3000.00"),
            available_quantity=20,
            total_quantity=20,
            is_active=True,
        )
        db.add(ticket_type1_2)
        
        # Create ticket types for event2
        ticket_type2_1 = TicketType(
            event_id=event2.id,
            name="Обычный",
            price=Decimal("1200.00"),
            available_quantity=100,
            total_quantity=100,
            is_active=True,
        )
        db.add(ticket_type2_1)
        
        ticket_type2_2 = TicketType(
            event_id=event2.id,
            name="VIP",
            price=Decimal("2500.00"),
            available_quantity=30,
            total_quantity=30,
            is_active=True,
        )
        db.add(ticket_type2_2)
        
        db.commit()
        print("✅ Test data seeded successfully!")
        print(f"   - Created 2 events")
        print(f"   - Created 4 ticket types")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

