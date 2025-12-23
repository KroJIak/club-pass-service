"""Promocode ORM model and Pydantic schemas."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Integer as SQLInteger
from api.core.db import Base


class Promocode(Base):
    """Promocode model."""
    __tablename__ = "promocodes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Numeric(5, 2), nullable=True)  # e.g., 10.00 for 10%
    discount_amount = Column(Numeric(10, 2), nullable=True)  # Fixed discount amount
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    usage_limit = Column(SQLInteger, nullable=True)  # None = unlimited
    usage_count = Column(SQLInteger, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
