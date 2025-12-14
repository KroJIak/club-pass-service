"""Message formatting and management."""
from typing import Dict, Any, Optional
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML"
) -> bool:
    """
    Safely edit message. If editing fails (e.g., different content types),
    delete old message and send new one.
    
    Returns True if message was edited, False if new message was sent.
    """
    try:
        # Try to edit text message
        if callback.message.photo:
            # If message has photo, try to edit caption
            await callback.message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            # Regular text message
            await callback.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        return True
    except TelegramBadRequest as e:
        # If editing fails (e.g., "message is not modified" or different content type),
        # delete old message and send new one
        if "message is not modified" not in str(e).lower():
            try:
                await callback.message.delete()
            except:
                pass
        
        # Send new message
        await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return False


async def safe_edit_or_send(
    message_or_callback: Message | CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML"
) -> bool:
    """
    Edit message if callback, or send new if message.
    Returns True if edited, False if sent new.
    """
    if isinstance(message_or_callback, CallbackQuery):
        return await safe_edit_message(
            message_or_callback,
            text,
            reply_markup,
            parse_mode
        )
    else:
        # It's a Message, send new one
        await message_or_callback.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return False


def format_event_message(event: Dict[str, Any]) -> str:
    """Format event information message."""
    return (
        f"🎉 <b>{event.get('name', 'Событие')}</b>\n\n"
        f"📅 Дата: {event.get('date', 'Не указано')}\n"
        f"🕐 Время: {event.get('time', 'Не указано')}\n"
        f"📍 Место: {event.get('location', 'Не указано')}\n\n"
        f"{event.get('description', '')}"
    )


def format_ticket_info(ticket: Dict[str, Any]) -> str:
    """Format ticket information message."""
    return (
        f"🎫 <b>Билет #{ticket.get('id', 'N/A')}</b>\n\n"
        f"🎉 Событие: {ticket.get('event_name', 'Не указано')}\n"
        f"📅 Дата: {ticket.get('date', 'Не указано')}\n"
        f"🎟️ Тип: {ticket.get('ticket_type', 'Не указано')}\n"
        f"🔑 Код: <code>{ticket.get('code', 'N/A')}</code>"
    )


def format_order_summary(order: Dict[str, Any]) -> str:
    """Format order summary message."""
    return (
        f"📋 <b>Подтверждение заказа</b>\n\n"
        f"🎉 Событие: {order.get('event_name', 'Не указано')}\n"
        f"🎟️ Тип билета: {order.get('ticket_type_name', 'Не указано')}\n"
        f"🔢 Количество: {order.get('quantity', 0)}\n"
        f"💰 Сумма: {order.get('total_amount', 0)} ₽"
    )
