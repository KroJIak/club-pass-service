"""Start command handler for staff bot."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from core.keyboards import get_mini_app_keyboard
from core.config import settings
from services.api_service import api_service

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - check access and show mini app button."""
    # Clear any previous state
    await state.clear()
    
    user_id = message.from_user.id
    
    # Check if user has staff access
    access_check = await api_service.check_staff_access(user_id)
    
    if not access_check or not access_check.get("has_access", False):
        # User doesn't have access
        await message.answer(
            "❌ У вас нет доступа к этому боту.\n\n"
            "Обратитесь к администратору для получения доступа."
        )
        return
    
    # User has access - show mini app button
    staff_user = access_check.get("staff_user", {})
    first_name = staff_user.get("first_name", "")
    last_name = staff_user.get("last_name", "")
    name = f"{first_name} {last_name}".strip() if first_name or last_name else "Сотрудник"
    
    welcome_text = (
        f"👋 Привет, {name}!\n\n"
        "Вы можете использовать это приложение для сканирования QR-кодов билетов."
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_mini_app_keyboard()
    )

