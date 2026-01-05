"""SupportMessagePhoto ORM model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.db import Base


class SupportMessagePhoto(Base):
    """Support message photo model."""
    __tablename__ = "support_message_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    support_message_id = Column(Integer, ForeignKey("support_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    is_admin_photo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    support_message = relationship("SupportMessage", back_populates="photos")


