"""Club settings model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from api.core.db import Base


class ClubSettings(Base):
    """Settings for club information."""
    __tablename__ = "club_settings"
    
    id = Column(Integer, primary_key=True, index=True, default=1)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    additional_info = Column(String, nullable=True)  # Additional information displayed in club info
    auto_deactivate_events = Column(Boolean, default=True, nullable=False)
    timezone = Column(String, default="Europe/Moscow", nullable=False)  # Default to Moscow timezone
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        # Ensure only one row exists
        # This is enforced at application level
    )

