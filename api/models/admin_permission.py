"""Admin permission ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from api.core.db import Base


class AdminPermission(Base):
    """Admin permission model."""
    __tablename__ = "admin_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("admin_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    resource = Column(String, nullable=False, index=True)
    can_read = Column(Boolean, default=False, nullable=False)
    can_write = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    group = relationship("AdminGroup", back_populates="permissions")
    
    __table_args__ = (
        UniqueConstraint('group_id', 'resource', name='uq_admin_permissions_group_resource'),
        Index("ix_admin_permissions_group_id", "group_id"),
        Index("ix_admin_permissions_resource", "resource"),
    )

