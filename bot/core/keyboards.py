"""Keyboard builders - only inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎫 Купить билет", callback_data="menu_buy_ticket"))
    builder.row(InlineKeyboardButton(text="🎟️ Мои билеты", callback_data="menu_my_tickets"))
    builder.row(InlineKeyboardButton(text="🎉 Ближайшие вечеринки", callback_data="menu_events"))
    builder.row(InlineKeyboardButton(text="ℹ️ Инфо о клубе", callback_data="menu_club_info"))
    builder.row(InlineKeyboardButton(text="💬 Поддержка", callback_data="menu_support"))
    return builder.as_markup()


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get 'back to main menu' button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu"))
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Generic back button for screens (goes to main menu)."""
    return get_back_to_menu_keyboard()


def get_events_keyboard(events: list) -> InlineKeyboardMarkup:
    """Get events list keyboard."""
    builder = InlineKeyboardBuilder()
    for event in events:
        builder.add(InlineKeyboardButton(
            text=f"{event.get('name', 'Событие')} - {event.get('date', '')}",
            callback_data=f"event_{event.get('id')}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))
    return builder.as_markup()


def get_ticket_types_keyboard(ticket_types: list) -> InlineKeyboardMarkup:
    """Get ticket types keyboard."""
    builder = InlineKeyboardBuilder()
    for ticket_type in ticket_types:
        builder.add(InlineKeyboardButton(
            text=f"{ticket_type.get('name', 'Тип')} - {ticket_type.get('price', 0)} ₽",
            callback_data=f"ticket_type_{ticket_type.get('id')}"
        ))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_events"))
    return builder.as_markup()


def get_quantity_keyboard(max_quantity: int = 5) -> InlineKeyboardMarkup:
    """Get quantity selection keyboard."""
    builder = InlineKeyboardBuilder()
    for i in range(1, min(max_quantity + 1, 6)):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"quantity_{i}"))
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_ticket_types"))
    return builder.as_markup()


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Get order confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order"))
    builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order"))
    return builder.as_markup()


def get_support_cancel_keyboard() -> InlineKeyboardMarkup:
    """Support screen keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_support"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))
    return builder.as_markup()
