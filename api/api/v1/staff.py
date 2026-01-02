"""Staff endpoints for QR scanner access."""
import logging
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
    staff_user = StaffUserRepository.get_by_telegram_id(db, telegram_user_id)
    has_access = staff_user is not None
    
    return StaffAccessCheckResponse(
        has_access=has_access,
        staff_user=StaffUserResponse.model_validate(staff_user) if staff_user else None
    )


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
    
    return TicketMarkUsedResponse(
        id=ticket.id,
        status=ticket.status.value,
        used_at=ticket.used_at,
    )

