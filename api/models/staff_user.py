"""Staff User ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Index
from api.core.db import Base


class StaffUser(Base):
    """Staff User model for QR scanner access."""
    __tablename__ = "staff_users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_staff_users_telegram_user_id", "telegram_user_id"),
    )

