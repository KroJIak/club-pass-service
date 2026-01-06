"""Users endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging
from api.core.config import settings

from api.core.db import get_db
from api.repositories.user_repository import UserRepository
from api.repositories.club_settings_repository import ClubSettingsRepository
from api.repositories.support_message_repository import SupportMessageRepository
from api.repositories.support_message_photo_repository import SupportMessagePhotoRepository
from api.repositories.menu_photo_repository import MenuPhotoRepository
from api.repositories.ticket_repository import TicketRepository
from api.repositories.music_request_repository import MusicRequestRepository
from api.repositories.music_request_limit_repository import MusicRequestLimitRepository
from api.repositories.event_repository import EventRepository
from api.api.v1.schemas import (
    UserCreate, UserUpdate, UserResponse, ClubSettingsResponse, SupportMessageCreate, SupportMessageResponse,
    MenuPhotoResponse, MenuPhotoListResponse, MusicRequestCreate, MusicRequestResponse
)
from api.models.ticket import TicketStatus
from datetime import datetime
import pytz

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


# IMPORTANT: Specific routes (like /club-settings, /support-messages, /menu-photos) must be defined BEFORE generic routes (like /{user_id})
# Otherwise FastAPI will try to match them as /{user_id} and fail with 422
@router.get("/menu-photos")
async def get_menu_photos_public(
    db: Session = Depends(get_db),
):
    """Get all active menu photos (public endpoint for bot)."""
    logger.info("=" * 80)
    logger.info("MENU PHOTOS ENDPOINT CALLED")
    logger.info("=" * 80)
    
    try:
        logger.info("Step 1: Calling MenuPhotoRepository.get_all(db)")
        photos = MenuPhotoRepository.get_all(db)
        logger.info(f"Step 2: Retrieved {len(photos)} photos from repository")
        
        # Convert ORM objects to Pydantic models
        photo_responses = []
        for i, photo in enumerate(photos):
            try:
                logger.info(f"Step 3.{i+1}: Validating photo {photo.id}")
                logger.info(f"  - Photo ID: {photo.id}")
                logger.info(f"  - File path: {photo.file_path}")
                logger.info(f"  - File name: {photo.file_name}")
                logger.info(f"  - File size: {photo.file_size}")
                logger.info(f"  - MIME type: {photo.mime_type}")
                logger.info(f"  - Display order: {photo.display_order}")
                logger.info(f"  - Created at: {photo.created_at} (type: {type(photo.created_at)})")
                logger.info(f"  - Updated at: {photo.updated_at} (type: {type(photo.updated_at)})")
                logger.info(f"  - Is deleted: {photo.is_deleted}")
                logger.info(f"  - Deleted at: {photo.deleted_at}")
                
                photo_response = MenuPhotoResponse.model_validate(photo)
                logger.info(f"Step 3.{i+1}: Photo {photo.id} validated successfully")
                photo_responses.append(photo_response)
            except Exception as e:
                logger.error(f"Step 3.{i+1}: Error validating photo {photo.id}: {e}", exc_info=True)
                logger.error(f"  - Photo object: {photo}")
                logger.error(f"  - Photo dict: {photo.__dict__ if hasattr(photo, '__dict__') else 'N/A'}")
                continue
        
        logger.info(f"Step 4: Created {len(photo_responses)} photo responses")
        
        result = MenuPhotoListResponse(photos=photo_responses)
        logger.info(f"Step 5: Created MenuPhotoListResponse with {len(result.photos)} photos")
        logger.info(f"Step 6: Converting to dict")
        result_dict = result.model_dump()
        logger.info(f"Step 7: Result dict: {result_dict}")
        logger.info(f"Step 8: Returning response")
        logger.info("=" * 80)
        
        return result_dict
    except Exception as e:
        logger.error(f"CRITICAL ERROR in get_menu_photos_public: {e}", exc_info=True)
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception args: {e.args}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


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
        
        # Get additional_info
        additional_info = getattr(settings, 'additional_info', None)
        logger.info(f"Step 10.5: Additional info: {additional_info}")
        
        # Build response dict - return directly without Pydantic validation
        logger.info("Step 11: Building response_data dictionary")
        response_data = {
            "id": int(settings.id),
            "address": settings.address if settings.address else None,
            "phone": settings.phone if settings.phone else None,
            "email": settings.email if settings.email else None,
            "additional_info": additional_info if additional_info else None,
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


def _get_valid_event_for_user(db: Session, user_id: int) -> Optional[object]:
    """Helper function to get valid active event for user."""
    # Get all used tickets for the user
    tickets = TicketRepository.get_by_user_id(db, user_id, active_only=False)
    used_tickets = [t for t in tickets if t.status == TicketStatus.USED]
    
    if not used_tickets:
        return None
    
    # Find an active event that hasn't ended
    valid_event = None
    current_time = datetime.utcnow()
    
    # Get timezone from club settings
    from api.utils.timezone import get_current_time_in_timezone
    current_time_tz = get_current_time_in_timezone(db)
    
    # Get timezone string
    settings = ClubSettingsRepository.get_settings(db)
    timezone_str = settings.timezone or "Europe/Moscow"
    tz = pytz.timezone(timezone_str)
    current_time_aware = tz.localize(current_time_tz)
    
    for ticket in used_tickets:
        event = ticket.event
        if not event or not event.is_active:
            continue
        
        # Parse end_date and end_time
        try:
            end_dt = datetime.strptime(f"{event.end_date} {event.end_time}", "%d.%m.%Y %H:%M")
            end_dt_aware = tz.localize(end_dt)
            
            # Check if event hasn't ended
            if end_dt_aware > current_time_aware:
                valid_event = event
                break
        except Exception as e:
            logger.warning(f"Error parsing event end date/time: {e}")
            continue
    
    return valid_event


@router.get("/music-requests/check-limit")
async def check_music_request_limit(
    telegram_user_id: int,
    db: Session = Depends(get_db),
):
    """Check if user can make a music request (rate limit check)."""
    try:
        # Get user by telegram_user_id
        user = UserRepository.get_by_telegram_id(db, telegram_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is staff - staff users can always add music
        from api.repositories.staff_user_repository import StaffUserRepository
        is_staff = StaffUserRepository.get_by_telegram_id(db, telegram_user_id) is not None
        
        # Get valid event - for staff, get any active event; for regular users, require used ticket
        valid_event = None
        if is_staff:
            # Staff users can use any active event
            from api.repositories.event_repository import EventRepository
            active_events = EventRepository.get_all_active(db)
            if active_events:
                # Get timezone for date comparison
                from api.utils.timezone import get_current_time_in_timezone
                current_time_tz = get_current_time_in_timezone(db)
                settings = ClubSettingsRepository.get_settings(db)
                timezone_str = settings.timezone or "Europe/Moscow"
                tz = pytz.timezone(timezone_str)
                current_time_aware = tz.localize(current_time_tz)
                
                # Find first active event that hasn't ended
                for event in active_events:
                    if event.end_date and event.end_time:
                        try:
                            end_dt = datetime.strptime(f"{event.end_date} {event.end_time}", "%d.%m.%Y %H:%M")
                            end_dt_aware = tz.localize(end_dt)
                            if end_dt_aware > current_time_aware:
                                valid_event = event
                                break
                        except Exception:
                            continue
                    else:
                        # Event without end date/time - use it
                        valid_event = event
                        break
        else:
            # Regular users need used ticket
            valid_event = _get_valid_event_for_user(db, user.id)
        
        if not valid_event:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No active event found. You need to be in the club to add music requests."
            )
        
        # Check rate limit (5 minutes) - skip for staff users
        can_make = True
        if not is_staff:
            can_make = MusicRequestLimitRepository.can_make_request(db, user.id, valid_event.id, cooldown_minutes=5)
        
        return {
            "can_make_request": can_make,
            "message": "You can add music requests once every 5 minutes" if not can_make else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking music request limit: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking music request limit: {str(e)}"
        )


@router.post("/music-requests", response_model=MusicRequestResponse)
async def create_music_request(
    request_data: MusicRequestCreate,
    telegram_user_id: int,
    db: Session = Depends(get_db),
):
    """Create a music request. Requires user to have a used ticket for an active event."""
    try:
        # Get user by telegram_user_id
        user = UserRepository.get_by_telegram_id(db, telegram_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is staff - staff users can always add music
        from api.repositories.staff_user_repository import StaffUserRepository
        is_staff = StaffUserRepository.get_by_telegram_id(db, telegram_user_id) is not None
        
        # Get valid event - for staff, get any active event; for regular users, require used ticket
        valid_event = None
        if is_staff:
            # Staff users can use any active event
            from api.repositories.event_repository import EventRepository
            active_events = EventRepository.get_all_active(db)
            if active_events:
                # Get timezone for date comparison
                from api.utils.timezone import get_current_time_in_timezone
                current_time_tz = get_current_time_in_timezone(db)
                settings = ClubSettingsRepository.get_settings(db)
                timezone_str = settings.timezone or "Europe/Moscow"
                tz = pytz.timezone(timezone_str)
                current_time_aware = tz.localize(current_time_tz)
                
                # Find first active event that hasn't ended
                for event in active_events:
                    if event.end_date and event.end_time:
                        try:
                            end_dt = datetime.strptime(f"{event.end_date} {event.end_time}", "%d.%m.%Y %H:%M")
                            end_dt_aware = tz.localize(end_dt)
                            if end_dt_aware > current_time_aware:
                                valid_event = event
                                break
                        except Exception:
                            continue
                    else:
                        # Event without end date/time - use it
                        valid_event = event
                        break
        else:
            # Regular users need used ticket
            valid_event = _get_valid_event_for_user(db, user.id)
        
        if not valid_event:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You need to be in the club to add music requests"
            )
        
        # Check if this track already exists in queue
        from api.models.music_queue import MusicQueue
        existing_queue_item = db.query(MusicQueue).filter(
            MusicQueue.track_title == request_data.track_title,
            MusicQueue.track_artist == (request_data.track_artist or ""),
            MusicQueue.is_deleted == False
        ).first()
        
        if existing_queue_item:
            # Track is in queue, return message that it's already in queue
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот трек уже в очереди и скоро будет включён"
            )
        
        # Check if request already exists for this event (in wishlist)
        existing_request = MusicRequestRepository.get_by_title_artist(
            db, valid_event.id, request_data.track_title, request_data.track_artist or ""
        )
        
        if existing_request:
            # Track is in wishlist, user cannot add it again
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже выбирали данную песню"
            )
        
        # Track is not in queue and not in wishlist - user can add it
        # Create new request
        music_request = MusicRequestRepository.create(
            db,
            user_id=user.id,
            event_id=valid_event.id,
            track_title=request_data.track_title,
            track_artist=request_data.track_artist or "",
            yandex_music_url=request_data.yandex_music_url,
            other_source_url=request_data.other_source_url,
        )
        
        # Update last request time (only for non-staff users, but updating doesn't hurt)
        if not is_staff:
            MusicRequestLimitRepository.update_last_request(db, user.id, valid_event.id)
        
        return MusicRequestResponse.model_validate(music_request)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating music request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating music request: {str(e)}"
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
    hard: bool = False,
    db: Session = Depends(get_db),
):
    """Delete a user (soft delete by default, hard delete if hard=true)."""
    try:
        logger.info(f"Deleting user: id={user_id}, hard={hard}")
        deleted = UserRepository.delete(db, user_id, hard=hard)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        logger.info(f"User deleted: id={user_id}, hard={hard}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
