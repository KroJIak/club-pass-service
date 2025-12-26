"""Event model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from src.db import Base


class Event(Base):
    """Event model."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(String, nullable=False)  # Format: "DD.MM.YYYY"
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_date = Column(String, nullable=True)  # Format: "DD.MM.YYYY"
    end_time = Column(String, nullable=True)  # Format: "HH:MM"
    djs = Column(JSON, nullable=True)  # List of DJ names
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="event", lazy="dynamic")
