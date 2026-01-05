"""MusicQueue ORM model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from api.core.db import Base


class MusicQueue(Base):
    """Music queue model."""
    __tablename__ = "music_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    track_title = Column(String, nullable=False)
    track_artist = Column(String, nullable=False)
    yandex_music_url = Column(String, nullable=True)
    other_source_url = Column(String, nullable=True)
    queue_order = Column(Integer, nullable=False, index=True)
    request_count = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

