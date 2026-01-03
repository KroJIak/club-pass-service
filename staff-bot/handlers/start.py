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
    
    user = message.from_user
    user_id = user.id
    
    # First, create or update user in the main users table
    await api_service.get_or_create_user(
        telegram_user_id=user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    
    # Check if user has staff access
    access_check = await api_service.check_staff_access(user_id)
    
    if not access_check or not access_check.get("has_access", False):
        # User doesn't have access
        await message.answer(
            "❌ You don't have access to this bot.\n\n"
            "Contact the administrator to get access."
        )
        return
    
    # User has access - show mini app button
    staff_user = access_check.get("staff_user", {})
    first_name = staff_user.get("first_name", "")
    last_name = staff_user.get("last_name", "")
    name = f"{first_name} {last_name}".strip() if first_name or last_name else "Staff"
    
    welcome_text = (
        f"👋 Hello, {name}!\n\n"
        "You can use this app to scan ticket QR codes."
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_mini_app_keyboard()
    )

