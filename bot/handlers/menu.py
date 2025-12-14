"""Main menu handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import (
    get_back_keyboard,
    get_main_menu_keyboard,
    get_support_cancel_keyboard,
)
from bot.core.config import settings
from bot.core.states import SupportStates
from bot.core.message_manager import safe_edit_message, remove_inline_keyboard
from bot.core.i18n import get_user_locale, t
from bot.core.middleware import temporary_messages_middleware
from bot.core.assets import get_locale_image_path

router = Router()

async def _freeze_previous_system_message(*, bot, user_id: int) -> None:
    """Remove inline keyboard from the last system message (best-effort)."""
    ref = temporary_messages_middleware.get_last_system_message(user_id)
    if not ref:
        return
    chat_id, message_id = ref
    await remove_inline_keyboard(bot, chat_id, message_id)


async def _finalize_support_feedback(
    *,
    message: Message,
    user_id: int,
    locale: str,
    confirmation_text: str,
) -> None:
    """
    Support UX "easter egg":
    - previous system message stays in chat, but loses system status and inline buttons
    - confirmation is always sent as a new system message
    - temporary user messages are flushed (but support feedback is not queued)
    """
    bot = message.bot

    await _freeze_previous_system_message(bot=bot, user_id=user_id)
    temporary_messages_middleware.clear_last_system_message(user_id)

    # Send confirmation with banner.jpg
    photo_path = get_locale_image_path(locale, t(locale, "screens.support.image"))
    photo = FSInputFile(photo_path)
    new_message = await message.answer_photo(
        photo=photo,
        caption=confirmation_text,
        reply_markup=get_back_keyboard(locale),
        parse_mode="HTML",
    )
    temporary_messages_middleware.set_last_system_message(
        user_id, new_message.chat.id, new_message.message_id
    )
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Handle back to menu callback."""
    await state.clear()
    
    locale = get_user_locale(callback.from_user.language_code)
    # Main menu: only image, no text
    await safe_edit_message(
        callback,
        "",  # No text for main menu
        reply_markup=get_main_menu_keyboard(locale),
        locale=locale,
        screen_key="main_menu"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_buy_ticket")
async def handle_buy_ticket(callback: CallbackQuery, state: FSMContext):
    """Handle 'Buy ticket' button."""
    locale = get_user_locale(callback.from_user.language_code)
    # Buy ticket: only image, no text
    await safe_edit_message(
        callback, 
        "",  # No text
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_my_tickets")
async def handle_my_tickets(callback: CallbackQuery):
    """Handle 'My tickets' button."""
    locale = get_user_locale(callback.from_user.language_code)
    # My tickets: only image, no text
    await safe_edit_message(
        callback, 
        "",  # No text
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="my_tickets"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_events")
async def handle_upcoming_events(callback: CallbackQuery):
    """Handle 'Upcoming events' button."""
    locale = get_user_locale(callback.from_user.language_code)
    # Events: only image, no text
    await safe_edit_message(
        callback, 
        "",  # No text
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="events"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_club_info")
async def handle_club_info(callback: CallbackQuery):
    """Handle 'Club info' button."""
    locale = get_user_locale(callback.from_user.language_code)
    # Club info: only address, phone, email (no title, no club name)
    info_text = f"{t(locale, 'labels.address')}: {settings.CLUB_ADDRESS}\n"
    
    if settings.CLUB_PHONE:
        info_text += f"{t(locale, 'labels.phone')}: {settings.CLUB_PHONE}\n"
    
    if settings.CLUB_EMAIL:
        info_text += f"{t(locale, 'labels.email')}: {settings.CLUB_EMAIL}\n"
    
    await safe_edit_message(
        callback,
        info_text,
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="club_info"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_support")
async def handle_support(callback: CallbackQuery, state: FSMContext):
    """Handle 'Support' button - request message from user."""
    locale = get_user_locale(callback.from_user.language_code)
    support_text = (
        f"{t(locale, 'messages.support_title')}\n\n"
        f"{t(locale, 'messages.support_prompt')}"
    )
    
    await safe_edit_message(
        callback,
        support_text,
        reply_markup=get_support_cancel_keyboard(locale),
        locale=locale,
        screen_key="support"
    )
    await callback.answer()
    
    # Set state to wait for support message
    await state.set_state(SupportStates.waiting_message)


@router.message(SupportStates.waiting_message, F.text)
async def handle_support_message(message: Message, state: FSMContext):
    """Handle support message from user."""
    support_message = message.text
    
    # TODO: Send message to support/admin
    # For now, just confirm receipt
    
    # This message is NOT temporary - it's feedback, should remain
    # Don't delete it - it's not a temporary message
    
    locale = get_user_locale(message.from_user.language_code)
    confirmation_text = t(locale, "messages.support_received")

    user_id = message.from_user.id

    await _finalize_support_feedback(
        message=message,
        user_id=user_id,
        locale=locale,
        confirmation_text=confirmation_text,
    )

    await state.clear()
