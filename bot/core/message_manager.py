"""Message formatting and management."""

from __future__ import annotations

from typing import Any, Dict, Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.core.middleware import temporary_messages_middleware


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
    user_id = callback.from_user.id
    bot = callback.bot
    chat_id = callback.message.chat.id
    
    try:
        # Try to edit message
        if callback.message.photo:
            # If message has photo, try to edit caption
            await callback.message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            temporary_messages_middleware.set_last_system_message(user_id, chat_id, callback.message.message_id)
        else:
            # Regular text message
            await callback.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            temporary_messages_middleware.set_last_system_message(user_id, chat_id, callback.message.message_id)

        # After bot system action -> delete ALL pending user messages
        await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
        return True
    except TelegramBadRequest as e:
        error_msg = str(e).lower()
        
        # If message is not modified, just leave it as is
        if "message is not modified" in error_msg:
            # Still a system action attempt -> flush pending user messages
            await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
            return True
        
        # If editing fails for other reasons (e.g., different content type),
        # delete old message and send new one
        old_message_id = callback.message.message_id
        try:
            await callback.message.delete()
        except:
            pass
        
        # Send new message
        new_message = await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        
        temporary_messages_middleware.set_last_system_message(user_id, new_message.chat.id, new_message.message_id)

        # After bot system action -> delete ALL pending user messages
        await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
        
        # Delete old system message if it was different
        if old_message_id != new_message.message_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=old_message_id)
            except:
                pass
        
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
        bot = message_or_callback.bot
        user_id = message_or_callback.from_user.id

        # It's a Message, send new system message
        new_message = await message_or_callback.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        temporary_messages_middleware.set_last_system_message(user_id, new_message.chat.id, new_message.message_id)

        # After bot system action -> delete ALL pending user messages
        await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
        return False


async def edit_last_system_message_or_send(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
) -> None:
    """
    Edit the last remembered system message for this user, if possible.
    Otherwise send a new system message.

    Used for Message-handlers (where we don't have CallbackQuery.message to edit).
    """
    bot = message.bot
    user_id = message.from_user.id

    ref = temporary_messages_middleware.get_last_system_message(user_id)
    if not ref:
        await safe_edit_or_send(message, text, reply_markup=reply_markup, parse_mode=parse_mode)
        return

    chat_id, message_id = ref

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        temporary_messages_middleware.set_last_system_message(user_id, chat_id, message_id)
        await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
        return
    except TelegramBadRequest as e:
        msg = str(e).lower()
        if "message is not modified" in msg:
            await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
            return
        # If there is no text to edit (e.g. photo message), try caption
        if "there is no text in the message to edit" in msg:
            try:
                await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
                temporary_messages_middleware.set_last_system_message(user_id, chat_id, message_id)
                await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
                return
            except TelegramBadRequest:
                pass

    # Fallback: send new and delete old
    new_msg = await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    temporary_messages_middleware.set_last_system_message(user_id, new_msg.chat.id, new_msg.message_id)
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
    await temporary_messages_middleware.delete_system_message(bot, chat_id, message_id)


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
