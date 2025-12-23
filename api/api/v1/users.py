"""Users endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.repositories.user_repository import UserRepository
from api.api.v1.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_or_update_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Create or update a user."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creating/updating user: telegram_user_id={user_data.telegram_user_id}, username={user_data.username}, first_name={user_data.first_name}, last_name={user_data.last_name}")
        user = UserRepository.get_or_create(db, user_data)
        logger.info(f"User created/updated: id={user.id}, telegram_user_id={user.telegram_user_id}, username={user.username}, first_name={user.first_name}, last_name={user.last_name}")
        response = UserResponse.model_validate(user)
        logger.info(f"UserResponse created successfully: id={response.id}")
        return response
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating user: {str(e)}"
        )
