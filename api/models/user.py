"""User ORM model and Pydantic schemas."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from api.core.db import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    
    __table_args__ = (
        Index("idx_users_telegram_user_id", "telegram_user_id"),
    )
