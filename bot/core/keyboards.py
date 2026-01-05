"""Keyboard builders - only inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.i18n import t

def get_main_menu_keyboard(locale: str, has_menu_photos: bool = False) -> InlineKeyboardMarkup:
    """Get main menu keyboard.
    
    Args:
        locale: User locale
        has_menu_photos: Whether menu photos exist (to show menu button)
    """
    builder = InlineKeyboardBuilder()
    # Buy ticket and My tickets on the same row
    builder.add(InlineKeyboardButton(text=t(locale, "buttons.buy_ticket"), callback_data="menu_buy_ticket"))
    builder.add(InlineKeyboardButton(text=t(locale, "buttons.my_tickets"), callback_data="menu_my_tickets"))
    builder.adjust(2)  # 2 buttons per row
    # Other buttons on separate rows
    # Menu button (if exists) should be above Club info
    if has_menu_photos:
        builder.row(InlineKeyboardButton(text=t(locale, "buttons.menu"), callback_data="menu_food_drinks"))
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.club_info"), callback_data="menu_club_info"))
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.support"), callback_data="menu_support"))
    return builder.as_markup()


def get_back_to_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    """Get 'back to main menu' button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=t(locale, "buttons.back_to_menu"), callback_data="back_to_menu"))
    return builder.as_markup()


def get_back_keyboard(locale: str) -> InlineKeyboardMarkup:
    """Generic back button for screens (goes to main menu)."""
    return get_back_to_menu_keyboard(locale)


def format_date_without_year(date_str: str) -> str:
    """Format date from DD.MM.YYYY to DD.MM."""
    if not date_str:
        return date_str
    # Split by dot and take first two parts (DD and MM)
    parts = date_str.split('.')
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return date_str


def get_events_keyboard(locale: str, events: list) -> InlineKeyboardMarkup:
    """Get events list keyboard."""
    builder = InlineKeyboardBuilder()
    for event in events:
        event_name = event.get('name', 'Event')
        
        # Format event date/time - only start date/time for inline buttons, without year
        start_date = event.get('start_date', '')
        start_time = event.get('start_time', '')
        
        # Format as "DD.MM HH:MM" (without year and without end date/time)
        start_date_short = format_date_without_year(start_date)
        event_datetime = f"{start_date_short} {start_time}" if start_date_short and start_time else f"{start_date} {start_time}"
        
        event_text = f"{event_name}\n{event_datetime}"
        builder.add(InlineKeyboardButton(
            text=event_text,
            callback_data=f"event_{event.get('id')}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back_to_menu"), callback_data="back_to_menu"))
    return builder.as_markup()


def get_ticket_types_keyboard(locale: str, ticket_types: list) -> InlineKeyboardMarkup:
    """Get ticket types keyboard."""
    builder = InlineKeyboardBuilder()
    for ticket_type in ticket_types:
        available = ticket_type.get('available_quantity', ticket_type.get('available', 0))
        # Skip ticket types with zero availability
        if available <= 0:
            continue
        available_text = f" ({available} {t(locale, 'labels.available')})" if available > 0 else ""
        price = ticket_type.get('price', 0)
        if isinstance(price, str):
            price = float(price)
        price_formatted = int(price) if isinstance(price, float) and price.is_integer() or isinstance(price, int) else price
        ticket_text = f"🎫 {ticket_type.get('name', 'Type')} - {price_formatted} ₽{available_text}"
        builder.add(InlineKeyboardButton(
            text=ticket_text,
            callback_data=f"ticket_type_{ticket_type.get('id')}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back"), callback_data="back_to_events"))
    return builder.as_markup()


def get_quantity_keyboard(locale: str, max_quantity: int = 5) -> InlineKeyboardMarkup:
    """Get quantity selection keyboard."""
    builder = InlineKeyboardBuilder()
    for i in range(1, min(max_quantity + 1, 6)):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"quantity_{i}"))
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back"), callback_data="back_to_ticket_types"))
    return builder.as_markup()


def get_confirm_order_keyboard(locale: str, total_price: float = None) -> InlineKeyboardMarkup:
    """Get order confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    confirm_text = t(locale, "buttons.confirm")
    if total_price is not None:
        price_formatted = int(total_price) if isinstance(total_price, float) and total_price.is_integer() else total_price
        confirm_text = f"{confirm_text} ({price_formatted} ₽)"
    builder.row(InlineKeyboardButton(text=confirm_text, callback_data="confirm_order"))
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back"), callback_data="back_to_quantity"))
    return builder.as_markup()


def get_support_cancel_keyboard(locale: str) -> InlineKeyboardMarkup:
    """Support screen keyboard - only back button."""
    return get_back_keyboard(locale)


def get_tickets_keyboard(locale: str, tickets: list) -> InlineKeyboardMarkup:
    """Get tickets list keyboard."""
    builder = InlineKeyboardBuilder()
    for ticket in tickets:
        status_emoji = "✅" if ticket.get("status") == "active" else "❌"
        # event_date already contains formatted datetime range from tickets handler
        event_datetime = ticket.get('event_date', '')
        ticket_text = f"{status_emoji} {ticket.get('event_name', 'Event')}\n{event_datetime}"
        builder.add(InlineKeyboardButton(
            text=ticket_text,
            callback_data=f"ticket_{ticket.get('id')}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back_to_menu"), callback_data="back_to_menu"))
    return builder.as_markup()
