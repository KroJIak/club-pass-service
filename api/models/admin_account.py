"""Admin account ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from api.core.db import Base


class AdminAccount(Base):
    """Admin account model."""
    __tablename__ = "admin_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("admin_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    language = Column(String(2), default='ru', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    group = relationship("AdminGroup", back_populates="accounts")
    
    __table_args__ = (
        Index("ix_admin_accounts_username", "username"),
        Index("ix_admin_accounts_group_id", "group_id"),
    )

