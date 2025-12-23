"""Admin CRUD endpoints for events and ticket types."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

from api.core.db import get_db
from api.repositories.event_repository import EventRepository
from api.repositories.ticket_type_repository import TicketTypeRepository
from api.api.v1.schemas import EventResponse, TicketTypeResponse
from api.models import Event, TicketType

router = APIRouter()


# Event schemas
class EventCreate(BaseModel):
    """Schema for creating an event."""
    name: str
    description: Optional[str] = None
    date: str
    time: str
    djs: Optional[List[str]] = None
    is_active: bool = True


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    djs: Optional[List[str]] = None
    is_active: Optional[bool] = None


# TicketType schemas
class TicketTypeCreate(BaseModel):
    """Schema for creating a ticket type."""
    event_id: int
    name: str
    price: Decimal
    available_quantity: int
    total_quantity: int
    is_active: bool = True


class TicketTypeUpdate(BaseModel):
    """Schema for updating a ticket type."""
    name: Optional[str] = None
    price: Optional[Decimal] = None
    available_quantity: Optional[int] = None
    total_quantity: Optional[int] = None
    is_active: Optional[bool] = None


# Events CRUD
@router.post("/admin/events", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    """Create a new event."""
    event = Event(
        name=event_data.name,
        description=event_data.description,
        date=event_data.date,
        time=event_data.time,
        djs=event_data.djs,
        is_active=event_data.is_active,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)


@router.put("/admin/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
):
    """Update an event."""
    event = EventRepository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    if event_data.name is not None:
        event.name = event_data.name
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.date is not None:
        event.date = event_data.date
    if event_data.time is not None:
        event.time = event_data.time
    if event_data.djs is not None:
        event.djs = event_data.djs
    if event_data.is_active is not None:
        event.is_active = event_data.is_active
    
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)


@router.delete("/admin/events/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    """Delete an event (soft delete by setting is_active=False)."""
    event = EventRepository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    event.is_active = False
    db.commit()
    return {"message": f"Event {event_id} deactivated successfully"}


# TicketTypes CRUD
@router.post("/admin/ticket-types", response_model=TicketTypeResponse)
async def create_ticket_type(
    ticket_type_data: TicketTypeCreate,
    db: Session = Depends(get_db),
):
    """Create a new ticket type."""
    # Check if event exists
    event = EventRepository.get_by_id(db, ticket_type_data.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {ticket_type_data.event_id} not found"
        )
    
    ticket_type = TicketType(
        event_id=ticket_type_data.event_id,
        name=ticket_type_data.name,
        price=ticket_type_data.price,
        available_quantity=ticket_type_data.available_quantity,
        total_quantity=ticket_type_data.total_quantity,
        is_active=ticket_type_data.is_active,
    )
    db.add(ticket_type)
    db.commit()
    db.refresh(ticket_type)
    return TicketTypeResponse.model_validate(ticket_type)


@router.put("/admin/ticket-types/{ticket_type_id}", response_model=TicketTypeResponse)
async def update_ticket_type(
    ticket_type_id: int,
    ticket_type_data: TicketTypeUpdate,
    db: Session = Depends(get_db),
):
    """Update a ticket type."""
    ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket type with id {ticket_type_id} not found"
        )
    
    if ticket_type_data.name is not None:
        ticket_type.name = ticket_type_data.name
    if ticket_type_data.price is not None:
        ticket_type.price = ticket_type_data.price
    if ticket_type_data.available_quantity is not None:
        ticket_type.available_quantity = ticket_type_data.available_quantity
    if ticket_type_data.total_quantity is not None:
        ticket_type.total_quantity = ticket_type_data.total_quantity
    if ticket_type_data.is_active is not None:
        ticket_type.is_active = ticket_type_data.is_active
    
    db.commit()
    db.refresh(ticket_type)
    return TicketTypeResponse.model_validate(ticket_type)


@router.delete("/admin/ticket-types/{ticket_type_id}")
async def delete_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db),
):
    """Delete a ticket type (soft delete by setting is_active=False)."""
    ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket type with id {ticket_type_id} not found"
        )
    
    ticket_type.is_active = False
    db.commit()
    return {"message": f"Ticket type {ticket_type_id} deactivated successfully"}

