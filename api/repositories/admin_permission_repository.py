"""Admin permission repository."""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from api.models.admin_permission import AdminPermission


class AdminPermissionRepository:
    """Repository for admin permission operations."""
    
    @staticmethod
    def get_by_id(db: Session, permission_id: int) -> Optional[AdminPermission]:
        """Get permission by ID."""
        return db.query(AdminPermission).filter(
            AdminPermission.id == permission_id
        ).first()
    
    @staticmethod
    def get_by_group_and_resource(db: Session, group_id: int, resource: str) -> Optional[AdminPermission]:
        """Get permission by group and resource."""
        return db.query(AdminPermission).filter(
            AdminPermission.group_id == group_id,
            AdminPermission.resource == resource
        ).first()
    
    @staticmethod
    def get_all_by_group(db: Session, group_id: int) -> List[AdminPermission]:
        """Get all permissions for a group."""
        return db.query(AdminPermission).filter(
            AdminPermission.group_id == group_id
        ).all()
    
    @staticmethod
    def get_permissions_dict(db: Session, group_id: int) -> Dict[str, Dict[str, bool]]:
        """Get all permissions for a group as a dictionary."""
        permissions = AdminPermissionRepository.get_all_by_group(db, group_id)
        result = {}
        for perm in permissions:
            result[perm.resource] = {
                "can_read": perm.can_read,
                "can_write": perm.can_write,
                "can_delete": perm.can_delete
            }
        return result
    
    @staticmethod
    def create_or_update(db: Session, group_id: int, resource: str, can_read: bool = False, 
                         can_write: bool = False, can_delete: bool = False) -> AdminPermission:
        """Create or update permission."""
        permission = AdminPermissionRepository.get_by_group_and_resource(db, group_id, resource)
        
        if permission:
            permission.can_read = can_read
            permission.can_write = can_write
            permission.can_delete = can_delete
        else:
            permission = AdminPermission(
                group_id=group_id,
                resource=resource,
                can_read=can_read,
                can_write=can_write,
                can_delete=can_delete
            )
            db.add(permission)
        
        db.commit()
        db.refresh(permission)
        return permission
    
    @staticmethod
    def bulk_update(db: Session, group_id: int, permissions: List[Dict[str, any]]) -> List[AdminPermission]:
        """Bulk update permissions for a group."""
        result = []
        for perm_data in permissions:
            perm = AdminPermissionRepository.create_or_update(
                db,
                group_id,
                perm_data["resource"],
                perm_data.get("can_read", False),
                perm_data.get("can_write", False),
                perm_data.get("can_delete", False)
            )
            result.append(perm)
        return result
    
    @staticmethod
    def delete(db: Session, permission_id: int) -> bool:
        """Delete permission."""
        permission = AdminPermissionRepository.get_by_id(db, permission_id)
        if not permission:
            return False
        
        db.delete(permission)
        db.commit()
        return True
    
    @staticmethod
    def delete_by_group_and_resource(db: Session, group_id: int, resource: str) -> bool:
        """Delete permission by group and resource."""
        permission = AdminPermissionRepository.get_by_group_and_resource(db, group_id, resource)
        if not permission:
            return False
        
        db.delete(permission)
        db.commit()
        return True

