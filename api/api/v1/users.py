"""Users endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from api.core.config import settings

from api.core.db import get_db
from api.repositories.user_repository import UserRepository
from api.repositories.club_settings_repository import ClubSettingsRepository
from api.repositories.support_message_repository import SupportMessageRepository
from api.repositories.support_message_photo_repository import SupportMessagePhotoRepository
from api.api.v1.schemas import UserCreate, UserUpdate, UserResponse, ClubSettingsResponse, SupportMessageCreate, SupportMessageResponse

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


# IMPORTANT: Specific routes (like /club-settings, /support-messages) must be defined BEFORE generic routes (like /{user_id})
# Otherwise FastAPI will try to match them as /{user_id} and fail with 422
@router.post("/support-messages", response_model=SupportMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_support_message(
    message_data: SupportMessageCreate,
    db: Session = Depends(get_db),
):
    """Create a support message from bot."""
    try:
        logger.info(f"Creating support message: user_id={message_data.user_id}, message_length={len(message_data.message)}")
        support_message = SupportMessageRepository.create(
            db=db,
            user_id=message_data.user_id,
            message=message_data.message,
        )
        
        # Handle photos if provided (already downloaded and saved by bot)
        if message_data.photo_paths:
            logger.info(f"Processing {len(message_data.photo_paths)} photos for support message {support_message.id}")
            from api.services.file_storage_service import get_full_file_path
            import os
            import mimetypes
            
            for photo_path in message_data.photo_paths:
                try:
                    full_path = get_full_file_path(photo_path)
                    if not os.path.exists(full_path):
                        logger.warning(f"Photo file not found: {full_path}")
                        continue
                    
                    # Get file info
                    file_size = os.path.getsize(full_path)
                    filename = os.path.basename(photo_path)
                    
                    # Determine MIME type from extension
                    mime_type, _ = mimetypes.guess_type(full_path)
                    if not mime_type:
                        mime_type = "image/jpeg"
                        
                        # Validate file size
                        max_size = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024
                    if file_size > max_size:
                        logger.warning(f"Photo {photo_path} exceeds max size ({file_size} > {max_size}), skipping")
                            continue
                        
                        # Create photo record
                        SupportMessagePhotoRepository.create(
                            db=db,
                            support_message_id=support_message.id,
                        file_path=photo_path,
                            file_name=filename,
                        file_size=file_size,
                            mime_type=mime_type,
                            is_admin_photo=False,
                        )
                        logger.info(f"Saved photo for support message {support_message.id}: {filename}")
                except Exception as e:
                    logger.error(f"Error processing photo {photo_path}: {e}", exc_info=True)
                    # Continue with other photos even if one fails
        
        # Refresh to get photos
        db.refresh(support_message)
        logger.info(f"Support message created: id={support_message.id}")
        return SupportMessageResponse.model_validate(support_message)
    except Exception as e:
        logger.error(f"Error creating support message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating support message: {str(e)}"
        )


@router.get("/club-settings")
async def get_club_settings_public(
    db: Session = Depends(get_db),
):
    """Get club settings (public endpoint for bot)."""
    import json
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    logger.info("=" * 80)
    logger.info("CLUB SETTINGS ENDPOINT CALLED")
    logger.info("=" * 80)
    
    try:
        logger.info("Step 1: Starting get_club_settings_public function")
        logger.info(f"Step 2: DB session type: {type(db)}")
        
        logger.info("Step 3: Calling ClubSettingsRepository.get_settings(db)")
        settings = ClubSettingsRepository.get_settings(db)
        logger.info(f"Step 4: Settings retrieved successfully")
        logger.info(f"  - Settings object: {settings}")
        logger.info(f"  - Settings type: {type(settings)}")
        logger.info(f"  - Settings id: {settings.id}")
        logger.info(f"  - Settings address: {settings.address}")
        logger.info(f"  - Settings phone: {settings.phone}")
        logger.info(f"  - Settings email: {settings.email}")
        logger.info(f"  - Settings updated_at: {settings.updated_at} (type: {type(settings.updated_at)})")
        
        # Handle case where auto_deactivate_events might not exist in DB
        logger.info("Step 5: Checking auto_deactivate_events attribute")
        try:
            logger.info("  - Attempting getattr(settings, 'auto_deactivate_events', None)")
            auto_deactivate = getattr(settings, 'auto_deactivate_events', None)
            logger.info(f"  - getattr result: {auto_deactivate} (type: {type(auto_deactivate)})")
            if auto_deactivate is None:
                logger.warning("  - auto_deactivate is None, setting to True")
                auto_deactivate = True
            else:
                logger.info(f"  - auto_deactivate value: {auto_deactivate}")
        except AttributeError as e:
            logger.warning(f"  - AttributeError caught: {e}")
            auto_deactivate = True
            logger.warning("  - Setting auto_deactivate to True (default)")
        
        logger.info(f"Step 6: Final auto_deactivate value: {auto_deactivate} (type: {type(auto_deactivate)})")
        
        # Ensure updated_at is a datetime object
        logger.info("Step 7: Processing updated_at")
        updated_at = settings.updated_at
        logger.info(f"  - updated_at value: {updated_at}")
        logger.info(f"  - updated_at type: {type(updated_at)}")
        
        if updated_at is None:
            logger.warning("  - updated_at is None, creating new datetime")
            updated_at = datetime.utcnow()
            logger.info(f"  - Created new datetime: {updated_at}")
        else:
            logger.info(f"  - updated_at is not None, using existing value")
        
        # Serialize datetime to ISO format string
        logger.info("Step 8: Serializing updated_at to ISO format")
        if hasattr(updated_at, 'isoformat'):
            logger.info("  - updated_at has isoformat method")
            updated_at_str = updated_at.isoformat()
            logger.info(f"  - ISO format result: {updated_at_str}")
        else:
            logger.warning("  - updated_at does not have isoformat method, using str()")
            updated_at_str = str(updated_at)
            logger.info(f"  - String result: {updated_at_str}")
        
        logger.info(f"Step 9: Final updated_at_str: {updated_at_str} (type: {type(updated_at_str)})")
        
        # Get timezone
        timezone = getattr(settings, 'timezone', None)
        if timezone is None:
            timezone = "Europe/Moscow"  # Default timezone
        logger.info(f"Step 10: Timezone: {timezone}")
        
        # Build response dict - return directly without Pydantic validation
        logger.info("Step 11: Building response_data dictionary")
        response_data = {
            "id": int(settings.id),
            "address": settings.address if settings.address else None,
            "phone": settings.phone if settings.phone else None,
            "email": settings.email if settings.email else None,
            "auto_deactivate_events": bool(auto_deactivate),
            "timezone": timezone,
            "updated_at": updated_at_str
        }
        
        logger.info("Step 11: Response data dictionary created:")
        for key, value in response_data.items():
            logger.info(f"  - {key}: {value} (type: {type(value)})")
        
        # Validate JSON serialization
        logger.info("Step 12: Testing JSON serialization")
        try:
            json_str = json.dumps(response_data)
            logger.info(f"  - JSON serialization successful: {json_str[:200]}...")
        except Exception as json_error:
            logger.error(f"  - JSON serialization failed: {json_error}")
            raise
        
        logger.info("Step 13: Creating JSONResponse")
        json_response = JSONResponse(content=response_data)
        logger.info(f"  - JSONResponse created: {json_response}")
        logger.info(f"  - JSONResponse status_code: {json_response.status_code}")
        logger.info(f"  - JSONResponse headers: {json_response.headers}")
        
        logger.info("Step 14: Returning JSONResponse")
        logger.info("=" * 80)
        return json_response
        
    except HTTPException as http_exc:
        logger.error("=" * 80)
        logger.error("HTTPException caught in get_club_settings_public")
        logger.error(f"  - Status code: {http_exc.status_code}")
        logger.error(f"  - Detail: {http_exc.detail}")
        logger.error("=" * 80)
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error("EXCEPTION in get_club_settings_public")
        logger.error(f"  - Exception type: {type(e)}")
        logger.error(f"  - Exception message: {str(e)}")
        logger.error(f"  - Exception args: {e.args}")
        import traceback
        logger.error(f"  - Full traceback:\n{traceback.format_exc()}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting club settings: {str(e)}"
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
