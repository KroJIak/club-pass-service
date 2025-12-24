"""Ticket model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TypeDecorator
from sqlalchemy.orm import relationship
import enum
from src.db import Base


class TicketStatus(str, enum.Enum):
    """Ticket status enum."""
    ACTIVE = "active"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    USED = "used"


class TicketStatusType(TypeDecorator):
    """Custom type decorator to ensure enum values are stored as strings."""
    impl = String
    cache_ok = True
    
    def __init__(self, length=20):
        super().__init__(length)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to its string value when binding to database."""
        if value is None:
            return None
        if isinstance(value, TicketStatus):
            # Convert to uppercase to match enum values in database
            # Database enum contains uppercase values (ACTIVE, REFUNDED, etc.)
            return value.value.upper()
        # If it's already a string, convert to uppercase
        return str(value).upper()
    
    def process_result_value(self, value, dialect):
        """Convert string value back to enum when reading from database."""
        if value is None:
            return None
        # Convert to lowercase for case-insensitive matching
        value_lower = str(value).lower()
        return TicketStatus(value_lower)


class Ticket(Base):
    """Ticket model."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # No FK constraint - users table not in this service
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_type_id = Column(Integer, nullable=False)  # No FK constraint - ticket_types table not in this service
    token = Column(String, unique=True, nullable=False, index=True)
    status = Column(TicketStatusType(20), default=TicketStatus.ACTIVE, nullable=False)
    used_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="tickets", lazy="joined")

