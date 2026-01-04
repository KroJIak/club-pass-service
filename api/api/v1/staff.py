"""Staff endpoints for QR scanner access."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

logger = logging.getLogger(__name__)

from api.core.db import get_db
from api.repositories.staff_user_repository import StaffUserRepository
from api.repositories.ticket_repository import TicketRepository
from api.services.ticket_service import TicketService
from api.api.v1.schemas import (
    StaffAccessCheckResponse,
    StaffUserResponse,
    TicketDetailResponse,
    TicketMarkUsedResponse,
)

router = APIRouter()


def verify_staff_access(telegram_user_id: int, db: Session) -> bool:
    """Verify if user has staff access."""
    staff_user = StaffUserRepository.get_by_telegram_id(db, telegram_user_id)
    return staff_user is not None


@router.get("/staff/check-access", response_model=StaffAccessCheckResponse)
async def check_staff_access(
    telegram_user_id: int = Query(..., description="Telegram user ID"),
    db: Session = Depends(get_db),
):
    """Check if user has staff access."""
    logger.info(f"=== Staff access check started ===")
    logger.info(f"Requested telegram_user_id: {telegram_user_id}")
    logger.info(f"Type of telegram_user_id: {type(telegram_user_id)}")
    
    staff_user = StaffUserRepository.get_by_telegram_id(db, telegram_user_id)
    logger.info(f"Staff user found: {staff_user is not None}")
    if staff_user:
        logger.info(f"Staff user details: id={staff_user.id}, telegram_user_id={staff_user.telegram_user_id}, first_name={staff_user.first_name}, last_name={staff_user.last_name}")
    else:
        logger.warning(f"No staff user found for telegram_user_id={telegram_user_id}")
        # Log all staff users for debugging
        all_staff_users = StaffUserRepository.get_all(db)
        logger.info(f"Total staff users in DB: {len(all_staff_users)}")
        for su in all_staff_users:
            logger.info(f"  - Staff user: id={su.id}, telegram_user_id={su.telegram_user_id}")
    
    has_access = staff_user is not None
    logger.info(f"has_access result: {has_access}")
    
    response = StaffAccessCheckResponse(
        has_access=has_access,
        staff_user=StaffUserResponse.model_validate(staff_user) if staff_user else None
    )
    logger.info(f"Response: has_access={response.has_access}, staff_user={response.staff_user.id if response.staff_user else None}")
    logger.info(f"=== Staff access check completed ===")
    
    return response


@router.get("/staff/tickets/token/{token}", response_model=TicketDetailResponse)
async def get_ticket_by_token_staff(
    token: str,
    telegram_user_id: int = Query(..., description="Telegram user ID"),
    db: Session = Depends(get_db),
):
    """Get ticket by token (staff only)."""
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
    telegram_user_id: int = Query(..., description="Telegram user ID"),
    db: Session = Depends(get_db),
):
    """Mark ticket as used (staff only)."""
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

