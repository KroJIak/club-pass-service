"""Admin authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from api.core.auth import create_access_token, get_current_admin
from api.core.config import settings
from datetime import timedelta

router = APIRouter()


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
    if login_data.username != settings.ADMIN_USERNAME or login_data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
