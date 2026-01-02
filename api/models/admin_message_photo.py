"""AdminMessagePhoto ORM model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.db import Base


class AdminMessagePhoto(Base):
    """Admin message photo model."""
    __tablename__ = "admin_message_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_message_id = Column(Integer, ForeignKey("admin_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    admin_message = relationship("AdminMessage", back_populates="photos")

