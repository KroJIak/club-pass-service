"""Tickets CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.services.ticket_service import TicketService
from api.api.v1.schemas import TicketListResponse, TicketDetailResponse, TicketRefundRequest, TicketRefundResponse, TicketMarkUsedRequest, TicketMarkUsedResponse
from api.models.ticket import TicketStatus
from datetime import datetime

router = APIRouter()


@router.get("/users/{user_id}/tickets", response_model=TicketListResponse)
async def get_user_tickets(
    user_id: int,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """Get tickets for a user."""
    tickets = TicketService.get_user_tickets(db, user_id, active_only=active_only)
    
    return TicketListResponse(
        tickets=[TicketDetailResponse.model_validate(ticket) for ticket in tickets]
    )


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """Get ticket by ID with all related data."""
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    return ticket


@router.post("/tickets/{ticket_id}/refund", response_model=TicketRefundResponse)
async def refund_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """Refund a ticket (mark as refunded)."""
    try:
        ticket = TicketService.refund_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found"
            )
        
        return TicketRefundResponse(
            ticket_id=ticket.id,
            status=ticket.status,
            refunded_at=ticket.refunded_at or datetime.utcnow(),
            message="Ticket refunded successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/tickets/{ticket_id}/mark-used", response_model=TicketMarkUsedResponse)
async def mark_ticket_as_used(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """Mark ticket as used."""
    ticket = TicketService.mark_ticket_as_used(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    return TicketMarkUsedResponse(
        ticket_id=ticket.id,
        is_used=ticket.is_used,
        used_at=ticket.used_at or datetime.utcnow(),
        message="Ticket marked as used successfully"
    )
