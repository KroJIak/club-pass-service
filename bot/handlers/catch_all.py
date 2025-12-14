"""Catch-all handlers.

We intentionally do NOT respond here.
This router exists so that every user message is considered "handled",
which makes our message middleware run and queue the message for deletion
after the next system action (send/edit).
"""

from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def catch_all_message(_: Message) -> None:
    """Do nothing."""
    return


