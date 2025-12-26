"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from api.models.ticket import TicketStatus
from api.models.payment import PaymentStatus


# User schemas
class UserCreate(BaseModel):
    """Schema for creating a user."""
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Event schemas
class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    name: str
    description: Optional[str] = None
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    djs: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Schema for list of events."""
    events: List[EventResponse]


# TicketType schemas
class TicketTypeResponse(BaseModel):
    """Schema for ticket type response."""
    id: int
    event_id: int
    name: str
    price: Decimal
    available_quantity: int
    total_quantity: int
    is_active: bool

    class Config:
        from_attributes = True


class TicketTypeListResponse(BaseModel):
    """Schema for list of ticket types."""
    ticket_types: List[TicketTypeResponse]


# TicketTypeTemplate schemas
class TicketTypeTemplateResponse(BaseModel):
    """Schema for ticket type template response."""
    id: int
    name: str
    price: Decimal
    available_quantity: int
    total_quantity: int

    class Config:
        from_attributes = True


class TicketTypeTemplateCreate(BaseModel):
    """Schema for creating a ticket type template."""
    name: str
    price: Decimal
    available_quantity: int
    total_quantity: int


class TicketTypeTemplateListResponse(BaseModel):
    """Schema for list of ticket type templates."""
    templates: List[TicketTypeTemplateResponse]


# Ticket schemas
class TicketResponse(BaseModel):
    """Schema for ticket response."""
    id: int
    user_id: int
    event_id: int
    ticket_type_id: int
    token: str
    status: TicketStatus
    used_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # Related data
    event: Optional[EventResponse] = None
    ticket_type: Optional[TicketTypeResponse] = None
    username: Optional[str] = None  # Telegram username
    first_name: Optional[str] = None  # User first name
    last_name: Optional[str] = None  # User last name

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    """Schema for creating a ticket."""
    user_id: int
    event_id: int
    ticket_type_id: int
    token: Optional[str] = None  # If not provided, will be auto-generated
    status: Optional[TicketStatus] = TicketStatus.ACTIVE


class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    user_id: Optional[int] = None
    event_id: Optional[int] = None
    ticket_type_id: Optional[int] = None
    token: Optional[str] = None
    status: Optional[TicketStatus] = None


class TicketListResponse(BaseModel):
    """Schema for list of tickets."""
    tickets: List[TicketResponse]


class TicketDetailResponse(BaseModel):
    """Schema for detailed ticket response with all related data."""
    id: int
    user_id: int
    event_id: int
    ticket_type_id: int
    token: str
    status: TicketStatus
    used_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    event: EventResponse
    ticket_type: TicketTypeResponse
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# Payment schemas
class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: int
    user_id: int
    order_id: Optional[str] = None
    yookassa_payment_id: Optional[str] = None
    telegram_payment_charge_id: Optional[str] = None
    amount: Decimal
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order schemas
class OrderCreate(BaseModel):
    """Schema for creating an order."""
    user_id: int
    event_id: int
    ticket_type_id: int
    quantity: int = Field(gt=0, le=10, description="Quantity of tickets (1-10)")
    promocode: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema for order response with payment invoice data."""
    order_id: str
    payment_id: int
    amount: float  # Changed from Decimal to float for JSON serialization
    invoice_title: str
    invoice_description: str
    invoice_payload: str
    invoice_prices: List[dict]  # List of {"label": str, "amount": int}
    provider_token: str  # YooKassa provider token from BotFather


# Refund schemas
class TicketRefundRequest(BaseModel):
    """Schema for ticket refund request."""
    ticket_id: int


class TicketRefundResponse(BaseModel):
    """Schema for ticket refund response."""
    ticket_id: int
    status: TicketStatus
    refunded_at: datetime
    message: str


# Mark ticket as used
class TicketMarkUsedRequest(BaseModel):
    """Schema for marking ticket as used."""
    ticket_id: int


class TicketMarkUsedResponse(BaseModel):
    """Schema for marking ticket as used response."""
    ticket_id: int
    status: TicketStatus
    used_at: datetime
    message: str


# Expiration Settings schemas
class ExpirationSettingsResponse(BaseModel):
    """Schema for expiration settings response."""
    id: int
    ticket_expiration_enabled: bool
    event_deactivation_enabled: bool
    check_interval_minutes: int
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpirationSettingsUpdate(BaseModel):
    """Schema for updating expiration settings."""
    ticket_expiration_enabled: bool | None = None
    event_deactivation_enabled: bool | None = None
    check_interval_minutes: int | None = None


class ClubSettingsResponse(BaseModel):
    """Schema for club settings response."""
    id: int
    address: str | None
    phone: str | None
    email: str | None
    auto_deactivate_events: bool = True  # Default to True for backward compatibility
    timezone: str = "Europe/Moscow"  # Default timezone for backward compatibility
    updated_at: datetime

    class Config:
        from_attributes = True


class ClubSettingsUpdate(BaseModel):
    """Schema for updating club settings."""
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    auto_deactivate_events: bool | None = None
    timezone: str | None = None

