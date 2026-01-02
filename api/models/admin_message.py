"""AdminMessage ORM model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.db import Base


class AdminMessage(Base):
    """Admin message model."""
    __tablename__ = "admin_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String, nullable=True)  # Nullable because message can be only photos
    sent_by = Column(String, nullable=False, index=True)  # Admin username
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="admin_messages")
    photos = relationship("AdminMessagePhoto", back_populates="admin_message", cascade="all, delete-orphan")

