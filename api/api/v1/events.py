"""Events CRUD endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.repositories.event_repository import EventRepository
from api.repositories.ticket_type_repository import TicketTypeRepository
from api.api.v1.schemas import EventResponse, EventListResponse, TicketTypeListResponse, TicketTypeResponse

router = APIRouter()


@router.get("/events", response_model=EventListResponse)
async def get_events(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """Get list of events."""
    if active_only:
        events = EventRepository.get_all_active(db)
    else:
        events = EventRepository.get_all_active(db)  # For now, only active
    
    return EventListResponse(
        events=[EventResponse.model_validate(event) for event in events]
    )


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    """Get event by ID."""
    event = EventRepository.get_active_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    return EventResponse.model_validate(event)


@router.get("/events/{event_id}/ticket-types", response_model=TicketTypeListResponse)
async def get_event_ticket_types(
    event_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """Get ticket types for an event."""
    # Check if event exists
    event = EventRepository.get_active_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    ticket_types = TicketTypeRepository.get_by_event_id(db, event_id, active_only=active_only)
    
    return TicketTypeListResponse(
        ticket_types=[TicketTypeResponse.model_validate(tt) for tt in ticket_types]
    )
