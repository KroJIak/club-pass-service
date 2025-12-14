"""Start command handler."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import get_main_menu_keyboard
from bot.core.config import settings
from bot.core.message_manager import delete_temporary_user_messages

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    # Clear any previous state
    await state.clear()
    
    # Mark user message as temporary
    temporary_messages = [message]
    
    # Welcome message
    welcome_text = (
        f"👋 Добро пожаловать в <b>{settings.CLUB_NAME}</b>!\n\n"
        "🎉 Покупайте билеты на лучшие вечеринки прямо здесь!\n\n"
        "Выберите действие:"
    )
    
    # Send bot response
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    
    # Delete temporary user messages after bot response
    await delete_temporary_user_messages(message.from_user.id, temporary_messages)
