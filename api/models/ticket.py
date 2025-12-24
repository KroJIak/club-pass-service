"""Ticket ORM model and Pydantic schemas."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
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


class Ticket(Base):
    """Ticket model."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="RESTRICT"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)  # For QR code
    status = Column(SQLEnum(TicketStatus, native_enum=False, create_constraint=False, length=20), default=TicketStatus.ACTIVE, nullable=False)
    used_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    
    __table_args__ = (
        # Index for token lookup
        # Index("idx_tickets_token", "token"),  # Already indexed via unique=True
    )
