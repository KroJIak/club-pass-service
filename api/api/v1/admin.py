"""Admin CRUD endpoints for all models."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
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
from api.repositories.promocode_repository import PromocodeRepository
from api.repositories.expiration_settings_repository import ExpirationSettingsRepository
from api.repositories.club_settings_repository import ClubSettingsRepository
from api.repositories.support_message_repository import SupportMessageRepository
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
    SupportMessageCreate,
    SupportMessageUpdate,
    SupportMessageListResponse,
)
from api.models import Event, TicketType, TicketTypeTemplate, Ticket, Payment, Order, Promocode, SupportMessage
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
    promocode: Optional[str] = None
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
    promocode: Optional[str] = None
    payment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    username: Optional[str] = None  # Telegram username
    first_name: Optional[str] = None  # User first name
    last_name: Optional[str] = None  # User last name
    event_name: Optional[str] = None  # Event name
    ticket_type_name: Optional[str] = None  # Ticket type name

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for list of orders."""
    orders: List[OrderAdminResponse]


# Promocode schemas
class PromocodeCreate(BaseModel):
    """Schema for creating a promocode."""
    code: str
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    valid_from: datetime
    valid_until: datetime
    usage_limit: Optional[int] = None
    is_active: bool = True


class PromocodeUpdate(BaseModel):
    """Schema for updating a promocode."""
    code: Optional[str] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    usage_limit: Optional[int] = None
    is_active: Optional[bool] = None


class PromocodeResponse(BaseModel):
    """Schema for promocode response."""
    id: int
    code: str
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    valid_from: datetime
    valid_until: datetime
    usage_limit: Optional[int] = None
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromocodeListResponse(BaseModel):
    """Schema for list of promocodes."""
    promocodes: List[PromocodeResponse]


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
        if event_data.is_active and event_data.end_date and event_data.end_time:
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
    will_be_active = event_data.is_active if event_data.is_active is not None else event.is_active
    if will_be_active:
        end_date_to_check = event_data.end_date if event_data.end_date is not None else event.end_date
        end_time_to_check = event_data.end_time if event_data.end_time is not None else event.end_time
        
        if end_date_to_check and end_time_to_check:
            from datetime import datetime
            import pytz
            from api.repositories.club_settings_repository import ClubSettingsRepository
            
            try:
                # Get timezone from club settings
                club_settings = ClubSettingsRepository.get_settings(db)
                timezone_str = getattr(club_settings, 'timezone', 'Europe/Moscow')
                if not timezone_str:
                    timezone_str = 'Europe/Moscow'
                
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
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete an event (hard delete)."""
    from api.models.order import Order
    from api.models.ticket import Ticket
    
    event = EventRepository.get_by_id(db, event_id)
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
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a ticket type (hard delete)."""
    ticket_type = TicketTypeRepository.get_by_id(db, ticket_type_id)
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket type with id {ticket_type_id} not found"
        )
    
    db.delete(ticket_type)
    db.commit()
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
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a ticket type template."""
    if not TicketTypeTemplateRepository.delete(db, template_id):
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
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a user."""
    success = UserRepository.delete(db, user_id)
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
        ticket.status = TicketStatus(status_value)
        logger.info(f"Updated status from {old_status} to {ticket.status}")
        # Set used_at when status changes to USED
        if ticket.status == TicketStatus.USED and not ticket.used_at:
            ticket.used_at = datetime.utcnow()
    
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
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a ticket."""
    ticket = TicketRepository.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found"
        )
    
    db.delete(ticket)
    db.commit()
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
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete an order (admin only)."""
    success = OrderRepository.delete(db, order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )


# Promocodes CRUD
@router.get("/admin/promocodes", response_model=PromocodeListResponse)
async def get_all_promocodes(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get all promocodes (admin only)."""
    promocodes = PromocodeRepository.get_all(db)
    return PromocodeListResponse(promocodes=[PromocodeResponse.model_validate(p) for p in promocodes])


@router.get("/admin/promocodes/{promocode_id}", response_model=PromocodeResponse)
async def get_promocode(
    promocode_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Get promocode by ID (admin only)."""
    promocode = PromocodeRepository.get_by_id(db, promocode_id)
    if not promocode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promocode with id {promocode_id} not found"
        )
    return PromocodeResponse.model_validate(promocode)


