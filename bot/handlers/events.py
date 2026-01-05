"""Events list handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.core.i18n import get_user_locale, t

# TODO: Implement events list handlers
router = Router()


@router.callback_query(F.data.startswith("event_"))
async def handle_event_callbacks(callback: CallbackQuery):
    """Placeholder for event callbacks."""
    locale = get_user_locale(callback.from_user.language_code)
    await callback.answer(t(locale, "messages.in_development"), show_alert=True)
