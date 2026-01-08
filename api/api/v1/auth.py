"""Admin authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
from api.core.auth import create_access_token, get_current_admin, verify_password
from api.core.config import settings
from api.core.db import get_db
from api.repositories.admin_account_repository import AdminAccountRepository
from api.repositories.admin_permission_repository import AdminPermissionRepository
from api.repositories.superadmin_settings_repository import SuperadminSettingsRepository
from datetime import timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str = "bearer"


class AdminInfo(BaseModel):
    """Admin information schema."""
    username: str
    is_superadmin: bool
    group_id: Optional[int] = None
    language: str = 'ru'
    permissions: Optional[Dict[str, Dict[str, bool]]] = None


@router.post("/admin/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint. Supports both superadmin and accounts from database."""
    logger.info(f"Login attempt: username='{login_data.username}'")
    
    # Check if superadmin
    is_superadmin = login_data.username == settings.ADMIN_USERNAME
    
    if is_superadmin:
        # Verify superadmin password
        if login_data.password != settings.ADMIN_PASSWORD:
            logger.warning(f"Login failed: superadmin password mismatch")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Login successful for superadmin: '{login_data.username}'")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": login_data.username,
                "is_superadmin": True,
                "group_id": None,
                "permissions": {}
            },
            expires_delta=access_token_expires
        )
        
        return LoginResponse(access_token=access_token, token_type="bearer")
    
    # Check account in database
    account = AdminAccountRepository.get_by_username(db, login_data.username)
    if not account:
        logger.warning(f"Login failed: account not found for username: '{login_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not account.is_active:
        logger.warning(f"Login failed: account is inactive for username: '{login_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, account.password_hash):
        logger.warning(f"Login failed: password mismatch for username: '{login_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Load permissions
    permissions = AdminPermissionRepository.get_permissions_dict(db, account.group_id)
    
    logger.info(f"Login successful for account: '{login_data.username}' (group_id: {account.group_id})")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": login_data.username,
            "is_superadmin": False,
            "group_id": account.group_id,
            "permissions": permissions,
            "account_id": account.id
        },
        expires_delta=access_token_expires
    )
    
    return LoginResponse(access_token=access_token, token_type="bearer")


@router.get("/admin/me", response_model=AdminInfo)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get current admin information with permissions."""
    language = 'ru'  # Default language
    username = current_admin.get("sub")
    
    # Get language from database
    if current_admin.get("is_superadmin", False):
        # For superadmin, get from superadmin_settings table
        settings = SuperadminSettingsRepository.get_by_username(db, username)
        if settings:
            language = settings.language
    else:
        # For regular admin, get from admin_accounts table
        account = AdminAccountRepository.get_by_username(db, username)
        if account:
            language = account.language
    
    return AdminInfo(
        username=username,
        is_superadmin=current_admin.get("is_superadmin", False),
        group_id=current_admin.get("group_id"),
        language=language,
        permissions=current_admin.get("permissions")
    )


@router.get("/admin/permissions")
async def get_permissions(current_admin: dict = Depends(get_current_admin)):
    """Get current admin permissions."""
    return {
        "is_superadmin": current_admin.get("is_superadmin", False),
        "permissions": current_admin.get("permissions", {})
    }
