"""My tickets handlers."""
from aiogram import Router
from aiogram.types import CallbackQuery

# TODO: Implement tickets view handlers
router = Router()


@router.callback_query()
async def handle_ticket_callbacks(callback: CallbackQuery):
    """Placeholder for ticket callbacks."""
    await callback.answer("🚧 В разработке", show_alert=True)
