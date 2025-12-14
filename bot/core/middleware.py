"""Middleware for bot."""
from typing import Any, Awaitable, Callable, Dict
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
