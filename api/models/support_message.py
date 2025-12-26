"""SupportMessage ORM model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.core.db import Base
import enum


class SupportMessageStatus(str, enum.Enum):
    """Support message status enum."""
    NEW = "new"
    RESPONDED = "responded"
    CLOSED = "closed"


class SupportMessage(Base):
    """Support message model."""
    __tablename__ = "support_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String, nullable=False)
    status = Column(SQLEnum(SupportMessageStatus), default=SupportMessageStatus.NEW, nullable=False, index=True)
    admin_response = Column(String, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    responded_by = Column(String, nullable=True)  # Admin username
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="support_messages")

