"""Admin CRUD endpoints for all models."""
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, UploadFile, File, Form, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

from api.core.db import get_db
from api.core.auth import get_current_admin
from api.repositories.event_repository import EventRepository
from api.repositories.ticket_type_repository import TicketTypeRepository
from api.repositories.ticket_type_template_repository import TicketTypeTemplateRepository
from api.repositories.user_repository import UserRepository
from api.repositories.ticket_repository import TicketRepository
from api.repositories.payment_repository import PaymentRepository
from api.repositories.order_repository import OrderRepository
from api.repositories.expiration_settings_repository import ExpirationSettingsRepository
from api.repositories.club_settings_repository import ClubSettingsRepository
from api.repositories.support_message_repository import SupportMessageRepository
from api.repositories.support_message_photo_repository import SupportMessagePhotoRepository
from api.repositories.admin_message_repository import AdminMessageRepository
from api.repositories.admin_message_photo_repository import AdminMessagePhotoRepository
from api.repositories.staff_user_repository import StaffUserRepository
from api.repositories.menu_photo_repository import MenuPhotoRepository
from api.repositories.music_request_repository import MusicRequestRepository
from api.repositories.music_queue_repository import MusicQueueRepository
from api.services.telegram_service import download_file_from_telegram
from api.services.file_storage_service import save_support_photo, get_full_file_path
from api.core.config import settings
from api.services.ticket_service import TicketService
from api.services.event_scheduling_service import schedule_event_deactivation, cancel_event_deactivation
from api.api.v1.schemas import (
    EventResponse, EventListResponse,
    TicketTypeResponse, TicketTypeListResponse,
    TicketTypeTemplateResponse, TicketTypeTemplateCreate, TicketTypeTemplateListResponse,
    UserResponse, UserCreate, UserUpdate,
    TicketResponse, TicketDetailResponse, TicketCreate, TicketUpdate, TicketMarkUsedResponse,
    PaymentResponse,
    ExpirationSettingsResponse,
    ExpirationSettingsUpdate,
    ClubSettingsResponse,
    ClubSettingsUpdate,
    SupportMessageResponse,
    SupportMessagePhotoResponse,
    SupportMessageCreate,
    SupportMessageUpdate,
    SupportMessageListResponse,
    AdminMessageResponse,
    AdminMessagePhotoResponse,
    StaffUserResponse,
    StaffUserCreate,
    StaffUserUpdate,
    StaffUserListResponse,
    MenuPhotoResponse,
    MenuPhotoListResponse,
    MenuPhotoReorderRequest,
    MusicRequestResponse,
    MusicRequestListResponse,
    MusicQueueResponse,
    MusicQueueListResponse,
    MusicQueueCreate,
    MusicQueueReorderRequest,
)
from api.models import Event, TicketType, TicketTypeTemplate, Ticket, Payment, Order, SupportMessage, MenuPhoto
from api.models.ticket import TicketStatus
from api.models.payment import PaymentStatus

router = APIRouter()


# Event schemas
class EventCreate(BaseModel):
    """Schema for creating an event."""
    name: str
    description: Optional[str] = None
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    djs: Optional[List[str]] = None
    is_active: bool = True


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    start_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None
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


# User schemas
class UserListResponse(BaseModel):
    """Schema for list of users."""
    users: List[UserResponse]


# Ticket schemas


class TicketListResponse(BaseModel):
    """Schema for list of tickets."""
    tickets: List[TicketResponse]


# Payment schemas
class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""
    status: Optional[PaymentStatus] = None


class PaymentListResponse(BaseModel):
    """Schema for list of payments."""
    payments: List[PaymentResponse]


# Order schemas
class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    order_id: str
    user_id: int
    event_id: int
    ticket_type_id: int
    quantity: int
    payment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderAdminResponse(BaseModel):
    """Schema for order in admin panel."""
    id: int
    order_id: str
    user_id: int
    event_id: int
    ticket_type_id: int
    quantity: int
    payment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    username: Optional[str] = None  # Telegram username
    first_name: Optional[str] = None  # User first name
    last_name: Optional[str] = None  # User last name
    event_name: Optional[str] = None  # Event name
    ticket_type_name: Optional[str] = None  # Ticket type name
    amount: Optional[Decimal] = None  # Payment amount
    payment_status: Optional[str] = None  # Payment status

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for list of orders."""
    orders: List[OrderAdminResponse]



# Events CRUD
@router.get("/admin/events", response_model=EventListResponse)
async def get_all_events(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all events (admin only)."""
    events = EventRepository.get_all(db)
    return EventListResponse(events=[EventResponse.model_validate(event) for event in events])


