"""Users endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from api.core.db import get_db
from api.repositories.user_repository import UserRepository
from api.repositories.club_settings_repository import ClubSettingsRepository
from api.api.v1.schemas import UserCreate, UserUpdate, UserResponse, ClubSettingsResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# Specific routes must be defined before generic ones
@router.post("/get-or-create", response_model=UserResponse)
async def get_or_create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Get existing user or create a new one (for backward compatibility with bot)."""
    try:
        logger.info(f"Getting or creating user: telegram_user_id={user_data.telegram_user_id}, username={user_data.username}, first_name={user_data.first_name}, last_name={user_data.last_name}")
        user = UserRepository.get_or_create(db, user_data)
        logger.info(f"User found/created: id={user.id}, telegram_user_id={user.telegram_user_id}, username={user.username}, first_name={user.first_name}, last_name={user.last_name}")
        return UserResponse.model_validate(user)
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting/creating user: {str(e)}"
        )


@router.get("/telegram/{telegram_user_id}", response_model=UserResponse)
async def get_user_by_telegram_id(
    telegram_user_id: int,
    db: Session = Depends(get_db),
):
    """Get user by Telegram user ID."""
    user = UserRepository.get_by_telegram_id(db, telegram_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_user_id {telegram_user_id} not found"
        )
    return UserResponse.model_validate(user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user."""
    try:
        # Check if user with this telegram_user_id already exists
        existing_user = UserRepository.get_by_telegram_id(db, user_data.telegram_user_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with telegram_user_id {user_data.telegram_user_id} already exists"
            )
        
        logger.info(f"Creating user: telegram_user_id={user_data.telegram_user_id}, username={user_data.username}, first_name={user_data.first_name}, last_name={user_data.last_name}")
        user = UserRepository.create(db, user_data)
        logger.info(f"User created: id={user.id}, telegram_user_id={user.telegram_user_id}")
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get user by ID."""
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing user."""
    try:
        logger.info(f"Updating user: id={user_id}, username={user_data.username}, first_name={user_data.first_name}, last_name={user_data.last_name}")
        user = UserRepository.update(db, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        logger.info(f"User updated: id={user.id}, telegram_user_id={user.telegram_user_id}")
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Delete a user."""
    try:
        logger.info(f"Deleting user: id={user_id}")
        deleted = UserRepository.delete(db, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        logger.info(f"User deleted: id={user_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


@router.get("/club-settings", response_model=ClubSettingsResponse)
async def get_club_settings_public(
    db: Session = Depends(get_db),
):
    """Get club settings (public endpoint for bot)."""
    try:
        settings = ClubSettingsRepository.get_settings(db)
        return ClubSettingsResponse.model_validate(settings)
    except Exception as e:
        logger.error(f"Error getting club settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting club settings: {str(e)}"
        )
