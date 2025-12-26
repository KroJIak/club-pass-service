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
        
        await bot.send_message(
            chat_id=request.telegram_user_id,
            text=formatted_message,
            parse_mode="HTML",
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

