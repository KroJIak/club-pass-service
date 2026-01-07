"""Permission checking utilities."""
from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from api.core.auth import get_current_admin


def has_permission(permissions: Dict[str, Dict[str, bool]], resource: str, action: str) -> bool:
    """
    Check if user has permission for a resource and action.
    
    Args:
        permissions: Permissions dictionary from token
        resource: Resource name (e.g., "users", "events")
        action: Action name ("read", "write", "delete")
    
    Returns:
        True if user has permission, False otherwise
    """
    # Empty permissions dict means superadmin (all permissions)
    if not permissions:
        return True
    
    resource_perms = permissions.get(resource)
    if not resource_perms:
        return False
    
    if action == "read":
        return resource_perms.get("can_read", False)
    elif action == "write":
        return resource_perms.get("can_write", False)
    elif action == "delete":
        return resource_perms.get("can_delete", False)
    
    return False


def require_permission(resource: str, action: str):
    """
    Dependency factory for checking permissions.
    
    Args:
        resource: Resource name (e.g., "users", "events")
        action: Action name ("read", "write", "delete")
    
    Returns:
        Dependency function
    """
    async def check_permission(current_admin: dict = Depends(get_current_admin)):
        """Check if current admin has required permission."""
        # Superadmin has all permissions
        if current_admin.get("is_superadmin"):
            return True
        
        permissions = current_admin.get("permissions", {})
        if not has_permission(permissions, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource}"
            )
        return True
    
    return Depends(check_permission)

