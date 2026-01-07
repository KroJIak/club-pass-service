"""Admin group ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from api.core.db import Base


class AdminGroup(Base):
    """Admin group model."""
    __tablename__ = "admin_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    accounts = relationship("AdminAccount", back_populates="group", cascade="all, delete-orphan")
    permissions = relationship("AdminPermission", back_populates="group", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_admin_groups_name", "name"),
    )

