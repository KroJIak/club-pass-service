"""Message formatting and management."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, Message, InputMediaPhoto

from bot.core.middleware import temporary_messages_middleware
from bot.core.i18n import t
from bot.core.assets import get_locale_image_path

logger = logging.getLogger(__name__)


def _get_screen_image_path(locale: str, screen_key: str) -> str:
    """Get image path for a screen from lang file: screens.{screen_key}.image"""
    filename = t(locale, f"screens.{screen_key}.image")
    return get_locale_image_path(locale, filename)


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
    photo_path: Optional[str] = None,
) -> Optional[Message]:
    """
    Edit callback message. Returns new Message if photo was sent, None if edited in place.
    If photo_path is provided and message already has photo, will replace the photo.
    """
    if callback.message.photo:
        # Message already has photo
        if photo_path:
            # Need to change photo - use edit_message_media to replace photo without deleting
            photo = FSInputFile(photo_path)
            media = InputMediaPhoto(media=photo, caption=text if text else None, parse_mode=parse_mode)
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
    elif photo_path:
        # Message doesn't have photo, but we need to add one - delete old and send new
        await callback.message.delete()
        photo = FSInputFile(photo_path)
        return await callback.message.answer_photo(
            photo=photo,
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
    photo_path: Optional[str] = None,
) -> Message:
    try:
        await callback.message.delete()
    except Exception:
        pass
    if photo_path:
        photo = FSInputFile(photo_path)
        return await callback.message.answer_photo(
            photo=photo,
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
) -> bool:
    """
    Safely edit message. If editing fails (e.g., different content types),
    delete old message and send new one.
    
    If locale and screen_key are provided, will attach appropriate image.
    
    Returns True if message was edited, False if new message was sent.
    """
    user_id = callback.from_user.id
    bot = callback.bot
    chat_id = callback.message.chat.id
    
    photo_path = None
    if locale and screen_key:
        photo_path = _get_screen_image_path(locale, screen_key)
    
    try:
        new_message = await _edit_callback_message(callback, text, reply_markup, parse_mode, photo_path)
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
        
        # If editing fails for other reasons (e.g., different content type),
        # delete old message and send new one
        old_message_id = callback.message.message_id
        new_message = await _delete_and_send_new_from_callback(callback, text, reply_markup, parse_mode, photo_path)

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
        photo_path = None
        if locale and screen_key:
            photo_path = _get_screen_image_path(locale, screen_key)
        
        if photo_path:
            photo = FSInputFile(photo_path)
            new_message = await message_or_callback.answer_photo(
                photo=photo,
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


def format_event_message(locale: str, event: Dict[str, Any]) -> str:
    """Format event information message."""
    return (
        f"🎉 <b>{event.get('name', t(locale, 'buttons.events'))}</b>\n\n"
        f"📅 {event.get('date', '')}\n"
        f"🕐 {event.get('time', '')}\n"
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
    return (
        f"📋 <b>{t(locale, 'buttons.confirm')}</b>\n\n"
        f"🎉 {order.get('event_name', '')}\n"
        f"🎟️ {order.get('ticket_type_name', '')}\n"
        f"🔢 {order.get('quantity', 0)}\n"
        f"💰 {order.get('total_amount', 0)} ₽"
    )
