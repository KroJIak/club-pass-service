"""Staff endpoints for QR scanner access."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

logger = logging.getLogger(__name__)

from api.core.db import get_db
from api.core.config import settings
from api.repositories.staff_user_repository import StaffUserRepository
from api.repositories.ticket_repository import TicketRepository
from api.services.ticket_service import TicketService
from api.utils.telegram_validation import validate_telegram_init_data, extract_user_id_from_init_data
from api.api.v1.schemas import (
    StaffAccessCheckRequest,
    StaffRequestWithInitData,
    StaffAccessCheckResponse,
    StaffUserResponse,
    TicketDetailResponse,
    TicketMarkUsedResponse,
)

router = APIRouter()


def validate_init_data_and_get_user_id(init_data: str) -> int:
    """
    Validate initData and extract user_id.
    
    Raises:
        HTTPException: If validation fails
    """
    if not settings.STAFF_BOT_TOKEN:
        logger.error("STAFF_BOT_TOKEN not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: STAFF_BOT_TOKEN not set"
        )
    
    logger.debug(f"STAFF_BOT_TOKEN length: {len(settings.STAFF_BOT_TOKEN)}")
    logger.debug(f"STAFF_BOT_TOKEN prefix: {settings.STAFF_BOT_TOKEN[:10]}...")
    logger.debug(f"initData length: {len(init_data)}")
    logger.debug(f"initData preview: {init_data[:100]}...")
    
    # Try with STAFF_BOT_TOKEN first
    try:
        validated_data = validate_telegram_init_data(init_data, settings.STAFF_BOT_TOKEN)
        user = validated_data.get('user')
        
        if not user or 'id' not in user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User data not found in initData"
            )
        
        return int(user['id'])
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"InitData validation failed with STAFF_BOT_TOKEN: {e}")
        
        # Try with main bot token as fallback
        if settings.TELEGRAM_BOT_TOKEN:
            logger.debug(f"Trying with main bot token (length: {len(settings.TELEGRAM_BOT_TOKEN)})...")
            try:
                validated_data = validate_telegram_init_data(init_data, settings.TELEGRAM_BOT_TOKEN)
                user = validated_data.get('user')
                
                if not user or 'id' not in user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User data not found in initData"
                    )
                
                logger.info(f"InitData validated successfully with main bot token")
                return int(user['id'])
            except (ValueError, HTTPException) as e2:
                logger.warning(f"InitData validation also failed with main bot token: {e2}")
        else:
            logger.warning("TELEGRAM_BOT_TOKEN not configured, cannot try fallback")
        
        logger.debug(f"Full initData: {init_data}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid initData signature: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during initData validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating initData"
        )


def verify_staff_access(telegram_user_id: int, db: Session) -> bool:
    """Verify if user has staff access."""
    staff_user = StaffUserRepository.get_by_telegram_id(db, telegram_user_id)
    return staff_user is not None


@router.post("/staff/check-access", response_model=StaffAccessCheckResponse)
async def check_staff_access(
    request: StaffAccessCheckRequest,
    db: Session = Depends(get_db),
):
    """Check if user has staff access. Validates Telegram initData signature."""
    logger.info(f"=== Staff access check started ===")
    
    # Validate initData signature and extract user_id
    telegram_user_id = validate_init_data_and_get_user_id(request.init_data)
    logger.info(f"Validated telegram_user_id: {telegram_user_id}")
    
    # Check if user has staff access
    staff_user = StaffUserRepository.get_by_telegram_id(db, telegram_user_id)
    logger.info(f"Staff user found: {staff_user is not None}")
    if staff_user:
        logger.info(f"Staff user details: id={staff_user.id}, telegram_user_id={staff_user.telegram_user_id}, first_name={staff_user.first_name}, last_name={staff_user.last_name}")
    else:
        logger.warning(f"No staff user found for telegram_user_id={telegram_user_id}")
    
    has_access = staff_user is not None
    logger.info(f"has_access result: {has_access}")
    
    response = StaffAccessCheckResponse(
        has_access=has_access,
        staff_user=StaffUserResponse.model_validate(staff_user) if staff_user else None
    )
    logger.info(f"Response: has_access={response.has_access}, staff_user={response.staff_user.id if response.staff_user else None}")
    logger.info(f"=== Staff access check completed ===")
    
    return response


@router.post("/staff/tickets/token/{token}", response_model=TicketDetailResponse)
async def get_ticket_by_token_staff(
    token: str,
    request: StaffRequestWithInitData,
    db: Session = Depends(get_db),
):
    """Get ticket by token (staff only). Validates Telegram initData signature."""
    # Validate initData signature and extract user_id
    telegram_user_id = validate_init_data_and_get_user_id(request.init_data)
    
    # Verify staff access
    if not verify_staff_access(telegram_user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You are not authorized to use staff features."
        )
    
    ticket = TicketService.get_ticket_by_token(db, token)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with token {token} not found"
        )
    return ticket


@router.post("/staff/tickets/{ticket_id}/mark-used", response_model=TicketMarkUsedResponse)
async def mark_ticket_as_used_staff(
    ticket_id: int,
    request: StaffRequestWithInitData,
    db: Session = Depends(get_db),
):
    """Mark ticket as used (staff only). Validates Telegram initData signature."""
    # Validate initData signature and extract user_id
    telegram_user_id = validate_init_data_and_get_user_id(request.init_data)
    
    # Verify staff access
    if not verify_staff_access(telegram_user_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You are not authorized to use staff features."
        )
    
    ticket = TicketService.mark_ticket_as_used(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    # Ensure used_at is set with timezone
    if not ticket.used_at:
        from api.utils.timezone import get_current_time_in_timezone
        ticket.used_at = get_current_time_in_timezone(db)
        db.commit()
        db.refresh(ticket)
    
    return TicketMarkUsedResponse(
        ticket_id=ticket.id,
        status=ticket.status,
        used_at=ticket.used_at,
        message="Ticket marked as used successfully"
    )

