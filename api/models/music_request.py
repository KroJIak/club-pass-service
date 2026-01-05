"""MusicRequest ORM model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.db import Base


class MusicRequest(Base):
    """Music request model for wishlist."""
    __tablename__ = "music_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    track_title = Column(String, nullable=False)
    track_artist = Column(String, nullable=False)
    yandex_music_url = Column(String, nullable=True)
    other_source_url = Column(String, nullable=True)
    request_count = Column(Integer, nullable=False, default=1, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="music_requests")
    event = relationship("Event", backref="music_requests")

