"""Ticket purchase flow handlers."""
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.i18n import get_user_locale, t

# TODO: Implement purchase flow handlers
router = Router()


@router.callback_query()
async def handle_purchase_callbacks(callback: CallbackQuery):
    """Placeholder for purchase callbacks."""
    locale = get_user_locale(callback.from_user.language_code)
    await callback.answer(t(locale, "messages.in_development"), show_alert=True)