@router.get("/admin/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get event by ID (admin only)."""
    event = EventRepository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return EventResponse.model_validate(event)


@router.post("/admin/events", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new event."""
    from datetime import datetime
    import pytz
    from api.repositories.club_settings_repository import ClubSettingsRepository
    
    # Get timezone from club settings
    club_settings = ClubSettingsRepository.get_settings(db)
    timezone_str = getattr(club_settings, 'timezone', 'Europe/Moscow')
    if not timezone_str:
        timezone_str = 'Europe/Moscow'
    
    # Validate datetime
    try:
        start_dt = datetime.strptime(f"{event_data.start_date} {event_data.start_time}", "%d.%m.%Y %H:%M")
        end_dt = datetime.strptime(f"{event_data.end_date} {event_data.end_time}", "%d.%m.%Y %H:%M")
        if end_dt <= start_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date and time must be later than start date and time"
            )
        
        # Check if trying to create active event with past end date/time
        # Only validate if auto_deactivate_events is enabled
        club_settings = ClubSettingsRepository.get_settings(db)
        if event_data.is_active and event_data.end_date and event_data.end_time and club_settings.auto_deactivate_events:
            try:
                tz = pytz.timezone(timezone_str)
                end_dt_tz = tz.localize(end_dt)
                current_time = datetime.now(tz)
                
                logger.info(f"Validating event creation: end_dt_tz={end_dt_tz}, current_time={current_time}, timezone={timezone_str}")
                
                if end_dt_tz <= current_time:
                    logger.warning(f"Rejecting creation: end time {end_dt_tz} is in the past (current: {current_time})")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot create active event with end date and time in the past"
                    )
            except HTTPException:
                # Re-raise HTTPException
                raise
            except Exception as tz_error:
                # If timezone parsing fails, try to use UTC as fallback
                logger.warning(f"Timezone parsing failed: {tz_error}, using UTC for comparison")
                try:
                    tz_utc = pytz.UTC
                    end_dt_utc = tz_utc.localize(end_dt)
                    current_time_utc = datetime.now(tz_utc)
                    
                    if end_dt_utc <= current_time_utc:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot create active event with end date and time in the past"
                        )
                except HTTPException:
                    raise
                except Exception:
                    # Last resort: use naive datetime (should not happen)
                    logger.error(f"All timezone parsing methods failed, using naive datetime")
                    if end_dt <= datetime.now():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot create active event with end date and time in the past"
                        )
    except ValueError as e:
        if "must be later" not in str(e) and "Cannot create" not in str(e):
            # Date format errors will be caught by Pydantic
            pass
    
    event = Event(
        name=event_data.name,
        description=event_data.description,
        start_date=event_data.start_date,
        start_time=event_data.start_time,
        end_date=event_data.end_date,
        end_time=event_data.end_time,
        djs=event_data.djs,
        is_active=event_data.is_active,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    logger.info(f"✅ Created event: ID={event.id}, Name='{event.name}', is_active={event.is_active}")
    
    # Schedule event deactivation if end_date and end_time are provided
    if event_data.end_date and event_data.end_time and event.is_active:
        logger.info(f"📅 Event is active with end date/time, scheduling deactivation...")
        await schedule_event_deactivation(db, event.id, event_data.end_date, event_data.end_time)
    
    return EventResponse.model_validate(event)


@router.put("/admin/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
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
    if event_data.start_date is not None:
        event.start_date = event_data.start_date
    if event_data.start_time is not None:
        event.start_time = event_data.start_time
    if event_data.end_date is not None:
        event.end_date = event_data.end_date
    if event_data.end_time is not None:
        event.end_time = event_data.end_time
    if event_data.djs is not None:
        event.djs = event_data.djs
    if event_data.is_active is not None:
        event.is_active = event_data.is_active
    
    # Validate datetime if any date/time fields are being updated
    if (event_data.start_date is not None or event_data.start_time is not None or 
        event_data.end_date is not None or event_data.end_time is not None):
        from datetime import datetime
        import pytz
        from api.repositories.club_settings_repository import ClubSettingsRepository
        
        start_date = event_data.start_date if event_data.start_date is not None else event.start_date
        start_time = event_data.start_time if event_data.start_time is not None else event.start_time
        end_date = event_data.end_date if event_data.end_date is not None else event.end_date
        end_time = event_data.end_time if event_data.end_time is not None else event.end_time
        
        try:
            start_dt = datetime.strptime(f"{start_date} {start_time}", "%d.%m.%Y %H:%M")
            end_dt = datetime.strptime(f"{end_date} {end_time}", "%d.%m.%Y %H:%M")
            if end_dt <= start_dt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date and time must be later than start date and time"
                )
        except ValueError:
            # Date format errors will be caught by Pydantic
            pass
    
    # Check if trying to activate event with past end date/time
    # Only validate if auto_deactivate_events is enabled
    will_be_active = event_data.is_active if event_data.is_active is not None else event.is_active
    if will_be_active:
        end_date_to_check = event_data.end_date if event_data.end_date is not None else event.end_date
        end_time_to_check = event_data.end_time if event_data.end_time is not None else event.end_time
        
        if end_date_to_check and end_time_to_check:
            from datetime import datetime
            import pytz
            from api.repositories.club_settings_repository import ClubSettingsRepository
            
            # Get timezone from club settings
            club_settings = ClubSettingsRepository.get_settings(db)
            timezone_str = getattr(club_settings, 'timezone', 'Europe/Moscow')
            if not timezone_str:
                timezone_str = 'Europe/Moscow'
            
            logger.info(f"Checking auto_deactivate_events: {club_settings.auto_deactivate_events} (type: {type(club_settings.auto_deactivate_events)})")
            
            # Only validate if auto_deactivate_events is enabled
            if club_settings.auto_deactivate_events:
                try:
                    end_dt = datetime.strptime(f"{end_date_to_check} {end_time_to_check}", "%d.%m.%Y %H:%M")
                    
                    try:
                        tz = pytz.timezone(timezone_str)
                        end_dt_tz = tz.localize(end_dt)
                        current_time = datetime.now(tz)
                        
                        logger.info(f"Validating event activation: end_dt_tz={end_dt_tz}, current_time={current_time}, timezone={timezone_str}")
                        
                        if end_dt_tz <= current_time:
                            logger.warning(f"Rejecting activation: end time {end_dt_tz} is in the past (current: {current_time})")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Cannot activate event with end date and time in the past"
                            )
                    except HTTPException:
                        # Re-raise HTTPException
                        raise
                    except Exception as tz_error:
                        # If timezone parsing fails, try to use UTC as fallback
                        logger.warning(f"Timezone parsing failed: {tz_error}, using UTC for comparison")
                        try:
                            tz_utc = pytz.UTC
                            end_dt_utc = tz_utc.localize(end_dt)
                            current_time_utc = datetime.now(tz_utc)
                            
                            if end_dt_utc <= current_time_utc:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Cannot activate event with end date and time in the past"
                                )
                        except HTTPException:
                            raise
                        except Exception:
                            # Last resort: use naive datetime (should not happen)
                            logger.error(f"All timezone parsing methods failed, using naive datetime")
                            if end_dt <= datetime.now():
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Cannot activate event with end date and time in the past"
                                )
                except ValueError:
                    # Date format errors will be caught by Pydantic
                    pass
            else:
                logger.info(f"Skipping validation: auto_deactivate_events is disabled")
    
    # Handle end_date and end_time changes
    end_date_changed = event_data.end_date is not None
    end_time_changed = event_data.end_time is not None
    
    db.commit()
    db.refresh(event)
    
    # Schedule or cancel deactivation based on changes
    if (end_date_changed or end_time_changed) and event.is_active:
        if event.end_date and event.end_time:
            # Cancel existing and schedule new
            await cancel_event_deactivation(event.id)
            await schedule_event_deactivation(db, event.id, event.end_date, event.end_time)
        else:
            # Cancel if end_date or end_time removed
            await cancel_event_deactivation(event.id)
    elif event_data.is_active is not None:
        if event.is_active and event.end_date and event.end_time:
            # Event reactivated, schedule deactivation
            await schedule_event_deactivation(db, event.id, event.end_date, event.end_time)
        elif not event.is_active:
            # Event deactivated, cancel scheduled deactivation
            await cancel_event_deactivation(event.id)
    
    return EventResponse.model_validate(event)


@router.delete("/admin/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete an event (soft delete by default, hard delete if hard=true)."""
    if hard:
        from api.models.order import Order
        from api.models.ticket import Ticket
        
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )
        
        # Explicitly delete related orders first to avoid constraint violations
        # Orders have CASCADE, but SQLAlchemy may try to set event_id to NULL which violates NOT NULL
        orders = db.query(Order).filter(Order.event_id == event_id).all()
        for order in orders:
            db.delete(order)
        
        # Explicitly delete related tickets first to avoid constraint violations
        # Tickets have CASCADE, but SQLAlchemy may try to set event_id to NULL which violates NOT NULL
        tickets = db.query(Ticket).filter(Ticket.event_id == event_id).all()
        for ticket in tickets:
            db.delete(ticket)
        
        db.delete(event)
        db.commit()
    else:
        success = EventRepository.delete(db, event_id, hard=False)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )
    return None


# TicketTypes CRUD
@router.get("/admin/ticket-types", response_model=TicketTypeListResponse)
async def get_all_ticket_types(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all ticket types (admin only)."""
    ticket_types = TicketTypeRepository.get_all(db)
    return TicketTypeListResponse(ticket_types=[TicketTypeResponse.model_validate(tt) for tt in ticket_types])


@router.get("/admin/ticket-types/{ticket_type_id}", response_model=TicketTypeResponse)
async def get_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get ticket type by ID (admin only)."""
    ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket type with id {ticket_type_id} not found"
        )
    return TicketTypeResponse.model_validate(ticket_type)


