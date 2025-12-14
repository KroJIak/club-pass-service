"""Events list handlers."""
from aiogram import Router
from aiogram.types import CallbackQuery

# TODO: Implement events list handlers
router = Router()


@router.callback_query()
async def handle_event_callbacks(callback: CallbackQuery):
    """Placeholder for event callbacks."""
    await callback.answer("🚧 В разработке", show_alert=True)
