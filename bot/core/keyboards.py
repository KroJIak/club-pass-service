"""Keyboard builders - only inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.i18n import t

def get_main_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    builder = InlineKeyboardBuilder()
    # Buy ticket and My tickets on the same row
    builder.add(InlineKeyboardButton(text=t(locale, "buttons.buy_ticket"), callback_data="menu_buy_ticket"))
    builder.add(InlineKeyboardButton(text=t(locale, "buttons.my_tickets"), callback_data="menu_my_tickets"))
    builder.adjust(2)  # 2 buttons per row
    # Other buttons on separate rows
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


def get_events_keyboard(locale: str, events: list) -> InlineKeyboardMarkup:
    """Get events list keyboard."""
    builder = InlineKeyboardBuilder()
    for event in events:
        djs = event.get('djs', [])
        if djs:
            djs_text = ", ".join(djs)
            event_text = f"🎧 {djs_text}\n📅 {event.get('date', '')} {event.get('time', '')}"
        else:
            event_text = f"🎉 {event.get('name', 'Event')}\n📅 {event.get('date', '')} {event.get('time', '')}"
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
        available_text = f" ({available} {t(locale, 'labels.available')})" if available > 0 else ""
        price = ticket_type.get('price', 0)
        if isinstance(price, str):
            price = float(price)
        ticket_text = f"🎫 {ticket_type.get('name', 'Type')} - {price} ₽{available_text}"
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
        builder.add(InlineKeyboardButton(text=f"🔢 {i}", callback_data=f"quantity_{i}"))
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back"), callback_data="back_to_ticket_types"))
    return builder.as_markup()


def get_confirm_order_keyboard(locale: str) -> InlineKeyboardMarkup:
    """Get order confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.confirm"), callback_data="confirm_order"))
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
        ticket_text = f"{status_emoji} {ticket.get('event_djs', 'Event')}\n📅 {ticket.get('event_date', '')} {ticket.get('event_time', '')}"
        builder.add(InlineKeyboardButton(
            text=ticket_text,
            callback_data=f"ticket_{ticket.get('id')}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t(locale, "buttons.back_to_menu"), callback_data="back_to_menu"))
    return builder.as_markup()
