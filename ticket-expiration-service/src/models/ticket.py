"""Ticket model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from src.db import Base


class TicketStatus(str, enum.Enum):
    """Ticket status enum."""
    ACTIVE = "active"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Ticket(Base):
    """Ticket model."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="RESTRICT"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="tickets")

