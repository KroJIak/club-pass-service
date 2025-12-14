"""Start command handler."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import get_main_menu_keyboard
from bot.core.config import settings
from bot.core.middleware import temporary_messages_middleware

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    # Clear any previous state
    await state.clear()
    
    user_id = message.from_user.id
    bot = message.bot
    
    # Welcome message
    welcome_text = (
        f"👋 Добро пожаловать в <b>{settings.CLUB_NAME}</b>!\n\n"
        "🎉 Покупайте билеты на лучшие вечеринки прямо здесь!\n\n"
        "Выберите действие:"
    )
    
    # 1. Send new system message first
    new_message = await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    
    # 2. Delete old system message if exists
    await temporary_messages_middleware.delete_last_system_message(user_id, bot)
    
    # 3. Remember new system message ID
    temporary_messages_middleware.set_last_system_message(
        user_id, new_message.message_id
    )
