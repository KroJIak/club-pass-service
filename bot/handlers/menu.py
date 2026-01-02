"""Main menu handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile, ReactionTypeEmoji
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
from bot.services.api_service import api_service

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

    # Send confirmation with banner.jpg (uses cached image)
    from bot.core.message_manager import get_screen_image
    photo_input = get_screen_image(locale, "support")
    new_message = await message.answer_photo(
        photo=photo_input,
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
    """Handle 'Buy ticket' button - redirect to purchase flow."""
    from bot.handlers.purchase import handle_select_event
    
    # Redirect to purchase flow
    await handle_select_event(callback, state)


@router.callback_query(F.data == "menu_my_tickets")
async def handle_my_tickets(callback: CallbackQuery, state: FSMContext):
    """Handle 'My tickets' button - redirect to tickets handler."""
    from bot.handlers.tickets import handle_my_tickets as tickets_handler
    
    # Redirect to tickets handler
    await tickets_handler(callback, state)


@router.callback_query(F.data == "menu_club_info")
async def handle_club_info(callback: CallbackQuery):
    """Handle 'Club info' button."""
    locale = get_user_locale(callback.from_user.language_code)
    
    # Get club settings from API
    club_settings = await api_service.get_club_settings()
    
    info_text = ""
    
    if club_settings:
        address = club_settings.get("address")
        if address and address.strip():
            info_text += f"{t(locale, 'labels.address')}: {address}\n"
        
        phone = club_settings.get("phone")
        if phone and phone.strip():
            info_text += f"{t(locale, 'labels.phone')}: {phone}\n"
        
        email = club_settings.get("email")
        if email and email.strip():
            info_text += f"{t(locale, 'labels.email')}: {email}\n"
    
    # Fallback to settings if API fails (backward compatibility)
    if not info_text:
        if settings.CLUB_ADDRESS:
            info_text += f"{t(locale, 'labels.address')}: {settings.CLUB_ADDRESS}\n"
        
        if settings.CLUB_PHONE:
            info_text += f"{t(locale, 'labels.phone')}: {settings.CLUB_PHONE}\n"
        
        if settings.CLUB_EMAIL:
            info_text += f"{t(locale, 'labels.email')}: {settings.CLUB_EMAIL}\n"
    
    if not info_text:
        info_text = t(locale, 'messages.club_info_not_configured', default="Информация о клубе не настроена")
    
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


@router.callback_query(F.data == "support_new_message")
async def handle_support_new_message(callback: CallbackQuery, state: FSMContext):
    """Handle 'Write again' button - open support form."""
    locale = get_user_locale(callback.from_user.language_code)
    support_text = (
        f"{t(locale, 'messages.support_title')}\n\n"
        f"{t(locale, 'messages.support_prompt')}"
    )
    
    user_id = callback.from_user.id
    bot = callback.bot
    
    # Delete old system message before sending new one
    old_system = temporary_messages_middleware.get_last_system_message(user_id)
    if old_system:
        old_chat_id, old_message_id = old_system
        # Don't delete the message we're clicking on (admin response)
        if not (old_chat_id == callback.message.chat.id and old_message_id == callback.message.message_id):
            await temporary_messages_middleware.delete_system_message(bot, old_chat_id, old_message_id)
    
    # Clear last system message tracking
    temporary_messages_middleware.clear_last_system_message(user_id)
    
    # Send new system message with support form
    from bot.core.message_manager import get_screen_image
    photo_input = get_screen_image(locale, "support")
    new_message = await callback.message.answer_photo(
        photo=photo_input,
        caption=support_text,
        reply_markup=get_support_cancel_keyboard(locale),
        parse_mode="HTML",
    )
    
    # Set new message as system message
    temporary_messages_middleware.set_last_system_message(
        user_id, new_message.chat.id, new_message.message_id
    )
    
    # Flush pending temporary user messages
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
    
    await callback.answer()
    
    # Set state to wait for support message
    await state.set_state(SupportStates.waiting_message)


@router.message(SupportStates.waiting_message, F.photo)
async def handle_support_photo(message: Message, state: FSMContext):
    """Handle support photo from user."""
    # Get the largest photo
    photo = message.photo[-1] if message.photo else None
    if not photo:
        return
    
    # Set reaction "writing hand" on user's message
    try:
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="✍️")]
        )
    except Exception as e:
        logger.warning(f"Failed to set reaction on support photo: {e}")
    
    # Download and save photo locally
    from bot.services.file_service import download_and_save_photo
    photo_path = await download_and_save_photo(message.bot, photo.file_id)
    
    if not photo_path:
        logger.error(f"Failed to download and save photo with file_id: {photo.file_id}")
        # Still continue to create message without photo
    
    # Get existing photo paths from state (if user sent multiple photos)
    state_data = await state.get_data()
    photo_paths = state_data.get("support_photo_paths", [])
    if photo_path:
        photo_paths.append(photo_path)
        await state.update_data(support_photo_paths=photo_paths)
    
    logger.info(f"Photo paths to send: {photo_paths}")
    
    # Send message to support/admin via API immediately
    locale = get_user_locale(message.from_user.language_code)
    
    # Get or create user first
    user_data = await api_service.create_or_update_user(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    
    if not user_data:
        # If user creation fails, still show confirmation but log error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create/update user for support message: telegram_user_id={message.from_user.id}")
        confirmation_text = t(locale, "messages.support_received")
    else:
        # Create support message with photos (no text)
        user_id = user_data.get("id")
        if user_id:
            logger.info(f"Creating support message with photo_paths: {photo_paths}")
            support_result = await api_service.create_support_message(
                user_id=user_id,
                message="",  # Empty message for photo-only support messages
                photo_paths=photo_paths if photo_paths else None
            )
            if not support_result:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create support message for user_id={user_id}")
        
        confirmation_text = t(locale, "messages.support_received")

    user_id = message.from_user.id

    await _finalize_support_feedback(
        message=message,
        user_id=user_id,
        locale=locale,
        confirmation_text=confirmation_text,
    )

    await state.clear()


@router.message(SupportStates.waiting_message, F.text)
async def handle_support_message(message: Message, state: FSMContext):
    """Handle support message from user."""
    support_message = message.text
    
    # Set reaction "writing hand" on user's message
    try:
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="✍️")]
        )
    except Exception as e:
        # If reaction fails, log but don't break the flow
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to set reaction on support message: {e}")
    
    # Get photo paths from state if any (already downloaded and saved)
    state_data = await state.get_data()
    photo_paths = state_data.get("support_photo_paths", [])
    
    # Send message to support/admin via API
    locale = get_user_locale(message.from_user.language_code)
    
    # Get or create user first
    from bot.services.api_service import api_service
    user_data = await api_service.create_or_update_user(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    
    if not user_data:
        # If user creation fails, still show confirmation but log error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create/update user for support message: telegram_user_id={message.from_user.id}")
        confirmation_text = t(locale, "messages.support_received")
    else:
        # Create support message
        user_id = user_data.get("id")
        if user_id:
            support_result = await api_service.create_support_message(
                user_id=user_id,
                message=support_message,
                photo_paths=photo_paths if photo_paths else None
            )
            if not support_result:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create support message for user_id={user_id}")
        
        confirmation_text = t(locale, "messages.support_received")

    user_id = message.from_user.id

    await _finalize_support_feedback(
        message=message,
        user_id=user_id,
        locale=locale,
        confirmation_text=confirmation_text,
    )

    await state.clear()
