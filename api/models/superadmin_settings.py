"""Superadmin settings ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from api.core.db import Base


class SuperadminSettings(Base):
    """Superadmin settings model."""
    __tablename__ = "superadmin_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    language = Column(String(2), default='ru', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

