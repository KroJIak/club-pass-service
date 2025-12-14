"""Middleware/state for tracking user temporary messages and last system message."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject

from bot.core.states import SupportStates

ChatId = int
MessageId = int
SystemMsgRef = Tuple[ChatId, MessageId]
UserMsgRef = Tuple[ChatId, MessageId]


class TemporaryMessagesMiddleware(BaseMiddleware):
    """
    Tracks ALL user messages as "temporary" (pending for deletion),
    except support feedback messages (SupportStates.waiting_message).

    Deletion is triggered by the bot when it performs a "system action"
    (send/edit system message). This is done via `flush_pending_user_messages(...)`.
    """

    def __init__(self) -> None:
        # Pending user messages per user_id: list of (chat_id, message_id)
        self.pending_user_messages: Dict[int, list[UserMsgRef]] = defaultdict(list)

        # Last system message per user_id: (chat_id, message_id)
        self.last_system_message: Dict[int, SystemMsgRef] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        chat_id = event.chat.id

        state: FSMContext | None = data.get("state")
        is_support_feedback = False
        if state:
            current_state = await state.get_state()
            if current_state == SupportStates.waiting_message.state:
                is_support_feedback = True

        # ВСЕ сообщения пользователя временные, кроме feedback в поддержку
        if not is_support_feedback:
            self.pending_user_messages[user_id].append((chat_id, event.message_id))

        return await handler(event, data)

    # ----- system message tracking -----
    def set_last_system_message(self, user_id: int, chat_id: int, message_id: int) -> None:
        self.last_system_message[user_id] = (chat_id, message_id)

    def get_last_system_message(self, user_id: int) -> Optional[SystemMsgRef]:
        return self.last_system_message.get(user_id)

    async def delete_system_message(self, bot, chat_id: int, message_id: int) -> bool:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            return True
        except Exception:
            return False

    async def delete_last_system_message(self, user_id: int, bot) -> bool:
        ref = self.get_last_system_message(user_id)
        if not ref:
            return False
        chat_id, message_id = ref
        deleted = await self.delete_system_message(bot, chat_id, message_id)
        if deleted:
            self.last_system_message.pop(user_id, None)
        return deleted

    # ----- pending user messages deletion -----
    async def flush_pending_user_messages(self, bot, user_id: int) -> None:
        """
        Try deleting all pending temporary user messages for this user.
        Called after bot sends/edits a system message.
        """
        pending = self.pending_user_messages.get(user_id, [])
        if not pending:
            return

        # Clear early to avoid re-entrancy loops; if deletion fails we don't retry endlessly.
        self.pending_user_messages[user_id] = []

        for chat_id, message_id in pending:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                # If Telegram doesn't allow deletion, ignore (best-effort).
                pass


# Global instance used across handlers/helpers
temporary_messages_middleware = TemporaryMessagesMiddleware()
