"""Admin group repository."""
from typing import Optional, List
from sqlalchemy.orm import Session
from api.models.admin_group import AdminGroup


class AdminGroupRepository:
    """Repository for admin group operations."""
    
    @staticmethod
    def get_by_id(db: Session, group_id: int) -> Optional[AdminGroup]:
        """Get group by ID."""
        return db.query(AdminGroup).filter(
            AdminGroup.id == group_id,
            AdminGroup.is_deleted == False
        ).first()
    
    @staticmethod
    def get_all(db: Session) -> List[AdminGroup]:
        """Get all groups."""
        return db.query(AdminGroup).filter(
            AdminGroup.is_deleted == False
        ).order_by(AdminGroup.created_at.desc()).all()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[AdminGroup]:
        """Get group by name."""
        return db.query(AdminGroup).filter(
            AdminGroup.name == name,
            AdminGroup.is_deleted == False
        ).first()
    
    @staticmethod
    def create(db: Session, name: str, description: Optional[str] = None) -> AdminGroup:
        """Create a new group."""
        group = AdminGroup(
            name=name,
            description=description
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def update(db: Session, group_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[AdminGroup]:
        """Update group."""
        group = AdminGroupRepository.get_by_id(db, group_id)
        if not group:
            return None
        
        if name is not None:
            group.name = name
        if description is not None:
            group.description = description
        
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def delete(db: Session, group_id: int, hard: bool = False) -> bool:
        """Delete group (soft delete by default)."""
        group = AdminGroupRepository.get_by_id(db, group_id)
        if not group:
            return False
        
        if hard:
            db.delete(group)
        else:
            from datetime import datetime
            group.is_deleted = True
            group.deleted_at = datetime.utcnow()
        
        db.commit()
        return True

