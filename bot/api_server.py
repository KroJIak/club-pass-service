"""Simple HTTP server for bot to receive messages from API."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from aiogram import Bot
from bot.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="Bot API Server")


class SendMessageRequest(BaseModel):
    """Request to send a message to a user."""
    telegram_user_id: int
    original_message: str
    admin_response: str


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
        
        # Format message with headers and quote
        formatted_message = (
            f"<b>Ваше обращение</b>\n\n"
            f"<blockquote>{request.original_message}</blockquote>\n\n"
            f"<b>Ответ администратора</b>\n\n"
            f"{request.admin_response}"
        )
        
        # Send support response
        await bot.send_message(
            chat_id=request.telegram_user_id,
            text=formatted_message,
            parse_mode="HTML",
        )
        
        # Send main menu after response
        from bot.core.keyboards import get_main_menu_keyboard
        from bot.core.message_manager import get_screen_image
        from bot.core.middleware import temporary_messages_middleware
        
        # Get user locale (default to ru_ru)
        # We don't have user's language code here, so use default
        locale = "ru_ru"  # Could be improved by storing user locale in DB
        
        # Get old system message to delete it
        old_system = temporary_messages_middleware.get_last_system_message(request.telegram_user_id)
        
        # Get main menu image
        photo_input = get_screen_image(locale, "main_menu")
        
        # Send main menu
        main_menu_message = await bot.send_photo(
            chat_id=request.telegram_user_id,
            photo=photo_input,
            caption=None,
            reply_markup=get_main_menu_keyboard(locale),
        )
        
        # Delete old system message if exists
        if old_system:
            old_chat_id, old_message_id = old_system
            if not (old_chat_id == main_menu_message.chat.id and old_message_id == main_menu_message.message_id):
                await temporary_messages_middleware.delete_system_message(bot, old_chat_id, old_message_id)
        
        # Update last system message for temporary messages middleware
        temporary_messages_middleware.set_last_system_message(
            request.telegram_user_id,
            main_menu_message.chat.id,
            main_menu_message.message_id
        )
        
        logger.info(f"Sent support response and main menu to user {request.telegram_user_id}")
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

