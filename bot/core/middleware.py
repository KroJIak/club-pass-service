"""Middleware for bot."""
from typing import Any, Awaitable, Callable, Dict, Optional
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.fsm.context import FSMContext

from bot.core.states import SupportStates


class TemporaryMessagesMiddleware(BaseMiddleware):
    """Middleware to track and delete temporary user messages."""
    
    def __init__(self):
        # Store temporary messages per user
        # Format: {user_id: [list of messages]}
        self.temporary_messages: Dict[int, list] = defaultdict(list)
        
        # Store last system message ID per user
        # Format: {user_id: message_id}
        self.last_system_message: Dict[int, int] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Process update and track temporary messages."""
        # Only process Message from users
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)
        
        message = event
        user_id = message.from_user.id
        
        # Get FSM context to check if user is in support state
        state: FSMContext = data.get("state")
        is_support_message = False
        
        if state:
            current_state = await state.get_state()
            # If user is sending feedback to support, don't mark as temporary
            if current_state == SupportStates.waiting_message:
                is_support_message = True
        
        # Mark message as temporary (unless it's support feedback)
        if not is_support_message:
            self.temporary_messages[user_id].append(message)
        
        # Call handler
        result = await handler(event, data)
        
        # After handler processed, delete temporary messages for this user
        if not is_support_message and user_id in self.temporary_messages:
            messages_to_delete = self.temporary_messages[user_id]
            self.temporary_messages[user_id] = []  # Clear list
            
            # Delete all temporary messages
            for msg in messages_to_delete:
                try:
                    await msg.delete()
                except Exception:
                    # Ignore errors (message might be already deleted)
                    pass
        
        return result
    
    def set_last_system_message(self, user_id: int, message_id: int):
        """Set last system message ID for user."""
        self.last_system_message[user_id] = message_id
    
    def get_last_system_message_id(self, user_id: int) -> Optional[int]:
        """Get last system message ID for user."""
        return self.last_system_message.get(user_id)
    
    async def delete_last_system_message(self, user_id: int, bot) -> bool:
        """Delete last system message for user. Returns True if deleted."""
        message_id = self.get_last_system_message_id(user_id)
        if message_id:
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
                del self.last_system_message[user_id]
                return True
            except Exception:
                return False
        return False


# Global instance
temporary_messages_middleware = TemporaryMessagesMiddleware()
