"""Event ORM model and Pydantic schemas."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from api.core.db import Base


class Event(Base):
    """Event model."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(String, nullable=False)  # Format: "DD.MM.YYYY"
    time = Column(String, nullable=False)  # Format: "HH:MM"
    djs = Column(JSON, nullable=True)  # List of DJ names: ["DJ. DIMSY", "EMPYZ", ...]
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="event")
