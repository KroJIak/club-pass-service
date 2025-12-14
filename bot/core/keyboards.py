"""Keyboard builders."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🎫 Купить билет"))
    builder.row(KeyboardButton(text="🎟️ Мои билеты"))
    builder.row(KeyboardButton(text="🎉 Ближайшие вечеринки"))
    builder.row(KeyboardButton(text="ℹ️ Инфо о клубе"), KeyboardButton(text="💬 Поддержка"))
    return builder.as_markup(resize_keyboard=True)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get back to menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu"))
    return builder.as_markup()


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