@router.post("/admin/ticket-types", response_model=TicketTypeResponse)
async def create_ticket_type(
    ticket_type_data: TicketTypeCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
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
    current_admin: dict = Depends(get_current_admin),
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


@router.delete("/admin/ticket-types/{ticket_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket_type(
    ticket_type_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a ticket type (soft delete by default, hard delete if hard=true)."""
    if hard:
        from api.models.order import Order
        from api.models.ticket import Ticket
        
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket type with id {ticket_type_id} not found"
            )
        
        # Explicitly delete related orders first to avoid constraint violations
        # Orders have RESTRICT, but SQLAlchemy may try to set ticket_type_id to NULL which violates NOT NULL
        orders = db.query(Order).filter(Order.ticket_type_id == ticket_type_id).all()
        for order in orders:
            db.delete(order)
        
        # Explicitly delete related tickets first to avoid constraint violations
        # Tickets have CASCADE, but SQLAlchemy may try to set ticket_type_id to NULL which violates NOT NULL
        tickets = db.query(Ticket).filter(Ticket.ticket_type_id == ticket_type_id).all()
        for ticket in tickets:
            db.delete(ticket)
        
        db.delete(ticket_type)
        db.commit()
    else:
        success = TicketTypeRepository.delete(db, ticket_type_id, hard=False)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket type with id {ticket_type_id} not found"
            )
    return None


# TicketTypeTemplate CRUD
@router.get("/admin/ticket-type-templates", response_model=TicketTypeTemplateListResponse)
async def get_all_ticket_type_templates(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all ticket type templates."""
    templates = TicketTypeTemplateRepository.get_all(db)
    return TicketTypeTemplateListResponse(templates=[TicketTypeTemplateResponse.model_validate(t) for t in templates])


@router.post("/admin/ticket-type-templates", response_model=TicketTypeTemplateResponse)
async def create_ticket_type_template(
    template_data: TicketTypeTemplateCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new ticket type template."""
    template = TicketTypeTemplateRepository.create(
        db=db,
        name=template_data.name,
        price=template_data.price,
        available_quantity=template_data.available_quantity,
        total_quantity=template_data.total_quantity,
    )
    return TicketTypeTemplateResponse.model_validate(template)


@router.delete("/admin/ticket-type-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket_type_template(
    template_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a ticket type template (soft delete by default, hard delete if hard=true)."""
    if not TicketTypeTemplateRepository.delete(db, template_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found"
        )
    return None


# Users CRUD
@router.get("/admin/users", response_model=UserListResponse)
async def get_all_users(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all users (admin only)."""
    users = UserRepository.get_all(db)
    return UserListResponse(users=[UserResponse.model_validate(user) for user in users])


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get user by ID (admin only)."""
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return UserResponse.model_validate(user)


@router.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new user (admin only)."""
    # Check if user with this telegram_user_id already exists
    existing_user = UserRepository.get_by_telegram_id(db, user_data.telegram_user_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_user_id {user_data.telegram_user_id} already exists"
        )
    
    user = UserRepository.create(db, user_data)
    return UserResponse.model_validate(user)


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update a user."""
    user = UserRepository.update(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return UserResponse.model_validate(user)


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a user (soft delete by default, hard delete if hard=true)."""
    success = UserRepository.delete(db, user_id, hard=hard)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return {"message": f"User {user_id} deleted successfully"}


# Tickets CRUD
@router.get("/admin/tickets", response_model=TicketListResponse)
async def get_all_tickets(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all tickets (admin only)."""
    from api.repositories.user_repository import UserRepository
    
    tickets = TicketRepository.get_all(db)
    ticket_responses = []
    for ticket in tickets:
        ticket_data = TicketResponse.model_validate(ticket)
        # Get user info from user
        user = UserRepository.get_by_id(db, ticket.user_id)
        if user:
            ticket_data.username = user.username
            ticket_data.first_name = user.first_name
            ticket_data.last_name = user.last_name
        # Event and ticket_type should be loaded via joinedload, but ensure they're set
        if ticket.event:
            ticket_data.event = EventResponse.model_validate(ticket.event)
        if ticket.ticket_type:
            ticket_data.ticket_type = TicketTypeResponse.model_validate(ticket.ticket_type)
        ticket_responses.append(ticket_data)
    
    return TicketListResponse(tickets=ticket_responses)


@router.post("/admin/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new ticket."""
    # Validate user exists
    user = UserRepository.get_by_id(db, ticket_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {ticket_data.user_id} not found"
        )
    
    # Validate event exists
    event = EventRepository.get_by_id(db, ticket_data.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {ticket_data.event_id} not found"
        )
    
    # Validate ticket type exists and belongs to the event
    ticket_type = TicketTypeRepository.get_by_id(db, ticket_data.ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket type with id {ticket_data.ticket_type_id} not found"
        )
    if ticket_type.event_id != ticket_data.event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket type {ticket_data.ticket_type_id} does not belong to event {ticket_data.event_id}"
        )
    
    # Create ticket
    try:
        ticket = TicketRepository.create(
            db,
            user_id=ticket_data.user_id,
            event_id=ticket_data.event_id,
            ticket_type_id=ticket_data.ticket_type_id,
            token=ticket_data.token,
            status=ticket_data.status,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Load related data for response
    ticket = TicketRepository.get_by_id(db, ticket.id)
    ticket_response = TicketResponse.model_validate(ticket)
    if ticket.user:
        ticket_response.username = ticket.user.username
        ticket_response.first_name = ticket.user.first_name
        ticket_response.last_name = ticket.user.last_name
    if ticket.event:
        ticket_response.event = EventResponse.model_validate(ticket.event)
    if ticket.ticket_type:
        ticket_response.ticket_type = TicketTypeResponse.model_validate(ticket.ticket_type)
    
    return ticket_response


@router.get("/admin/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get ticket by ID (admin only)."""
    ticket = TicketRepository.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    return TicketDetailResponse.model_validate(ticket)


@router.put("/admin/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update a ticket."""
    
    ticket = TicketRepository.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    # Log what Pydantic received
    logger.info(f"=== Pydantic TicketUpdate model ===")
    logger.info(f"ticket_data object: {ticket_data}")
    logger.info(f"ticket_data dict (exclude_unset=False): {ticket_data.model_dump(exclude_unset=False)}")
    logger.info(f"ticket_data dict (exclude_unset=True): {ticket_data.model_dump(exclude_unset=True)}")
    
    # Get all fields that were provided (not None)
    # Use model_dump(exclude_unset=True) to get only fields that were explicitly set
    update_dict = ticket_data.model_dump(exclude_unset=True)
    logger.info(f"Fields to update: {update_dict}")
    logger.info(f"Current ticket state: user_id={ticket.user_id}, event_id={ticket.event_id}, ticket_type_id={ticket.ticket_type_id}, token={ticket.token}, status={ticket.status}")
    
    # Update user_id if provided
    if 'user_id' in update_dict and update_dict['user_id'] is not None:
        user = UserRepository.get_by_id(db, update_dict['user_id'])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {update_dict['user_id']} not found"
            )
        old_user_id = ticket.user_id
        ticket.user_id = update_dict['user_id']
        logger.info(f"Updated user_id from {old_user_id} to {ticket.user_id}")
    
    # Update event_id if provided
    if 'event_id' in update_dict and update_dict['event_id'] is not None:
        event = EventRepository.get_by_id(db, update_dict['event_id'])
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {update_dict['event_id']} not found"
            )
        old_event_id = ticket.event_id
        ticket.event_id = update_dict['event_id']
        logger.info(f"Updated event_id from {old_event_id} to {ticket.event_id}")
    
    # Update ticket_type_id if provided
    if 'ticket_type_id' in update_dict and update_dict['ticket_type_id'] is not None:
        ticket_type = TicketTypeRepository.get_by_id(db, update_dict['ticket_type_id'])
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket type with id {update_dict['ticket_type_id']} not found"
            )
        # Validate that ticket_type belongs to event if event_id is also being updated
        if 'event_id' in update_dict and update_dict['event_id'] is not None:
            if ticket_type.event_id != update_dict['event_id']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ticket type {update_dict['ticket_type_id']} does not belong to event {update_dict['event_id']}"
                )
        # Validate that ticket_type belongs to current event if event_id is not being updated
        elif ticket_type.event_id != ticket.event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ticket type {update_dict['ticket_type_id']} does not belong to event {ticket.event_id}"
            )
        old_ticket_type_id = ticket.ticket_type_id
        ticket.ticket_type_id = update_dict['ticket_type_id']
        logger.info(f"Updated ticket_type_id from {old_ticket_type_id} to {ticket.ticket_type_id}")
    
    # Update token if provided
    if 'token' in update_dict and update_dict['token'] is not None:
        # Check if token is unique (excluding current ticket)
        existing_ticket = TicketRepository.get_by_token(db, update_dict['token'])
        if existing_ticket and existing_ticket.id != ticket_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token {update_dict['token']} already exists"
            )
        old_token = ticket.token
        ticket.token = update_dict['token']
        logger.info(f"Updated token from {old_token} to {ticket.token}")
    
    # Update status if provided
    if 'status' in update_dict and update_dict['status'] is not None:
        # Explicitly convert to enum using the value to ensure SQLAlchemy uses the correct string
        status_value = update_dict['status']
        if isinstance(status_value, TicketStatus):
            status_value = status_value.value
        old_status = ticket.status
        new_status = TicketStatus(status_value)
        
        # Update total_quantity based on status change
        if old_status == TicketStatus.ACTIVE and new_status == TicketStatus.CANCELLED:
            # Ticket cancelled: increase total_quantity
            TicketTypeRepository.increase_total_quantity(db, ticket.ticket_type_id, 1)
        elif old_status == TicketStatus.CANCELLED and new_status == TicketStatus.ACTIVE:
            # Ticket restored from cancelled: decrease total_quantity
            TicketTypeRepository.decrease_total_quantity(db, ticket.ticket_type_id, 1)
        
        ticket.status = new_status
        logger.info(f"Updated status from {old_status} to {ticket.status}")
        # Set used_at when status changes to USED
        if ticket.status == TicketStatus.USED and not ticket.used_at:
            from api.utils.timezone import get_current_time_in_timezone
            ticket.used_at = get_current_time_in_timezone(db)
    
    logger.info(f"Ticket state before commit: user_id={ticket.user_id}, event_id={ticket.event_id}, ticket_type_id={ticket.ticket_type_id}, token={ticket.token}, status={ticket.status}")
    db.commit()
    db.refresh(ticket)
    logger.info(f"Ticket state after commit and refresh: user_id={ticket.user_id}, event_id={ticket.event_id}, ticket_type_id={ticket.ticket_type_id}, token={ticket.token}, status={ticket.status}")
    
    # Load related data for response
    ticket = TicketRepository.get_by_id(db, ticket.id)
    ticket_response = TicketResponse.model_validate(ticket)
    if ticket.user:
        ticket_response.username = ticket.user.username
        ticket_response.first_name = ticket.user.first_name
        ticket_response.last_name = ticket.user.last_name
    if ticket.event:
        ticket_response.event = EventResponse.model_validate(ticket.event)
    if ticket.ticket_type:
        ticket_response.ticket_type = TicketTypeResponse.model_validate(ticket.ticket_type)
    
    return ticket_response


@router.get("/admin/tickets/token/{token}", response_model=TicketDetailResponse)
async def get_ticket_by_token(
    token: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get ticket by token (admin only)."""
    ticket = TicketService.get_ticket_by_token(db, token)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with token {token} not found"
        )
    return ticket


@router.post("/admin/tickets/{ticket_id}/mark-used", response_model=TicketMarkUsedResponse)
async def mark_ticket_as_used_admin(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Mark ticket as used (admin only)."""
    ticket = TicketService.mark_ticket_as_used(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    return TicketMarkUsedResponse(
        ticket_id=ticket.id,
        status=ticket.status,
        used_at=ticket.used_at or datetime.utcnow(),
        message="Ticket marked as used successfully"
    )


@router.delete("/admin/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a ticket (soft delete by default, hard delete if hard=true)."""
    if hard:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found"
            )
        
        # If ticket was active, increase total_quantity
        if ticket.status == TicketStatus.ACTIVE:
            TicketTypeRepository.increase_total_quantity(db, ticket.ticket_type_id, 1)
        
        db.delete(ticket)
        db.commit()
    else:
        ticket = TicketRepository.get_by_id(db, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found"
            )
        
        # If ticket was active, increase total_quantity
        if ticket.status == TicketStatus.ACTIVE:
            TicketTypeRepository.increase_total_quantity(db, ticket.ticket_type_id, 1)
        
        success = TicketRepository.delete(db, ticket_id, hard=False)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found"
            )
    return {"message": f"Ticket {ticket_id} deleted successfully"}


# Payments CRUD
@router.get("/admin/payments", response_model=PaymentListResponse)
async def get_all_payments(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all payments (admin only)."""
    payments = PaymentRepository.get_all(db)
    return PaymentListResponse(payments=[PaymentResponse.model_validate(payment) for payment in payments])


@router.get("/admin/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get payment by ID (admin only)."""
    payment = PaymentRepository.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found"
        )
    return PaymentResponse.model_validate(payment)


@router.put("/admin/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update a payment."""
    if payment_data.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )
    
    payment = PaymentRepository.update_status(db, payment_id, payment_data.status)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found"
        )
    return PaymentResponse.model_validate(payment)


# Orders CRUD
@router.get("/admin/orders", response_model=OrderListResponse)
async def get_all_orders(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all orders (admin only)."""
    from api.repositories.user_repository import UserRepository
    from api.repositories.event_repository import EventRepository
    from api.repositories.ticket_type_repository import TicketTypeRepository
    
    orders = OrderRepository.get_all(db)
    order_responses = []
    for order in orders:
        order_data = OrderAdminResponse.model_validate(order)
        # Get user info from user
        user = UserRepository.get_by_id(db, order.user_id)
        if user:
            order_data.username = user.username
            order_data.first_name = user.first_name
            order_data.last_name = user.last_name
        # Get event name
        event = EventRepository.get_by_id(db, order.event_id)
        if event:
            order_data.event_name = event.name
        # Get ticket type name
        ticket_type = TicketTypeRepository.get_by_id(db, order.ticket_type_id)
        if ticket_type:
            order_data.ticket_type_name = ticket_type.name
        # Get payment info
        if order.payment_id and order.payment:
            order_data.amount = order.payment.amount
            order_data.payment_status = order.payment.status.value
        order_responses.append(order_data)
    
    return OrderListResponse(orders=order_responses)


@router.get("/admin/orders/{order_id}", response_model=OrderAdminResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get order by ID (admin only)."""
    from api.repositories.user_repository import UserRepository
    
    order = OrderRepository.get_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    from api.repositories.event_repository import EventRepository
    from api.repositories.ticket_type_repository import TicketTypeRepository
    
    order_data = OrderAdminResponse.model_validate(order)
    # Get user info from user
    user = UserRepository.get_by_id(db, order.user_id)
    if user:
        order_data.username = user.username
        order_data.first_name = user.first_name
        order_data.last_name = user.last_name
    # Get event name
    event = EventRepository.get_by_id(db, order.event_id)
    if event:
        order_data.event_name = event.name
    # Get ticket type name
    ticket_type = TicketTypeRepository.get_by_id(db, order.ticket_type_id)
    if ticket_type:
        order_data.ticket_type_name = ticket_type.name
    return order_data


@router.delete("/admin/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete an order (soft delete by default, hard delete if hard=true)."""
    success = OrderRepository.delete(db, order_id, hard=hard)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )


# Expiration Settings
@router.get("/admin/expiration-settings", response_model=ExpirationSettingsResponse)
async def get_expiration_settings(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get expiration service settings."""
    from api.repositories.expiration_settings_repository import ExpirationSettingsRepository
    settings = ExpirationSettingsRepository.get_settings(db)
    return ExpirationSettingsResponse.model_validate(settings)


@router.put("/admin/expiration-settings", response_model=ExpirationSettingsResponse)
async def update_expiration_settings(
    settings_update: ExpirationSettingsUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update expiration service settings."""
    from api.repositories.expiration_settings_repository import ExpirationSettingsRepository
    from api.core.config import settings as api_settings
    import httpx
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        settings = ExpirationSettingsRepository.update_settings(
            db,
            ticket_expiration_enabled=settings_update.ticket_expiration_enabled,
            event_deactivation_enabled=settings_update.event_deactivation_enabled,
            check_interval_minutes=settings_update.check_interval_minutes
        )
        
        # If check_interval_minutes was updated, notify expiration-service
        if settings_update.check_interval_minutes is not None:
            expiration_service_url = api_settings.EXPIRATION_SERVICE_URL
            logger.info(f"Using expiration service URL: {expiration_service_url}")
            logger.info(f"Updating interval to {settings.check_interval_minutes} minutes")
            
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    url = f"{expiration_service_url}/update-interval"
                    logger.info(f"Sending POST request to {url}")
                    response = await client.post(
                        url,
                        json={"check_interval_minutes": settings.check_interval_minutes}
                    )
                    logger.info(f"Response status: {response.status_code}, body: {response.text}")
                    if response.status_code == 200:
                        logger.info(f"Successfully updated expiration service interval to {settings.check_interval_minutes} minutes")
                    else:
                        logger.warning(f"Failed to update expiration service interval: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Error notifying expiration service: {e}", exc_info=True)
                # Don't fail the request if expiration service is unreachable
        
        return ExpirationSettingsResponse.model_validate(settings)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Club Settings endpoints
@router.get("/admin/club-settings")
async def get_club_settings(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get club settings."""
    settings = ClubSettingsRepository.get_settings(db)
    # Handle case where auto_deactivate_events might not exist in DB
    try:
        auto_deactivate = getattr(settings, 'auto_deactivate_events', None)
        if auto_deactivate is None:
            auto_deactivate = True
    except AttributeError:
        auto_deactivate = True
    
    # Ensure updated_at is a datetime object
    updated_at = settings.updated_at
    if updated_at is None:
        updated_at = datetime.utcnow()
    
    # Handle case where timezone might not exist in DB
    try:
        timezone = getattr(settings, 'timezone', None)
        if timezone is None:
            timezone = "Europe/Moscow"
    except AttributeError:
        timezone = "Europe/Moscow"
    
    # Handle case where additional_info might not exist in DB
    try:
        additional_info = getattr(settings, 'additional_info', None)
    except AttributeError:
        additional_info = None
    
    response_data = {
        "id": int(settings.id),
        "address": settings.address if settings.address else None,
        "phone": settings.phone if settings.phone else None,
        "email": settings.email if settings.email else None,
        "additional_info": additional_info if additional_info else None,
        "auto_deactivate_events": bool(auto_deactivate),
        "timezone": timezone if timezone else "Europe/Moscow",
        "updated_at": updated_at
    }
    
    return response_data


@router.put("/admin/club-settings")
async def update_club_settings(
    settings_update: ClubSettingsUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update club settings."""
    try:
        # Get current settings to check if auto_deactivate_events is being enabled
        current_settings = ClubSettingsRepository.get_settings(db)
        was_auto_deactivate_disabled = not current_settings.auto_deactivate_events
        will_be_auto_deactivate_enabled = settings_update.auto_deactivate_events if settings_update.auto_deactivate_events is not None else current_settings.auto_deactivate_events
        
        settings = ClubSettingsRepository.update_settings(
            db,
            address=settings_update.address,
            phone=settings_update.phone,
            email=settings_update.email,
            additional_info=settings_update.additional_info,
            auto_deactivate_events=settings_update.auto_deactivate_events,
            timezone=settings_update.timezone
        )
        
        # If auto_deactivate_events was just enabled, check all active events
        if was_auto_deactivate_disabled and will_be_auto_deactivate_enabled:
            logger.info("Auto deactivate events was just enabled, checking all active events for expiration...")
            from api.models.event import Event
            from api.models.ticket import Ticket, TicketStatus
            import pytz
            
            # Get timezone
            timezone_str = settings.timezone or "Europe/Moscow"
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz)
            
            # Get all active events
            active_events = db.query(Event).filter(
                Event.is_active == True,
                Event.is_deleted == False
            ).all()
            
            deactivated_count = 0
            expired_tickets_count = 0
            
            for event in active_events:
                if event.end_date and event.end_time:
                    try:
                        end_dt = datetime.strptime(f"{event.end_date} {event.end_time}", "%d.%m.%Y %H:%M")
                        end_dt_tz = tz.localize(end_dt)
                        
                        if end_dt_tz <= current_time:
                            logger.info(f"Deactivating expired event {event.id} ({event.name})")
                            event.is_active = False
                            deactivated_count += 1
                            
                            # Mark all active tickets for this event as expired
                            tickets = db.query(Ticket).filter(
                                Ticket.event_id == event.id,
                                Ticket.status == TicketStatus.ACTIVE
                            ).all()
                            
                            for ticket in tickets:
                                ticket.status = TicketStatus.EXPIRED
                                expired_tickets_count += 1
                                logger.debug(f"   Expired ticket {ticket.id} (token: {ticket.token})")
                    except Exception as e:
                        logger.error(f"Error processing event {event.id}: {e}", exc_info=True)
                        continue
            
            if deactivated_count > 0 or expired_tickets_count > 0:
                db.commit()
                logger.info(f"✅ Checked all active events: deactivated {deactivated_count} event(s), expired {expired_tickets_count} ticket(s)")
            else:
                logger.info("✅ Checked all active events: no expired events found")
        
        # Ensure updated_at is a datetime object
        updated_at = settings.updated_at
        if updated_at is None:
            updated_at = datetime.utcnow()
        
        # Handle case where additional_info might not exist in DB
        try:
            additional_info = getattr(settings, 'additional_info', None)
        except AttributeError:
            additional_info = None
        
        response_data = {
            "id": int(settings.id),
            "address": settings.address if settings.address else None,
            "phone": settings.phone if settings.phone else None,
            "email": settings.email if settings.email else None,
            "additional_info": additional_info if additional_info else None,
            "auto_deactivate_events": bool(settings.auto_deactivate_events),
            "timezone": settings.timezone if settings.timezone else "Europe/Moscow",
            "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
        }
        
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update club settings: {str(e)}"
        )


# Support Messages CRUD
@router.get("/admin/support-messages", response_model=SupportMessageListResponse)
async def get_all_support_messages(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all support messages (admin only)."""
    from api.models.support_message import SupportMessageStatus
    
    status_filter = None
    if status:
        try:
            status_filter = SupportMessageStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Must be one of: new, responded, closed"
            )
    
    # Parse date filters
    date_from_dt = None
    date_to_dt = None
    if date_from:
        try:
            date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date_from format. Expected YYYY-MM-DD, got: {date_from}"
            )
    
    if date_to:
        try:
            date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date_to format. Expected YYYY-MM-DD, got: {date_to}"
            )
    
    # Validate date range
    if date_from_dt and date_to_dt and date_from_dt > date_to_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be less than or equal to date_to"
        )
    
    messages = SupportMessageRepository.get_all(
        db,
        status=status_filter,
        user_id=user_id,
        date_from=date_from_dt,
        date_to=date_to_dt,
        search=search,
    )
    
    # Populate user info and photos
    result = []
    for msg in messages:
        msg_dict = SupportMessageResponse.model_validate(msg).model_dump()
        if msg.user:
            msg_dict['username'] = msg.user.username
            msg_dict['first_name'] = msg.user.first_name
            msg_dict['last_name'] = msg.user.last_name
        # Get photos for this message
        photos = SupportMessagePhotoRepository.get_by_support_message_id(db, msg.id)
        msg_dict['photos'] = [SupportMessagePhotoResponse.model_validate(p).model_dump() for p in photos]
        result.append(SupportMessageResponse(**msg_dict))
    
    return SupportMessageListResponse(messages=result)


@router.get("/admin/support-messages/{message_id}", response_model=SupportMessageResponse)
async def get_support_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get a support message by ID (admin only)."""
    message = SupportMessageRepository.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    msg_dict = SupportMessageResponse.model_validate(message).model_dump()
    if message.user:
        msg_dict['username'] = message.user.username
        msg_dict['first_name'] = message.user.first_name
        msg_dict['last_name'] = message.user.last_name
    # Get photos for this message
    photos = SupportMessagePhotoRepository.get_by_support_message_id(db, message_id)
    msg_dict['photos'] = [SupportMessagePhotoResponse.model_validate(p).model_dump() for p in photos]
    return SupportMessageResponse(**msg_dict)


@router.get("/admin/support-messages/{message_id}/photos/{photo_id}")
async def get_support_message_photo(
    message_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get a support message photo file (admin only)."""
    photo = SupportMessagePhotoRepository.get_by_id(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} not found"
        )
    
    if photo.support_message_id != message_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Photo {photo_id} does not belong to message {message_id}"
        )
    
    full_path = get_full_file_path(photo.file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo file not found: {photo.file_path}"
        )
    
    return FileResponse(
        full_path,
        media_type=photo.mime_type,
        filename=photo.file_name,
    )


@router.post("/admin/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Upload a photo file and return the file path."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        max_size = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size ({settings.MAX_PHOTO_SIZE_MB}MB)"
            )
        
        # Validate MIME type
        mime_type = file.content_type or "image/jpeg"
        if not mime_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Save file with compression
        file_path = save_support_photo(file_content, file.filename or "photo.jpg", mime_type, compress=True)
        
        # Return JPEG mime type for compressed images
        return {"file_path": file_path, "filename": file.filename, "mime_type": "image/jpeg"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload photo: {str(e)}"
        )


@router.put("/admin/support-messages/{message_id}/respond", response_model=SupportMessageResponse)
async def respond_to_support_message(
    message_id: int,
    response_data: dict,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Respond to a support message (admin only)."""
    from api.models.support_message import SupportMessageStatus
    from api.core.config import settings
    import os
    import httpx
    
    message = SupportMessageRepository.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    admin_response = response_data.get('admin_response', '')
    photo_file_ids = response_data.get('photo_file_ids', [])
    photo_paths = response_data.get('photo_paths', [])
    
    if not admin_response and not photo_file_ids and not photo_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="admin_response or photos are required"
        )
    
    admin_username = current_admin.get("sub", "admin")
    
    # Handle photos if provided
    photo_file_ids = response_data.get('photo_file_ids', [])
    photo_paths = response_data.get('photo_paths', [])  # Paths from uploaded files
    
    # Process photo_paths (from direct upload) - save to database for history
    if photo_paths:
        logger.info(f"Processing {len(photo_paths)} photos from uploaded files for admin response to message {message_id}")
        for photo_path in photo_paths:
            try:
                # Get file info
                from api.services.file_storage_service import get_full_file_path
                full_path = get_full_file_path(photo_path)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    filename = os.path.basename(photo_path)
                    
                    # Determine MIME type from extension
                    import mimetypes
                    mime_type, _ = mimetypes.guess_type(full_path)
                    if not mime_type:
                        mime_type = "image/jpeg"
                    
                    # Create photo record
                    SupportMessagePhotoRepository.create(
                        db=db,
                        support_message_id=message_id,
                        file_path=photo_path,
                        file_name=filename,
                        file_size=file_size,
                        mime_type=mime_type,
                        is_admin_photo=True,
                    )
                    logger.info(f"Added uploaded photo for support message {message_id}: {filename}")
            except Exception as e:
                logger.error(f"Error processing photo path {photo_path}: {e}", exc_info=True)
    
    updated_message = SupportMessageRepository.update(
        db=db,
        message_id=message_id,
        status=SupportMessageStatus.RESPONDED,
        admin_response=admin_response,
        responded_by=admin_username,
    )
    
    if not updated_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    # Send response to user via bot HTTP API
    try:
        # Get user's telegram_user_id
        telegram_user_id = message.user.telegram_user_id if message.user else None
        
        if telegram_user_id:
            # Send request to bot's HTTP API
            bot_api_url = os.getenv('BOT_API_URL', 'http://bot:8002')
            if not bot_api_url:
                logger.warning("BOT_API_URL not configured, cannot send support response")
            else:
                async with httpx.AsyncClient() as client:
                    # Send photo_file_ids if available (bot will use them directly)
                    # Otherwise send photo_paths if available (uploaded files)
                    request_data = {
                        "telegram_user_id": telegram_user_id,
                        "original_message": message.message,
                        "admin_response": admin_response,
                    }
                    if photo_file_ids:
                        request_data["photo_file_ids"] = photo_file_ids
                    elif photo_paths:
                        request_data["photo_paths"] = photo_paths
                    
                    response = await client.post(
                        f"{bot_api_url}/send-support-response",
                        json=request_data,
                        timeout=30.0,  # Increased timeout for file operations
                    )
                    if response.status_code != 200:
                        logger.warning(f"Failed to send message to user {telegram_user_id}: {response.text}")
                    else:
                        logger.info(f"Successfully sent support response to user {telegram_user_id}")
        else:
            logger.warning(f"User {message.user_id} has no telegram_user_id, cannot send support response")
    except Exception as e:
        logger.error(f"Error sending support response to user: {e}", exc_info=True)
        # Don't fail the request if sending fails - message is already saved
    
    # Refresh to get photos
    db.refresh(updated_message)
    msg_dict = SupportMessageResponse.model_validate(updated_message).model_dump()
    if updated_message.user:
        msg_dict['username'] = updated_message.user.username
        msg_dict['first_name'] = updated_message.user.first_name
        msg_dict['last_name'] = updated_message.user.last_name
    
    return SupportMessageResponse(**msg_dict)


@router.put("/admin/support-messages/{message_id}", response_model=SupportMessageResponse)
async def update_support_message(
    message_id: int,
    message_data: SupportMessageUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update a support message (admin only)."""
    message = SupportMessageRepository.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    updated_message = SupportMessageRepository.update(
        db=db,
        message_id=message_id,
        status=message_data.status,
        admin_response=message_data.admin_response,
    )
    
    if not updated_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    msg_dict = SupportMessageResponse.model_validate(updated_message).model_dump()
    if updated_message.user:
        msg_dict['username'] = updated_message.user.username
        msg_dict['first_name'] = updated_message.user.first_name
        msg_dict['last_name'] = updated_message.user.last_name
    
    return SupportMessageResponse(**msg_dict)


@router.post("/admin/send-message")
async def send_message_to_user(
    request_data: dict,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Send a direct message to a user (admin only)."""
    import os
    import httpx
    from api.services.file_storage_service import get_full_file_path
    from api.repositories.user_repository import UserRepository
    from api.repositories.admin_message_repository import AdminMessageRepository
    from api.repositories.admin_message_photo_repository import AdminMessagePhotoRepository
    
    telegram_user_id = request_data.get("telegram_user_id")
    message = request_data.get("message")
    photo_file_ids = request_data.get("photo_file_ids", [])
    photo_paths = request_data.get("photo_paths", [])  # Paths from uploaded files
    
    if not telegram_user_id or (not message and not photo_paths and not photo_file_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="telegram_user_id and either message or photos are required"
        )
    
    # Get user by telegram_user_id
    user = UserRepository.get_by_telegram_id(db, telegram_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_user_id {telegram_user_id} not found"
        )
    
    admin_username = current_admin.get("sub", "admin")
    
    # Save message to database
    admin_message = AdminMessageRepository.create(
        db=db,
        user_id=user.id,
        message=message,
        sent_by=admin_username,
    )
    
    # Process photo_paths (from direct upload) - save to database
    if photo_paths:
        logger.info(f"Processing {len(photo_paths)} photos from uploaded files for direct message to user {telegram_user_id}")
        for photo_path in photo_paths:
            try:
                full_path = get_full_file_path(photo_path)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    filename = os.path.basename(photo_path)
                    
                    # Determine MIME type from extension
                    import mimetypes
                    mime_type, _ = mimetypes.guess_type(full_path)
                    if not mime_type:
                        mime_type = "image/jpeg"
                    
                    # Create photo record
                    AdminMessagePhotoRepository.create(
                        db=db,
                        admin_message_id=admin_message.id,
                        file_path=photo_path,
                        file_name=filename,
                        file_size=file_size,
                        mime_type=mime_type,
                    )
                    logger.info(f"Saved uploaded photo for admin message {admin_message.id}: {filename}")
                else:
                    logger.warning(f"Photo file not found: {full_path}")
            except Exception as e:
                logger.error(f"Error processing photo path {photo_path}: {e}", exc_info=True)
    
    # Get bot API URL from environment
    bot_api_url = os.getenv('BOT_API_URL', 'http://bot:8002')
    if not bot_api_url:
        logger.warning("BOT_API_URL not configured, cannot send direct message")
        raise HTTPException(status_code=500, detail="Bot API URL not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            request_payload = {
                "telegram_user_id": telegram_user_id,
                "message": message or "",
            }
            # Send photo_file_ids if available (bot will use them directly)
            # Otherwise send photo_paths if available (uploaded files)
            if photo_file_ids:
                request_payload["photo_file_ids"] = photo_file_ids
            elif photo_paths:
                request_payload["photo_paths"] = photo_paths
            
            response = await client.post(
                f"{bot_api_url}/send-direct-message",
                json=request_payload,
                timeout=30.0,  # Increased timeout for file operations
            )
            response.raise_for_status()
            return {"status": "success", "message": "Message sent successfully"}
    except httpx.HTTPStatusError as e:
        # Get error details from bot API response
        error_detail = f"Failed to send message"
        try:
            error_data = e.response.json()
            if "detail" in error_data:
                error_detail = error_data["detail"]
        except:
            error_detail = f"Failed to send message: {e.response.text if hasattr(e.response, 'text') else str(e)}"
        
        logger.error(f"Failed to send message to bot API: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to send message to bot API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.delete("/admin/support-messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_support_message(
    message_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a support message (soft delete by default, hard delete if hard=true)."""
    message = SupportMessageRepository.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    if hard:
        from api.services.file_storage_service import delete_support_photo
        # Delete all photos associated with this message
        photos = SupportMessagePhotoRepository.get_by_support_message_id(db, message_id)
        for photo in photos:
            delete_support_photo(photo.file_path)
    
    if not SupportMessageRepository.delete(db, message_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    return None


@router.get("/admin/admin-messages", response_model=List[AdminMessageResponse])
async def get_admin_messages(
    user_id: Optional[int] = None,
    sent_by: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get admin messages history (admin only)."""
    from api.repositories.admin_message_photo_repository import AdminMessagePhotoRepository
    
    # Parse date strings
    date_from_obj = None
    date_to_obj = None
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use ISO format."
            )
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use ISO format."
            )
    
    # Get messages
    messages = AdminMessageRepository.get_all(
        db=db,
        user_id=user_id,
        sent_by=sent_by,
        date_from=date_from_obj,
        date_to=date_to_obj,
        limit=limit,
        offset=offset,
    )
    
    # Build response with user info and photos
    result = []
    for msg in messages:
        msg_dict = AdminMessageResponse.model_validate(msg).model_dump()
        if msg.user:
            msg_dict['username'] = msg.user.username
            msg_dict['first_name'] = msg.user.first_name
            msg_dict['last_name'] = msg.user.last_name
        
        # Get photos
        photos = AdminMessagePhotoRepository.get_by_admin_message_id(db, msg.id)
        msg_dict['photos'] = [AdminMessagePhotoResponse.model_validate(photo).model_dump() for photo in photos]
        
        result.append(AdminMessageResponse(**msg_dict))
    
    return result


@router.delete("/admin/admin-messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_message(
    message_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete an admin message (soft delete by default, hard delete if hard=true)."""
    message = AdminMessageRepository.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin message with id {message_id} not found"
        )
    
    if hard:
        from api.services.file_storage_service import delete_support_photo
        from api.repositories.admin_message_photo_repository import AdminMessagePhotoRepository
        # Delete all photos associated with this message
        photos = AdminMessagePhotoRepository.get_by_admin_message_id(db, message_id)
        for photo in photos:
            delete_support_photo(photo.file_path)
    
    if not AdminMessageRepository.delete(db, message_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin message with id {message_id} not found"
        )
    return None


@router.get("/admin/admin-messages/{message_id}/photos/{photo_id}")
async def get_admin_message_photo(
    message_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get an admin message photo file (admin only)."""
    from api.repositories.admin_message_photo_repository import AdminMessagePhotoRepository
    
    photo = AdminMessagePhotoRepository.get_by_id(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} not found"
        )
    
    if photo.admin_message_id != message_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Photo {photo_id} does not belong to message {message_id}"
        )
    
    full_path = get_full_file_path(photo.file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo file not found: {photo.file_path}"
        )
    
    return FileResponse(
        full_path,
        media_type=photo.mime_type,
        filename=photo.file_name,
    )
# Staff Users CRUD
@router.get("/admin/staff-users", response_model=StaffUserListResponse)
async def get_all_staff_users(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all staff users (admin only)."""
    staff_users = StaffUserRepository.get_all(db)
    return StaffUserListResponse(staff_users=[StaffUserResponse.model_validate(user) for user in staff_users])


@router.post("/admin/staff-users", response_model=StaffUserResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_user(
    user_data: StaffUserCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new staff user (admin only)."""
    # Check if staff user with this telegram_user_id already exists
    existing_staff_user = StaffUserRepository.get_by_telegram_id(db, user_data.telegram_user_id)
    if existing_staff_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Staff user with telegram_user_id {user_data.telegram_user_id} already exists"
        )
    
    staff_user = StaffUserRepository.create(
        db,
        telegram_user_id=user_data.telegram_user_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    return StaffUserResponse.model_validate(staff_user)


@router.put("/admin/staff-users/{staff_user_id}", response_model=StaffUserResponse)
async def update_staff_user(
    staff_user_id: int,
    user_data: StaffUserUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update a staff user (admin only)."""
    staff_user = StaffUserRepository.get_by_id(db, staff_user_id)
    if not staff_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff user with id {staff_user_id} not found"
        )
    
    updated_staff_user = StaffUserRepository.update(
        db,
        staff_user_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    if not updated_staff_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff user with id {staff_user_id} not found"
        )
    
    return StaffUserResponse.model_validate(updated_staff_user)


@router.delete("/admin/staff-users/{staff_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_user(
    staff_user_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a staff user (soft delete by default, hard delete if hard=true)."""
    if not StaffUserRepository.delete(db, staff_user_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff user with id {staff_user_id} not found"
        )
    return None


# Menu Photos CRUD
@router.get("/admin/menu-photos", response_model=MenuPhotoListResponse)
async def get_menu_photos(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all menu photos (admin only)."""
    photos = MenuPhotoRepository.get_all(db)
    return MenuPhotoListResponse(photos=[MenuPhotoResponse.model_validate(photo) for photo in photos])


@router.get("/admin/menu-photos/{photo_id}/file")
async def get_menu_photo_file(
    photo_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get menu photo file (admin only)."""
    photo = MenuPhotoRepository.get_by_id(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu photo with id {photo_id} not found"
        )
    
    full_path = get_full_file_path(photo.file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo file not found: {photo.file_path}"
        )
    
    return FileResponse(
        full_path,
        media_type=photo.mime_type,
        filename=photo.file_name,
    )


@router.post("/admin/menu-photos", response_model=MenuPhotoResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Upload a new menu photo (admin only)."""
    # Check current count
    current_count = MenuPhotoRepository.get_count(db)
    if current_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 menu photos allowed"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        max_size = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size ({settings.MAX_PHOTO_SIZE_MB}MB)"
            )
        
        # Validate MIME type
        mime_type = file.content_type or "image/jpeg"
        if not mime_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Save file with compression
        from api.services.file_storage_service import save_menu_photo
        file_path = save_menu_photo(file_content, file.filename or "photo.jpg", mime_type, compress=True)
        
        # Get next display_order
        display_order = MenuPhotoRepository.get_max_display_order(db)
        
        # Create photo record
        menu_photo = MenuPhotoRepository.create(
            db=db,
            file_path=file_path,
            file_name=file.filename or "photo.jpg",
            file_size=len(file_content),
            mime_type="image/jpeg",  # Always JPEG after compression
            display_order=display_order,
        )
        
        return MenuPhotoResponse.model_validate(menu_photo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading menu photo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload menu photo: {str(e)}"
        )


@router.delete("/admin/menu-photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_photo(
    photo_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a menu photo (admin only)."""
    if hard:
        from api.services.file_storage_service import delete_menu_photo as delete_file
        menu_photo = db.query(MenuPhoto).filter(MenuPhoto.id == photo_id).first()
        if menu_photo:
            delete_file(menu_photo.file_path)
    
    if not MenuPhotoRepository.delete(db, photo_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu photo with id {photo_id} not found"
        )
    return None


@router.put("/admin/menu-photos/reorder", status_code=status.HTTP_200_OK)
async def reorder_menu_photos(
    reorder_request: MenuPhotoReorderRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Reorder menu photos (admin only)."""
    try:
        # Convert to list of dicts for repository
        photo_orders = [{"id": item.id, "display_order": item.display_order} for item in reorder_request.photos]
        success = MenuPhotoRepository.reorder(db, photo_orders)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reorder menu photos"
            )
        return {"message": "Menu photos reordered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering menu photos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder menu photos: {str(e)}"
        )


# Music Management endpoints

@router.get("/admin/music-queue", response_model=MusicQueueListResponse)
async def get_music_queue(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get music queue (admin only)."""
    queue_items = MusicQueueRepository.get_all(db)
    
    # request_count is now stored directly in MusicQueue, no need to search in MusicRequest
    queue_responses = []
    for item in queue_items:
        queue_dict = {
            "id": item.id,
            "track_title": item.track_title,
            "track_artist": item.track_artist,
            "yandex_music_url": item.yandex_music_url,
            "other_source_url": item.other_source_url,
            "queue_order": item.queue_order,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "request_count": item.request_count,
        }
        queue_responses.append(MusicQueueResponse.model_validate(queue_dict))
    
    return MusicQueueListResponse(queue=queue_responses)


@router.get("/admin/music-wishlist", response_model=MusicRequestListResponse)
async def get_music_wishlist(
    event_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get music wishlist (admin only)."""
    requests = MusicRequestRepository.get_all(db, event_id=event_id)
    return MusicRequestListResponse(requests=[MusicRequestResponse.model_validate(req) for req in requests])


@router.post("/admin/music-queue", response_model=MusicQueueResponse, status_code=status.HTTP_201_CREATED)
async def create_music_queue_item(
    queue_data: MusicQueueCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Add a track to music queue (admin only)."""
    queue_item = MusicQueueRepository.create(
        db,
        track_title=queue_data.track_title,
        track_artist=queue_data.track_artist,
        yandex_music_url=queue_data.yandex_music_url,
        other_source_url=queue_data.other_source_url,
    )
    return MusicQueueResponse.model_validate(queue_item)


@router.put("/admin/music-queue/reorder", status_code=status.HTTP_200_OK)
async def reorder_music_queue(
    reorder_request: MusicQueueReorderRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Reorder music queue items (admin only)."""
    try:
        queue_orders = [{"id": item.id, "queue_order": item.queue_order} for item in reorder_request.items]
        success = MusicQueueRepository.reorder(db, queue_orders)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reorder music queue"
            )
        return {"message": "Music queue reordered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering music queue: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder music queue: {str(e)}"
        )


@router.delete("/admin/music-queue/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_music_queue_item(
    queue_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a music queue item (admin only)."""
    if not MusicQueueRepository.delete(db, queue_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Music queue item with id {queue_id} not found"
        )
    return None


@router.delete("/admin/music-wishlist/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_music_request(
    request_id: int,
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a music request from wishlist (admin only)."""
    if not MusicRequestRepository.delete(db, request_id, hard=hard):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Music request with id {request_id} not found"
        )
    return None


@router.post("/admin/music-wishlist/{request_id}/move-to-queue", response_model=MusicQueueResponse, status_code=status.HTTP_201_CREATED)
async def move_music_request_to_queue(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Move a music request from wishlist to queue (admin only)."""
    music_request = MusicRequestRepository.get_by_id(db, request_id)
    if not music_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Music request with id {request_id} not found"
        )
    
    # Check if track already exists in queue
    from api.models.music_queue import MusicQueue
    existing_queue_item = db.query(MusicQueue).filter(
        MusicQueue.track_title == music_request.track_title,
        MusicQueue.track_artist == music_request.track_artist,
        MusicQueue.is_deleted == False
    ).first()
    
    if existing_queue_item:
        # Track already in queue, update request_count by adding the request_count from the request being moved
        # This preserves the total request count even after hard delete
        existing_queue_item.request_count = max(
            existing_queue_item.request_count,
            music_request.request_count
        )
        db.commit()
        db.refresh(existing_queue_item)
        
        # Delete the request from wishlist (hard delete - moving between columns)
        MusicRequestRepository.delete(db, request_id, hard=True)
        return MusicQueueResponse.model_validate(existing_queue_item)
    
    # Create queue item with request_count from the request being moved
    queue_item = MusicQueueRepository.create(
        db,
        track_title=music_request.track_title,
        track_artist=music_request.track_artist,
        yandex_music_url=music_request.yandex_music_url,
        other_source_url=music_request.other_source_url,
        request_count=music_request.request_count,
    )
    
    # Delete the request from wishlist (hard delete - moving between columns)
    MusicRequestRepository.delete(db, request_id, hard=True)
    
    return MusicQueueResponse.model_validate(queue_item)


@router.post("/admin/music-queue/{queue_id}/move-to-wishlist", response_model=MusicRequestResponse, status_code=status.HTTP_201_CREATED)
async def move_music_queue_to_wishlist(
    queue_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Move a music queue item back to wishlist (admin only)."""
    queue_item = MusicQueueRepository.get_by_id(db, queue_id)
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Music queue item with id {queue_id} not found"
        )
    
    # Find active request with same title and artist (if exists)
    from api.models.music_request import MusicRequest
    existing_request = db.query(MusicRequest).filter(
        MusicRequest.track_title == queue_item.track_title,
        MusicRequest.track_artist == queue_item.track_artist,
        MusicRequest.is_deleted == False
    ).first()
    
    if existing_request:
        # Request already exists in wishlist, just delete queue item (hard delete - moving between columns)
        MusicQueueRepository.delete(db, queue_id, hard=True)
        return MusicRequestResponse.model_validate(existing_request)
    
    # If no existing request found, we need to create a new one
    # But we don't have user_id and event_id, so we'll use a default event
    # This is a fallback - ideally we should preserve the original request
    from api.repositories.event_repository import EventRepository
    active_events = EventRepository.get_all_active(db)
    if not active_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active event found. Cannot move track to wishlist without an event."
        )
    active_event = active_events[0]  # Use first active event
    
    # Create a new request (we'll use a system user or the first user)
    from api.repositories.user_repository import UserRepository
    users = UserRepository.get_all(db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users found. Cannot create music request."
        )
    
    # Create new request
    music_request = MusicRequestRepository.create(
        db,
        user_id=users[0].id,  # Use first user as fallback
        event_id=active_event.id,
        track_title=queue_item.track_title,
        track_artist=queue_item.track_artist,
        yandex_music_url=queue_item.yandex_music_url,
        other_source_url=queue_item.other_source_url,
    )
    
    # Delete queue item (hard delete - moving between columns)
    MusicQueueRepository.delete(db, queue_id, hard=True)
    
    return MusicRequestResponse.model_validate(music_request)


@router.delete("/admin/music-queue/batch", status_code=status.HTTP_200_OK)
async def delete_music_queue_batch(
    queue_ids: List[int] = Body(...),
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete multiple music queue items (admin only)."""
    count = MusicQueueRepository.delete_batch(db, queue_ids, hard=hard)
    return {"deleted_count": count}


@router.delete("/admin/music-wishlist/batch", status_code=status.HTTP_200_OK)
async def delete_music_wishlist_batch(
    request_ids: List[int] = Body(...),
    hard: bool = False,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete multiple music requests from wishlist (admin only)."""
    count = MusicRequestRepository.delete_batch(db, request_ids, hard=hard)
    return {"deleted_count": count}

