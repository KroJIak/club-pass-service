"""My tickets handlers."""
from aiogram import Router
from aiogram.types import CallbackQuery

from bot.core.i18n import get_user_locale, t

# TODO: Implement tickets view handlers
router = Router()


@router.callback_query()
async def handle_ticket_callbacks(callback: CallbackQuery):
    """Placeholder for ticket callbacks."""
    locale = get_user_locale(callback.from_user.language_code)
    await callback.answer(t(locale, "messages.in_development"), show_alert=True)
