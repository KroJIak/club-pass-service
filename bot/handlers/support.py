"""Support handlers."""
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
import logging
from typing import Optional

from bot.services.api_service import api_service

router = Router()
logger = logging.getLogger(__name__)


async def send_support_response_to_user(
    bot: Bot,
    telegram_user_id: int,
    original_message: str,
    admin_response: str,
) -> bool:
    """
    Send admin response to user with quoted original message.
    This message is NOT temporary - it persists in chat history.
    """
    try:
        # Format message with quote
        # Using HTML formatting with blockquote
        formatted_message = (
            f"<blockquote>{original_message}</blockquote>\n\n"
            f"{admin_response}"
        )
        
        await bot.send_message(
            chat_id=telegram_user_id,
            text=formatted_message,
            parse_mode="HTML",
        )
        
        logger.info(f"Sent support response to user {telegram_user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send support response to user {telegram_user_id}: {e}")
        return False


# This function will be called by the API when admin responds
# We'll need to set up a webhook or polling mechanism
async def process_support_response(message_id: int, admin_response: str) -> bool:
    """
    Process a support response - fetch message details and send to user.
    This is called from API endpoint or scheduled task.
    """
    try:
        # Get message details from API
        # For now, we'll need to implement this via API call or direct DB access
        # The API endpoint should call this function after updating the message
        
        # This is a placeholder - actual implementation depends on architecture
        # Option 1: API calls bot service via HTTP
        # Option 2: Bot polls API for new responses
        # Option 3: Shared message queue (Redis, etc.)
        
        logger.info(f"Processing support response for message_id={message_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to process support response: {e}")
        return False
