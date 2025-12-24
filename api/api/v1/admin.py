"""Admin CRUD endpoints for all models."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from api.core.db import get_db
from api.core.auth import get_current_admin
from api.repositories.event_repository import EventRepository
from api.repositories.ticket_type_repository import TicketTypeRepository
from api.repositories.user_repository import UserRepository
from api.repositories.ticket_repository import TicketRepository
from api.repositories.payment_repository import PaymentRepository
from api.repositories.order_repository import OrderRepository
from api.repositories.promocode_repository import PromocodeRepository
from api.repositories.expiration_settings_repository import ExpirationSettingsRepository
from api.api.v1.schemas import (
    EventResponse, EventListResponse,
    TicketTypeResponse, TicketTypeListResponse,
    UserResponse, UserCreate, UserUpdate,
    TicketResponse, TicketDetailResponse, TicketUpdate,
    PaymentResponse,
    ExpirationSettingsResponse,
    ExpirationSettingsUpdate,
)
from api.models import Event, TicketType, Ticket, Payment, Order, Promocode
from api.models.ticket import TicketStatus
from api.models.payment import PaymentStatus

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


# User schemas
class UserListResponse(BaseModel):
    """Schema for list of users."""
    users: List[UserResponse]


# Ticket schemas
class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    status: Optional[TicketStatus] = None


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


@router.delete("/admin/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin),
):
    """Delete an event (hard delete)."""
    event = EventRepository.get_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
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
        # Get username from user
        user = UserRepository.get_by_id(db, ticket.user_id)
        if user:
            ticket_data.username = user.username
        ticket_responses.append(ticket_data)
    
    return TicketListResponse(tickets=ticket_responses)


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
    
    if ticket_data.status is not None:
        # Explicitly convert to enum using the value to ensure SQLAlchemy uses the correct string
        status_value = ticket_data.status.value if isinstance(ticket_data.status, TicketStatus) else ticket_data.status
        ticket.status = TicketStatus(status_value)
        # Set used_at when status changes to USED
        if ticket.status == TicketStatus.USED and not ticket.used_at:
            ticket.used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    return TicketResponse.model_validate(ticket)


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
    
    orders = OrderRepository.get_all(db)
    order_responses = []
    for order in orders:
        order_data = OrderAdminResponse.model_validate(order)
        # Get username from user
        user = UserRepository.get_by_id(db, order.user_id)
        if user:
            order_data.username = user.username
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
    order_data = OrderAdminResponse.model_validate(order)
    # Get username from user
    user = UserRepository.get_by_id(db, order.user_id)
    if user:
        order_data.username = user.username
    return order_data


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
    settings = ExpirationSettingsRepository.update_settings(
        db,
        ticket_expiration_enabled=settings_update.ticket_expiration_enabled,
        event_deactivation_enabled=settings_update.event_deactivation_enabled
    )
    return ExpirationSettingsResponse.model_validate(settings)
