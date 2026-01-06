"""Admin authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.core.auth import create_access_token, get_current_admin
from api.core.config import settings
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


@router.post("/admin/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Admin login endpoint."""
    # Log authentication attempt (without password for security)
    logger.info(f"Login attempt: username='{login_data.username}'")
    logger.info(f"Expected username: '{settings.ADMIN_USERNAME}', Expected password length: {len(settings.ADMIN_PASSWORD)}")
    logger.info(f"Provided password length: {len(login_data.password)}")
    
    if login_data.username != settings.ADMIN_USERNAME:
        logger.warning(f"Login failed: username mismatch (expected: '{settings.ADMIN_USERNAME}', got: '{login_data.username}')")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if login_data.password != settings.ADMIN_PASSWORD:
        logger.warning(f"Login failed: password mismatch (expected length: {len(settings.ADMIN_PASSWORD)}, got length: {len(login_data.password)})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Login successful for username: '{login_data.username}'")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(access_token=access_token, token_type="bearer")


@router.get("/admin/me", response_model=AdminInfo)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """Get current admin information."""
    return AdminInfo(username=current_admin.get("sub"))
