"""Expiration service settings model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime
from api.core.db import Base


class ExpirationSettings(Base):
    """Settings for expiration service."""
    __tablename__ = "expiration_settings"
    
    id = Column(Integer, primary_key=True, index=True, default=1)
    ticket_expiration_enabled = Column(Boolean, default=True, nullable=False)
    event_deactivation_enabled = Column(Boolean, default=True, nullable=False)
    check_interval_minutes = Column(Integer, default=30, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        # Ensure only one row exists
        # This is enforced at application level
    )