@router.post("/admin/promocodes", response_model=PromocodeResponse)
async def create_promocode(
    promocode_data: PromocodeCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Create a new promocode."""
    # Check if code already exists
    existing = PromocodeRepository.get_by_code(db, promocode_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Promocode with code {promocode_data.code} already exists"
        )
    
    promocode = PromocodeRepository.create(
        db,
        code=promocode_data.code,
        discount_percent=promocode_data.discount_percent,
        discount_amount=promocode_data.discount_amount,
        valid_from=promocode_data.valid_from,
        valid_until=promocode_data.valid_until,
        usage_limit=promocode_data.usage_limit,
        is_active=promocode_data.is_active,
    )
    return PromocodeResponse.model_validate(promocode)


@router.put("/admin/promocodes/{promocode_id}", response_model=PromocodeResponse)
async def update_promocode(
    promocode_id: int,
    promocode_data: PromocodeUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Update a promocode."""
    # Check if code is being changed and already exists
    if promocode_data.code is not None:
        existing = PromocodeRepository.get_by_code(db, promocode_data.code)
        if existing and existing.id != promocode_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promocode with code {promocode_data.code} already exists"
            )
    
    promocode = PromocodeRepository.update(
        db,
        promocode_id,
        code=promocode_data.code,
        discount_percent=promocode_data.discount_percent,
        discount_amount=promocode_data.discount_amount,
        valid_from=promocode_data.valid_from,
        valid_until=promocode_data.valid_until,
        usage_limit=promocode_data.usage_limit,
        is_active=promocode_data.is_active,
    )
    if not promocode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promocode with id {promocode_id} not found"
        )
    return PromocodeResponse.model_validate(promocode)


@router.delete("/admin/promocodes/{promocode_id}")
async def delete_promocode(
    promocode_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a promocode (soft delete by setting is_active=False)."""
    success = PromocodeRepository.delete(db, promocode_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promocode with id {promocode_id} not found"
        )
    return {"message": f"Promocode {promocode_id} deactivated successfully"}


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
    
    response_data = {
        "id": int(settings.id),
        "address": settings.address if settings.address else None,
        "phone": settings.phone if settings.phone else None,
        "email": settings.email if settings.email else None,
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
        settings = ClubSettingsRepository.update_settings(
            db,
            address=settings_update.address,
            phone=settings_update.phone,
            email=settings_update.email,
            auto_deactivate_events=settings_update.auto_deactivate_events,
            timezone=settings_update.timezone
        )
        
        # Ensure updated_at is a datetime object
        updated_at = settings.updated_at
        if updated_at is None:
            updated_at = datetime.utcnow()
        
        response_data = {
            "id": int(settings.id),
            "address": settings.address if settings.address else None,
            "phone": settings.phone if settings.phone else None,
            "email": settings.email if settings.email else None,
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
    
    messages = SupportMessageRepository.get_all(db, status=status_filter)
    
    # Populate user info
    result = []
    for msg in messages:
        msg_dict = SupportMessageResponse.model_validate(msg).model_dump()
        if msg.user:
            msg_dict['username'] = msg.user.username
            msg_dict['first_name'] = msg.user.first_name
            msg_dict['last_name'] = msg.user.last_name
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
    
    return SupportMessageResponse(**msg_dict)


@router.put("/admin/support-messages/{message_id}/respond", response_model=SupportMessageResponse)
async def respond_to_support_message(
    message_id: int,
    response_data: dict,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Respond to a support message (admin only)."""
    from api.models.support_message import SupportMessageStatus
    import os
    import httpx
    
    message = SupportMessageRepository.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    
    admin_response = response_data.get('admin_response')
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="admin_response is required"
        )
    
    admin_username = current_admin.get("sub", "admin")
    
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
    
    # Send response to user via bot using Telegram Bot API
    try:
        # Get user's telegram_user_id
        telegram_user_id = message.user.telegram_user_id if message.user else None
        
        if telegram_user_id:
            # Use Telegram Bot API directly
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if bot_token:
                bot_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                
                # Format message with quote
                formatted_message = (
                    f"<blockquote>{message.message}</blockquote>\n\n"
                    f"{admin_response}"
                )
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        bot_api_url,
                        json={
                            "chat_id": telegram_user_id,
                            "text": formatted_message,
                            "parse_mode": "HTML",
                        },
                        timeout=10.0,
                    )
                    if response.status_code != 200:
                        logger.warning(f"Failed to send message to user {telegram_user_id}: {response.text}")
            else:
                logger.warning("TELEGRAM_BOT_TOKEN not configured, cannot send support response")
        else:
            logger.warning(f"User {message.user_id} has no telegram_user_id, cannot send support response")
    except Exception as e:
        logger.error(f"Error sending support response to user: {e}", exc_info=True)
        # Don't fail the request if sending fails - message is already saved
    
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


@router.delete("/admin/support-messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_support_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete a support message (admin only)."""
    if not SupportMessageRepository.delete(db, message_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Support message with id {message_id} not found"
        )
    return None
