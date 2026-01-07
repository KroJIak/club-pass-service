"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from api.models.ticket import TicketStatus
from api.models.payment import PaymentStatus
from api.models.support_message import SupportMessageStatus


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
    additional_info: str | None = None
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
    additional_info: str | None = None
    auto_deactivate_events: bool | None = None
    timezone: str | None = None


# MenuPhoto schemas
class MenuPhotoResponse(BaseModel):
    """Schema for menu photo response."""
    id: int
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuPhotoListResponse(BaseModel):
    """Schema for menu photos list response."""
    photos: List[MenuPhotoResponse]


class MenuPhotoReorderItem(BaseModel):
    """Schema for menu photo reorder item."""
    id: int
    display_order: int


class MenuPhotoReorderRequest(BaseModel):
    """Schema for menu photo reorder request."""
    photos: List[MenuPhotoReorderItem]


# SupportMessage schemas
class SupportMessagePhotoResponse(BaseModel):
    """Schema for support message photo response."""
    id: int
    support_message_id: int
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    is_admin_photo: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SupportMessageResponse(BaseModel):
    """Schema for support message response."""
    id: int
    user_id: int
    message: str
    status: SupportMessageStatus
    admin_response: Optional[str] = None
    responded_at: Optional[datetime] = None
    responded_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Related data
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photos: List[SupportMessagePhotoResponse] = []

    class Config:
        from_attributes = True


class SupportMessageCreate(BaseModel):
    """Schema for creating a support message."""
    user_id: int
    message: str
    photo_paths: Optional[List[str]] = None


class SupportMessageUpdate(BaseModel):
    """Schema for updating a support message."""
    status: Optional[SupportMessageStatus] = None
    admin_response: Optional[str] = None


# AdminMessage schemas
class AdminMessagePhotoResponse(BaseModel):
    """Schema for admin message photo response."""
    id: int
    admin_message_id: int
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminMessageResponse(BaseModel):
    """Schema for admin message response."""
    id: int
    user_id: int
    message: Optional[str] = None
    sent_by: str
    created_at: datetime
    updated_at: datetime
    # Related data
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photos: List[AdminMessagePhotoResponse] = []

    class Config:
        from_attributes = True
    photo_file_ids: Optional[List[str]] = None


class SupportMessageListResponse(BaseModel):
    """Schema for list of support messages."""
    messages: List[SupportMessageResponse]


# Staff User schemas
class StaffUserCreate(BaseModel):
    """Schema for creating a staff user."""
    telegram_user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class StaffUserResponse(BaseModel):
    """Schema for staff user response."""
    id: int
    telegram_user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StaffUserUpdate(BaseModel):
    """Schema for updating a staff user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class StaffUserListResponse(BaseModel):
    """Schema for list of staff users."""
    staff_users: List[StaffUserResponse]


class StaffAccessCheckResponse(BaseModel):
    """Schema for staff access check response."""
    has_access: bool
    staff_user: Optional[StaffUserResponse] = None


# Music Request schemas
class MusicRequestCreate(BaseModel):
    """Schema for creating a music request."""
    track_title: str
    track_artist: Optional[str] = None
    yandex_music_url: Optional[str] = None
    other_source_url: Optional[str] = None


class MusicRequestResponse(BaseModel):
    """Schema for music request response."""
    id: int
    user_id: int
    event_id: int
    track_title: str
    track_artist: str
    yandex_music_url: Optional[str] = None
    other_source_url: Optional[str] = None
    request_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MusicRequestListResponse(BaseModel):
    """Schema for list of music requests."""
    requests: List[MusicRequestResponse]


# Music Queue schemas
class MusicQueueCreate(BaseModel):
    """Schema for creating a music queue item."""
    track_title: str
    track_artist: str
    yandex_music_url: Optional[str] = None
    other_source_url: Optional[str] = None


class MusicQueueResponse(BaseModel):
    """Schema for music queue response."""
    id: int
    track_title: str
    track_artist: str
    yandex_music_url: Optional[str] = None
    other_source_url: Optional[str] = None
    queue_order: int
    request_count: Optional[int] = 0  # Request count from wishlist
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MusicQueueListResponse(BaseModel):
    """Schema for list of music queue items."""
    queue: List[MusicQueueResponse]


class MusicQueueReorderItem(BaseModel):
    """Schema for reordering music queue items."""
    id: int
    queue_order: int


class MusicQueueReorderRequest(BaseModel):
    """Schema for music queue reorder request."""
    items: List[MusicQueueReorderItem]


# Music Search schemas
class MusicSearchTrackResponse(BaseModel):
    """Schema for music search track response."""
    title: str
    artist: str
    source: str
    links: dict
    album: Optional[str] = None
    release_date: Optional[str] = None
    track_id: Optional[str] = None


class MusicSearchResponse(BaseModel):
    """Schema for music search response."""
    tracks: List[MusicSearchTrackResponse]


# Admin Group schemas
class AdminGroupCreate(BaseModel):
    """Schema for creating an admin group."""
    name: str
    description: Optional[str] = None


class AdminGroupUpdate(BaseModel):
    """Schema for updating an admin group."""
    name: Optional[str] = None
    description: Optional[str] = None


class AdminGroupResponse(BaseModel):
    """Schema for admin group response."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminGroupListResponse(BaseModel):
    """Schema for list of admin groups."""
    groups: List[AdminGroupResponse]


# Admin Account schemas
class AdminAccountCreate(BaseModel):
    """Schema for creating an admin account."""
    group_id: int
    username: str
    password: str
    is_active: bool = True


class AdminAccountUpdate(BaseModel):
    """Schema for updating an admin account."""
    group_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    language: Optional[str] = None


class AdminAccountResponse(BaseModel):
    """Schema for admin account response."""
    id: int
    group_id: int
    username: str
    is_active: bool
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminAccountListResponse(BaseModel):
    """Schema for list of admin accounts."""
    accounts: List[AdminAccountResponse]


class LanguageUpdateRequest(BaseModel):
    """Schema for updating language preference."""
    language: str


# Admin Permission schemas
class AdminPermissionItem(BaseModel):
    """Schema for a single permission."""
    resource: str
    can_read: bool
    can_write: bool
    can_delete: bool


class AdminPermissionUpdateRequest(BaseModel):
    """Schema for updating permissions."""
    permissions: List[AdminPermissionItem]


class AdminPermissionResponse(BaseModel):
    """Schema for admin permission response."""
    id: int
    group_id: int
    resource: str
    can_read: bool
    can_write: bool
    can_delete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminPermissionListResponse(BaseModel):
    """Schema for list of admin permissions."""
    permissions: List[AdminPermissionResponse]


class AdminGroupWithPermissionsResponse(BaseModel):
    """Schema for admin group with permissions."""
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[AdminPermissionResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

