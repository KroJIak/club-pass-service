"""Main menu handlers."""
import logging
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile, ReactionTypeEmoji
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import (
    get_back_keyboard,
    get_main_menu_keyboard,
    get_support_cancel_keyboard,
    get_back_to_menu_keyboard,
)
from bot.core.config import settings
from bot.core.states import SupportStates
from bot.core.message_manager import safe_edit_message, remove_inline_keyboard
from bot.core.i18n import get_user_locale, t
from bot.core.middleware import temporary_messages_middleware
from bot.core.assets import get_locale_image_path
from bot.services.api_service import api_service

router = Router()
logger = logging.getLogger(__name__)

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
    # Check if menu photos exist
    menu_photos = await api_service.get_menu_photos()
    has_menu_photos = len(menu_photos) > 0
    
    # Main menu: only image, no text
    await safe_edit_message(
        callback,
        "",  # No text for main menu
        reply_markup=get_main_menu_keyboard(locale, has_menu_photos=has_menu_photos),
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


@router.callback_query(F.data == "menu_food_drinks")
async def handle_menu_food_drinks(callback: CallbackQuery, state: FSMContext):
    """Handle 'Menu' button - show food and drinks menu photos."""
    locale = get_user_locale(callback.from_user.language_code)
    
    # Get menu photos from API
    menu_photos = await api_service.get_menu_photos()
    
    if not menu_photos:
        # No photos, show empty message
        await safe_edit_message(
            callback,
            t(locale, "messages.menu_empty"),
            reply_markup=get_back_to_menu_keyboard(locale),
            locale=locale,
        )
        await callback.answer()
        return
    
    # Prepare media group (max 10 photos)
    from aiogram.types import InputMediaPhoto
    from bot.core.config import settings
    import os
    
    media_group = []
    photos_to_send = menu_photos[:10]  # Telegram limit is 10 photos per media group
    
    for photo in photos_to_send:
        # Build full file path
        file_path = photo.get("file_path", "")
        if not file_path:
            continue
        
        # Get absolute path
        full_path = os.path.join(os.getcwd(), file_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            logger.warning(f"Menu photo file not found: {full_path}")
            continue
        
        # Create InputMediaPhoto
        media = InputMediaPhoto(media=FSInputFile(full_path))
        media_group.append(media)
    
    if not media_group:
        # No valid photos found
        await safe_edit_message(
            callback,
            t(locale, "messages.menu_empty"),
            reply_markup=get_back_to_menu_keyboard(locale),
            locale=locale,
        )
        await callback.answer()
        return
    
    # Send media group
    user_id = callback.from_user.id
    bot = callback.bot
    
    # Freeze previous system message
    await _freeze_previous_system_message(bot=bot, user_id=user_id)
    temporary_messages_middleware.clear_last_system_message(user_id)
    
    # Send media group
    messages = await bot.send_media_group(
        chat_id=callback.message.chat.id,
        media=media_group,
    )
    
    # Mark all media group messages as temporary (they will be deleted on next flush)
    for msg in messages:
        temporary_messages_middleware.pending_user_messages[user_id].append(
            (msg.chat.id, msg.message_id)
        )
    temporary_messages_middleware._persist_state()
    
    # Send message with "Main Menu" button
    menu_title = t(locale, "messages.menu_title")
    menu_order_text = t(locale, "messages.menu_order_text")
    menu_text = f"{menu_title}\n\n{menu_order_text}"
    new_message = await bot.send_message(
        chat_id=callback.message.chat.id,
        text=menu_text,
        reply_markup=get_back_to_menu_keyboard(locale),
        parse_mode="HTML",
    )
    
    # Set the last message as system message
    temporary_messages_middleware.set_last_system_message(
        user_id, new_message.chat.id, new_message.message_id
    )
    
    # Flush pending temporary user messages (this will delete the media group messages)
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
    
    # Delete the original message with menu button
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete original menu message: {e}")
    
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
    
    # Get caption (text with photo) if exists
    photo_caption = message.caption or ""
    
    # Check if this is part of a media group
    media_group_id = message.media_group_id
    
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
    
    # Get existing data from state
    state_data = await state.get_data()
    photo_paths = state_data.get("support_photo_paths", [])
    existing_text = state_data.get("support_text", "")
    pending_media_group_id = state_data.get("pending_media_group_id")
    
    # Add photo to list
    if photo_path:
        photo_paths.append(photo_path)
    
    # Combine existing text with caption
    message_text = existing_text
    if photo_caption:
        if message_text:
            message_text = f"{message_text}\n{photo_caption}"
        else:
            message_text = photo_caption
    
    # If this is part of a media group, wait a bit for other photos
    if media_group_id:
        # Check if we're already processing this media group
        if pending_media_group_id == media_group_id:
            # This is another photo from the same media group, just update state and return
            await state.update_data(
                support_photo_paths=photo_paths,
                support_text=message_text,
                pending_media_group_id=media_group_id
            )
            logger.info(f"Added photo to media group {media_group_id}, waiting for more...")
            return
        
        # This is the first photo of a new media group
        await state.update_data(
            support_photo_paths=photo_paths,
            support_text=message_text,
            pending_media_group_id=media_group_id
        )
        logger.info(f"Started media group {media_group_id}, waiting for more photos...")
        
        # Wait a bit for other photos in the group to arrive
        # Telegram sends media group photos with small delays, so we wait longer
        await asyncio.sleep(5.0)
        
        # Check state again - if media_group_id changed, another group started
        state_data = await state.get_data()
        if state_data.get("pending_media_group_id") != media_group_id:
            # Another media group started, process the previous one
            logger.info(f"Media group {media_group_id} completed, processing...")
            # Use the data we collected
            photo_paths = state_data.get("support_photo_paths", [])
            message_text = state_data.get("support_text", "")
        else:
            # Still the same group, process it now
            logger.info(f"Processing media group {media_group_id} after wait...")
            # Get the latest state data
            state_data = await state.get_data()
            photo_paths = state_data.get("support_photo_paths", [])
            message_text = state_data.get("support_text", "")
    else:
        # Single photo, update state
        await state.update_data(
            support_photo_paths=photo_paths,
            support_text=message_text
        )
    
    # Get final data from state
    state_data = await state.get_data()
    final_photo_paths = state_data.get("support_photo_paths", [])
    final_message_text = state_data.get("support_text", "")
    
    logger.info(f"Photo paths to send: {final_photo_paths}, message text: '{final_message_text}'")
    
    # Send message to support/admin via API
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
        logger.error(f"Failed to create/update user for support message: telegram_user_id={message.from_user.id}")
        confirmation_text = t(locale, "messages.support_received")
    else:
        # Create support message with photos and text (if any)
        user_id = user_data.get("id")
        if user_id:
            logger.info(f"Creating support message with photo_paths: {final_photo_paths}, message: '{final_message_text}'")
            support_result = await api_service.create_support_message(
                user_id=user_id,
                message=final_message_text,  # Use caption or existing text
                photo_paths=final_photo_paths if final_photo_paths else None
            )
            if not support_result:
                logger.error(f"Failed to create support message for user_id={user_id}")
        
        confirmation_text = t(locale, "messages.support_received")

    user_id = message.from_user.id

    await _finalize_support_feedback(
        message=message,
        user_id=user_id,
        locale=locale,
        confirmation_text=confirmation_text,
    )

    # Clear state after processing
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
