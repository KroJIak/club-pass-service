"""Start command handler."""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import get_main_menu_keyboard
from bot.core.config import settings
from bot.core.middleware import temporary_messages_middleware
from bot.core.i18n import get_user_locale, t

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    # Clear any previous state
    await state.clear()
    
    user_id = message.from_user.id
    bot = message.bot
    old_system = temporary_messages_middleware.get_last_system_message(user_id)

    locale = get_user_locale(message.from_user.language_code)

    welcome_text = t(
        locale,
        "messages.start",
        club_name=settings.CLUB_NAME,
        choose_action=t(locale, "messages.choose_action"),
    )
    
    # 1) Send new system message first
    new_message = await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(locale),
        parse_mode="HTML"
    )
    
    # 2) Delete old system message (only for /start)
    if old_system:
        old_chat_id, old_message_id = old_system
        # Don't delete the message we just sent (paranoia)
        if not (old_chat_id == new_message.chat.id and old_message_id == new_message.message_id):
            await temporary_messages_middleware.delete_system_message(bot, old_chat_id, old_message_id)

    # 3) Remember new system message ID as current
    temporary_messages_middleware.set_last_system_message(user_id, new_message.chat.id, new_message.message_id)

    # 4) After system send -> delete all pending temporary user messages (including /start)
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
