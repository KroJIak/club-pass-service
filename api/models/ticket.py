"""Ticket ORM model and Pydantic schemas."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TypeDecorator, Boolean
from sqlalchemy.orm import relationship
import enum
from api.core.db import Base


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
            return value.value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string value back to enum when reading from database."""
        if value is None:
            return None
        # Convert to lowercase for case-insensitive matching (handles both old and new values)
        value_lower = str(value).lower()
        return TicketStatus(value_lower)


class Ticket(Base):
    """Ticket model."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="RESTRICT"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)  # For QR code
    status = Column(TicketStatusType(20), default=TicketStatus.ACTIVE, nullable=False)
    used_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    
    __table_args__ = (
        # Index for token lookup
        # Index("idx_tickets_token", "token"),  # Already indexed via unique=True
    )
