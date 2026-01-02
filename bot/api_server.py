"""Simple HTTP server for bot to receive messages from API."""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import re
from aiogram import Bot
from aiogram.types import BufferedInputFile
from bot.core.config import settings

logger = logging.getLogger(__name__)


def escape_html(text: str) -> str:
    """Escape special characters for HTML."""
    # Escape HTML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

app = FastAPI(title="Bot API Server")


class SendMessageRequest(BaseModel):
    """Request to send a message to a user."""
    telegram_user_id: int
    original_message: str
    admin_response: str
    photo_file_ids: Optional[List[str]] = None
    photo_paths: Optional[List[str]] = None  # Paths to photo files on server


class SendDirectMessageRequest(BaseModel):
    """Request to send a direct message to a user."""
    telegram_user_id: int
    message: str
    photo_file_ids: Optional[List[str]] = None
    photo_paths: Optional[List[str]] = None  # Paths to photo files on server


@app.post("/send-support-response")
async def send_support_response(request: SendMessageRequest):
    """Send support response to user with quoted original message."""
    try:
        # Get bot instance from global context
        # We'll need to set this when bot starts
        bot = get_bot_instance()
        if not bot:
            raise HTTPException(
                status_code=503,
                detail="Bot instance not available"
            )
        
        # Format message with headers and collapsible quote using HTML
        # Escape text for HTML
        # If original message is empty or only whitespace, show "Фотография без описания"
        original_text = request.original_message.strip() if request.original_message else ""
        if not original_text:
            original_text = "Фотография без описания"
        
        escaped_original = escape_html(original_text)
        escaped_response = escape_html(request.admin_response)
        
        # Use <blockquote expandable> for collapsible blockquote in HTML
        formatted_message = (
            f"<b>Ваше обращение</b>\n"
            f"<blockquote expandable>{escaped_original}</blockquote>\n\n"
            f"<b>Ответ администратора</b>\n"
            f"<blockquote>{escaped_response}</blockquote>"
        )
        
        # Create inline keyboard with "Write again" button
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from bot.core.i18n import DEFAULT_LOCALE, t
        
        # Use default locale for button text (user's locale is not available here)
        locale = DEFAULT_LOCALE
        
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.add(InlineKeyboardButton(
            text=t(locale, "buttons.write_again"),
            callback_data="support_new_message"
        ))
        reply_markup = keyboard_builder.as_markup()
        
        # Send support response with photos if any
        if request.photo_file_ids:
            # Send photos first using file_ids
            from aiogram.types import InputMediaPhoto
            media_group = []
            for file_id in request.photo_file_ids:
                media_group.append(InputMediaPhoto(media=file_id))
            
            # Send media group
            await bot.send_media_group(
                chat_id=request.telegram_user_id,
                media=media_group,
            )
        elif request.photo_paths:
            # Send photos using file paths
            from aiogram.types import FSInputFile, InputMediaPhoto
            import os
            media_group = []
            for photo_path in request.photo_paths:
                full_path = os.path.join(os.getcwd(), photo_path)
                if os.path.exists(full_path):
                    photo_file = FSInputFile(full_path)
                    media_group.append(InputMediaPhoto(media=photo_file))
            
            if media_group:
                # Send media group
                await bot.send_media_group(
                    chat_id=request.telegram_user_id,
                    media=media_group,
                )
        
        # Send text message
        await bot.send_message(
            chat_id=request.telegram_user_id,
            text=formatted_message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
        
        # Mark last system message (menu) as temporary
        # This will cause it to be deleted when user sends /start or clicks inline button
        from bot.core.middleware import temporary_messages_middleware
        
        old_system = temporary_messages_middleware.get_last_system_message(request.telegram_user_id)
        if old_system:
            old_chat_id, old_message_id = old_system
            # Add the old menu message to pending_user_messages so it gets deleted
            # when user interacts (sends /start or clicks button)
            temporary_messages_middleware.pending_user_messages[request.telegram_user_id].append(
                (old_chat_id, old_message_id)
            )
            # Clear last system message tracking so it's no longer considered "system"
            temporary_messages_middleware.clear_last_system_message(request.telegram_user_id)
            temporary_messages_middleware._persist_state()
            logger.info(
                f"Marked last system message as temporary for user {request.telegram_user_id}: "
                f"chat_id={old_chat_id} message_id={old_message_id}"
            )
        
        logger.info(f"Sent support response to user {request.telegram_user_id}")
        return {"status": "success", "message": "Response sent successfully"}
        
    except Exception as e:
        logger.error(f"Failed to send support response to user {request.telegram_user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message: {str(e)}"
        )


# Global bot instance
_bot_instance: Optional[Bot] = None


def set_bot_instance(bot: Bot):
    """Set the global bot instance."""
    global _bot_instance
    _bot_instance = bot


def get_bot_instance() -> Optional[Bot]:
    """Get the global bot instance."""
    return _bot_instance




@app.post("/send-direct-message")
async def send_direct_message(request: SendDirectMessageRequest):
    """Send a direct message to a user (admin to user)."""
    try:
        bot = get_bot_instance()
        if not bot:
            raise HTTPException(
                status_code=503,
                detail="Bot instance not available"
            )
        
        # Format message with header and blockquote using HTML
        escaped_message = escape_html(request.message)
        formatted_message = (
            f"<b>Сообщение от администратора</b>\n"
            f"<blockquote>{escaped_message}</blockquote>"
        )
        
        # Create inline keyboard with "Write to support" button
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from bot.core.i18n import DEFAULT_LOCALE, t
        
        # Use default locale for button text (user's locale is not available here)
        locale = DEFAULT_LOCALE
        
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.add(InlineKeyboardButton(
            text=t(locale, "buttons.write_to_support"),
            callback_data="support_new_message"
        ))
        reply_markup = keyboard_builder.as_markup()
        
        # Send direct message with photos if any
        if request.photo_file_ids:
            # Send photos first using file_ids
            from aiogram.types import InputMediaPhoto
            media_group = []
            for file_id in request.photo_file_ids:
                media_group.append(InputMediaPhoto(media=file_id))
            
            # Send media group
            await bot.send_media_group(
                chat_id=request.telegram_user_id,
                media=media_group,
            )
        elif request.photo_paths:
            # Send photos using file paths
            from aiogram.types import FSInputFile, InputMediaPhoto
            import os
            media_group = []
            for photo_path in request.photo_paths:
                full_path = os.path.join(os.getcwd(), photo_path)
                if os.path.exists(full_path):
                    photo_file = FSInputFile(full_path)
                    media_group.append(InputMediaPhoto(media=photo_file))
            
            if media_group:
                # Send media group
                await bot.send_media_group(
                    chat_id=request.telegram_user_id,
                    media=media_group,
                )
        
        # Send text message
        await bot.send_message(
            chat_id=request.telegram_user_id,
            text=formatted_message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
        
        # Mark last system message (menu) as temporary
        from bot.core.middleware import temporary_messages_middleware
        
        old_system = temporary_messages_middleware.get_last_system_message(request.telegram_user_id)
        if old_system:
            old_chat_id, old_message_id = old_system
            temporary_messages_middleware.pending_user_messages[request.telegram_user_id].append(
                (old_chat_id, old_message_id)
            )
            temporary_messages_middleware.clear_last_system_message(request.telegram_user_id)
            temporary_messages_middleware._persist_state()
            logger.info(
                f"Marked last system message as temporary for user {request.telegram_user_id}: "
                f"chat_id={old_chat_id} message_id={old_message_id}"
            )
        
        logger.info(f"Sent direct message to user {request.telegram_user_id}")
        return {"status": "success", "message": "Message sent successfully"}
        
    except Exception as e:
        logger.error(f"Failed to send direct message to user {request.telegram_user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message: {str(e)}"
        )

