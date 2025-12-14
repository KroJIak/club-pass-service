"""Middleware/state for tracking user temporary messages and last system message."""

from __future__ import annotations

import json
import logging
import os
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

logger = logging.getLogger("bot.temp_messages")


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

        # Local persistence (so we don't lose pending msgs on restart)
        self._state_file = os.path.join(os.path.dirname(__file__), "..", ".runtime", "state.json")
        self._load_state()

    def _ensure_runtime_dir(self) -> None:
        runtime_dir = os.path.dirname(os.path.abspath(self._state_file))
        os.makedirs(runtime_dir, exist_ok=True)

    def _load_state(self) -> None:
        try:
            if not os.path.exists(self._state_file):
                return
            with open(self._state_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            pending = raw.get("pending_user_messages", {})
            last = raw.get("last_system_message", {})

            self.pending_user_messages = defaultdict(
                list,
                {int(k): [tuple(vv) for vv in v] for k, v in pending.items()},
            )
            self.last_system_message = {int(k): tuple(v) for k, v in last.items()}
        except Exception:
            # Best-effort; if state is corrupt, ignore.
            self.pending_user_messages = defaultdict(list)
            self.last_system_message = {}

    def _persist_state(self) -> None:
        try:
            self._ensure_runtime_dir()
            data = {
                "pending_user_messages": {str(k): v for k, v in self.pending_user_messages.items()},
                "last_system_message": {str(k): list(v) for k, v in self.last_system_message.items()},
            }
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            # Best-effort persistence.
            pass

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

        # Log every incoming user message (for debugging message deletion)
        try:
            username = event.from_user.username
            text = event.text or event.caption or ""
            content_type = "photo" if event.photo else "text"
            logger.info(
                "incoming user message: user_id=%s chat_id=%s message_id=%s username=%s type=%s text=%r support_feedback=%s",
                user_id,
                chat_id,
                event.message_id,
                username,
                content_type,
                text,
                is_support_feedback,
            )
        except Exception:
            pass

        # ВСЕ сообщения пользователя временные, кроме feedback в поддержку
        if not is_support_feedback:
            self.pending_user_messages[user_id].append((chat_id, event.message_id))
            self._persist_state()
            try:
                logger.debug(
                    "queued pending user message: user_id=%s pending_count=%s",
                    user_id,
                    len(self.pending_user_messages[user_id]),
                )
            except Exception:
                pass

        return await handler(event, data)

    # ----- system message tracking -----
    def set_last_system_message(self, user_id: int, chat_id: int, message_id: int) -> None:
        self.last_system_message[user_id] = (chat_id, message_id)
        self._persist_state()

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
            self._persist_state()
        return deleted

    # ----- pending user messages deletion -----
    async def flush_pending_user_messages(self, bot, user_id: int) -> None:
        """
        Try deleting all pending temporary user messages for this user.
        Called after bot sends/edits a system message.
        """
        pending = self.pending_user_messages.get(user_id, [])
        if not pending:
            try:
                logger.debug("flush pending: user_id=%s pending_count=0", user_id)
            except Exception:
                pass
            return

        try:
            logger.info("flush pending: user_id=%s pending_count=%s", user_id, len(pending))
        except Exception:
            pass

        # Clear early to avoid re-entrancy loops; if deletion fails we don't retry endlessly.
        self.pending_user_messages[user_id] = []
        self._persist_state()

        deleted = 0
        failed = 0
        for chat_id, message_id in pending:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
                deleted += 1
            except Exception:
                # If Telegram doesn't allow deletion, ignore (best-effort).
                failed += 1
                try:
                    logger.warning(
                        "failed to delete user message: user_id=%s chat_id=%s message_id=%s",
                        user_id,
                        chat_id,
                        message_id,
                    )
                except Exception:
                    pass

        try:
            logger.info("flush pending done: user_id=%s deleted=%s failed=%s", user_id, deleted, failed)
        except Exception:
            pass


# Global instance used across handlers/helpers
temporary_messages_middleware = TemporaryMessagesMiddleware()
