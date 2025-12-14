"""Ticket purchase flow handlers."""
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# TODO: Implement purchase flow handlers
router = Router()


@router.callback_query()
async def handle_purchase_callbacks(callback: CallbackQuery):
    """Placeholder for purchase callbacks."""
    await callback.answer("🚧 В разработке", show_alert=True)
