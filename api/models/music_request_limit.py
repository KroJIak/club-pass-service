"""MusicRequestLimit ORM model."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.db import Base


class MusicRequestLimit(Base):
    """Music request limit model for rate limiting."""
    __tablename__ = "music_request_limits"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True, index=True)
    last_request_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="music_request_limits")
    event = relationship("Event", backref="music_request_limits")

