"""Message formatting and management."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, CallbackQuery, FSInputFile, InlineKeyboardMarkup, Message, InputMediaPhoto

from bot.core.middleware import temporary_messages_middleware
from bot.core.i18n import t
from bot.core.assets import get_locale_image_path
from bot.core.image_cache import get_cached_image

logger = logging.getLogger(__name__)


def get_screen_image(locale: str, screen_key: str) -> BufferedInputFile | FSInputFile:
    """
    Get image for a screen - uses cache if available, otherwise falls back to file path.
    Returns BufferedInputFile (from cache) or FSInputFile (from disk).
    """
    filename = t(locale, f"screens.{screen_key}.image")
    
    # Try to get from cache first
    cached = get_cached_image(locale, filename)
    if cached:
        return BufferedInputFile(cached.read(), filename=filename)
    
    # Fallback to file path if not in cache
    filepath = get_locale_image_path(locale, filename)
    return FSInputFile(filepath)


async def remove_inline_keyboard(bot, chat_id: int, message_id: int) -> bool:
    """
    Best-effort removal of inline keyboard from an existing message.

    Returns True if edit call succeeded, False otherwise.
    """
    try:
        try:
            empty_keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=empty_keyboard,
            )
        except Exception:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=None,
            )
        return True
    except Exception as e:
        logger.warning(
            "failed to remove inline keyboard: chat_id=%s message_id=%s error=%s",
            chat_id,
            message_id,
            str(e),
        )
        return False


async def _after_system_action(bot, user_id: int, chat_id: int, message_id: int) -> None:
    temporary_messages_middleware.set_last_system_message(user_id, chat_id, message_id)
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)


async def _edit_callback_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup],
    parse_mode: Optional[str],
    photo_input: Optional[BufferedInputFile | FSInputFile] = None,
) -> Optional[Message]:
    """
    Edit callback message. Returns new Message if photo was sent, None if edited in place.
    If photo_path is provided and message already has photo, will replace the photo.
    """
    if callback.message.photo:
        # Message already has photo
        if photo_input:
            # Need to change photo - use edit_message_media to replace photo without deleting
            media = InputMediaPhoto(media=photo_input, caption=text if text else None, parse_mode=parse_mode)
            await callback.bot.edit_message_media(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                media=media,
                reply_markup=reply_markup,
            )
            return None
        else:
            # Just edit caption
            await callback.message.edit_caption(
                caption=text if text else None,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            return None
    elif photo_input:
        # Message doesn't have photo, but we need to add one - delete old and send new
        await callback.message.delete()
        return await callback.message.answer_photo(
            photo=photo_input,
            caption=text if text else None,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    else:
        # Regular text message
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        return None


async def _delete_and_send_new_from_callback(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup],
    parse_mode: Optional[str],
    photo_input: Optional[BufferedInputFile | FSInputFile] = None,
) -> Message:
    try:
        await callback.message.delete()
    except Exception:
        pass
    if photo_input:
        return await callback.message.answer_photo(
            photo=photo_input,
            caption=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    return await callback.message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
    locale: Optional[str] = None,
    screen_key: Optional[str] = None,
    photo_input: Optional[BufferedInputFile | FSInputFile] = None,
) -> bool:
    """
    Safely edit message. If editing fails (e.g., different content types),
    delete old message and send new one.
    
    If locale and screen_key are provided, will attach appropriate image.
    If photo_input is provided, it will be used instead of screen_key image.
    
    Returns True if message was edited, False if new message was sent.
    """
    user_id = callback.from_user.id
    bot = callback.bot
    chat_id = callback.message.chat.id
    
    if photo_input is None:
        if locale and screen_key:
            photo_input = get_screen_image(locale, screen_key)
    
    try:
        new_message = await _edit_callback_message(callback, text, reply_markup, parse_mode, photo_input)
        # If photo was sent, new_message contains the new message, otherwise use original
        if new_message:
            await _after_system_action(bot, user_id, new_message.chat.id, new_message.message_id)
        else:
            await _after_system_action(bot, user_id, chat_id, callback.message.message_id)
        return True
    except TelegramBadRequest as e:
        error_msg = str(e).lower()
        
        # If message is not modified, just leave it as is
        if "message is not modified" in error_msg:
            # Still a system action attempt -> flush pending user messages
            await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
            return True
        
        # If message was deleted (not found), send new message
        if "message to edit not found" in error_msg or "message not found" in error_msg:
            # Message was already deleted, send new one
            old_message_id = callback.message.message_id
            new_message = await _delete_and_send_new_from_callback(callback, text, reply_markup, parse_mode, photo_input)
            await _after_system_action(bot, user_id, new_message.chat.id, new_message.message_id)
            return False
        
        # If editing fails for other reasons (e.g., different content type),
        # delete old message and send new one
        old_message_id = callback.message.message_id
        new_message = await _delete_and_send_new_from_callback(callback, text, reply_markup, parse_mode, photo_input)

        await _after_system_action(bot, user_id, new_message.chat.id, new_message.message_id)

        # Delete old system message if it was different
        if old_message_id != new_message.message_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=old_message_id)
            except Exception:
                pass

        return False


async def safe_edit_or_send(
    message_or_callback: Message | CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = "HTML",
    locale: Optional[str] = None,
    screen_key: Optional[str] = None,
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
            parse_mode,
            locale,
            screen_key,
        )
    else:
        bot = message_or_callback.bot
        user_id = message_or_callback.from_user.id

        # It's a Message, send new system message with photo if needed
        photo_input = None
        if locale and screen_key:
            photo_input = _get_screen_image(locale, screen_key)
        
        if photo_input:
            new_message = await message_or_callback.answer_photo(
                photo=photo_input,
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        else:
            new_message = await message_or_callback.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
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


def format_date_without_year(date_str: str) -> str:
    """Format date from DD.MM.YYYY to DD.MM."""
    if not date_str:
        return date_str
    # Split by dot and take first two parts (DD and MM)
    parts = date_str.split('.')
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return date_str


def format_event_message(locale: str, event: Dict[str, Any]) -> str:
    """Format event information message."""
    # Format event date/time range - keep full format with end date/time in messages
    start_date = event.get('start_date', '')
    start_time = event.get('start_time', '')
    end_date = event.get('end_date', '')
    end_time = event.get('end_time', '')
    
    # Format dates without year for display
    start_date_short = format_date_without_year(start_date)
    end_date_short = format_date_without_year(end_date) if end_date else ''
    
    # Format as "DD.MM HH:MM - DD.MM HH:MM" or just start if end is missing
    if end_date and end_time:
        event_datetime = f"{start_date_short} {start_time} - {end_date_short} {end_time}"
    else:
        event_datetime = f"{start_date_short} {start_time}"
    
    return (
        f"🎉 <b>{event.get('name', t(locale, 'buttons.events'))}</b>\n\n"
        f"📅 {event_datetime}\n"
        f"📍 {event.get('location', '')}\n\n"
        f"{event.get('description', '')}"
    )


def format_ticket_info(locale: str, ticket: Dict[str, Any]) -> str:
    """Format ticket information message."""
    return (
        f"🎫 <b>{t(locale, 'buttons.my_tickets')} #{ticket.get('id', 'N/A')}</b>\n\n"
        f"🎉 {ticket.get('event_name', '')}\n"
        f"📅 {ticket.get('date', '')}\n"
        f"🎟️ {ticket.get('ticket_type', '')}\n"
        f"🔑 <code>{ticket.get('code', 'N/A')}</code>"
    )


def format_order_summary(locale: str, order: Dict[str, Any]) -> str:
    """Format order summary message."""
    total_amount = order.get('total_amount', 0)
    if isinstance(total_amount, (int, float)):
        total_amount_formatted = int(total_amount) if isinstance(total_amount, float) and total_amount.is_integer() else total_amount
    else:
        total_amount_formatted = total_amount
    return (
        f"📋 <b>{t(locale, 'buttons.confirm')}</b>\n\n"
        f"🎉 {order.get('event_name', '')}\n"
        f"🎟️ {order.get('ticket_type_name', '')}\n"
        f"🔢 {order.get('quantity', 0)}\n"
        f"💰 {total_amount_formatted} ₽"
    )
