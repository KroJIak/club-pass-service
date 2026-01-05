"""Music request handlers."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.keyboards import get_back_keyboard
from bot.core.states import MusicStates
from bot.core.i18n import get_user_locale, t
from bot.core.message_manager import safe_edit_message
from bot.core.middleware import temporary_messages_middleware
from bot.services.api_service import api_service

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "menu_add_music")
async def handle_add_music(callback: CallbackQuery, state: FSMContext):
    """Handle 'Add music' button - check ticket and request song title."""
    locale = get_user_locale(callback.from_user.language_code)
    bot = callback.bot
    user_id = callback.from_user.id
    
    # Get user tickets to check if they have a used ticket for an active event
    telegram_user_id = callback.from_user.id
    tickets = await api_service.get_user_tickets(telegram_user_id, active_only=False)
    
    # Filter for used tickets
    used_tickets = [t for t in tickets if t.get("status") == "used"]
    
    if not used_tickets:
        await callback.answer(
            t(locale, "messages.music.not_in_club"),
            show_alert=True
        )
        return
    
    # Check if there's an active event that hasn't ended
    # This check will be done on the API side, but we can do a basic check here
    # For now, just proceed - API will validate
    
    # Request song title in quote format
    text = f"<blockquote>{t(locale, 'messages.music.enter_title')}</blockquote>"
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_back_keyboard(locale),
        locale=locale
    )
    
    await state.set_state(MusicStates.waiting_title)
    await callback.answer()


@router.message(MusicStates.waiting_title)
async def handle_music_title_input(message: Message, state: FSMContext):
    """Handle song title input - search for tracks and show results."""
    locale = get_user_locale(message.from_user.language_code)
    bot = message.bot
    user_id = message.from_user.id
    song_title = message.text.strip()
    
    if not song_title:
        enter_title_text = f"<blockquote>{t(locale, 'messages.music.enter_title')}</blockquote>"
        enter_msg = await message.answer(enter_title_text, parse_mode="HTML")
        temporary_messages_middleware.set_last_system_message(user_id, enter_msg.chat.id, enter_msg.message_id)
        await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
        return
    
    # Search for music
    search_result = await api_service.search_music(song_title)
    
    if not search_result or not search_result.get("tracks"):
        # Send no results message and flush pending user messages
        no_results_msg = await message.answer(t(locale, "messages.music.no_results"))
        temporary_messages_middleware.set_last_system_message(user_id, no_results_msg.chat.id, no_results_msg.message_id)
        await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
        return
    
    tracks = search_result.get("tracks", [])
    
    # Limit to 4 tracks as per plan
    tracks = tracks[:4]
    
    # Format results as quote with hyperlinks
    result_lines = []
    for i, track in enumerate(tracks, 1):
        title = track.get("title", "Unknown")
        artist = track.get("artist", "Unknown")
        
        # Get Yandex Music link
        links = track.get("links", {})
        yandex_url = links.get("yandex_music")
        
        if yandex_url:
            result_lines.append(f"{i}. <a href=\"{yandex_url}\">{artist} - {title}</a>")
        else:
            result_lines.append(f"{i}. {artist} - {title}")
    
    result_text = "\n".join(result_lines)
    quote_text = f"<blockquote>{result_text}</blockquote>"
    
    # Create inline keyboard with track numbers (1-4)
    builder = InlineKeyboardBuilder()
    for i in range(1, len(tracks) + 1):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"select_track_{i}"))
    builder.adjust(4)  # 4 buttons per row
    builder.row(InlineKeyboardButton(
        text=t(locale, "buttons.back_to_menu"),
        callback_data="back_to_menu"
    ))
    
    # Save tracks in state
    await state.update_data(tracks=tracks, song_title=song_title)
    
    # Send results
    results_msg = await message.answer(
        quote_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    # Mark as system message and flush pending user messages (including the user's song title message)
    temporary_messages_middleware.set_last_system_message(user_id, results_msg.chat.id, results_msg.message_id)
    await temporary_messages_middleware.flush_pending_user_messages(bot, user_id)
    
    # Clear state
    await state.clear()


@router.callback_query(F.data.startswith("select_track_"))
async def handle_track_selected(callback: CallbackQuery, state: FSMContext):
    """Handle track selection - create music request."""
    locale = get_user_locale(callback.from_user.language_code)
    
    # Get track index from callback data
    try:
        track_index = int(callback.data.split("_")[-1]) - 1
    except (ValueError, IndexError):
        await callback.answer("Invalid track selection", show_alert=True)
        return
    
    # Get tracks from state
    data = await state.get_data()
    tracks = data.get("tracks", [])
    
    if track_index < 0 or track_index >= len(tracks):
        await callback.answer("Invalid track selection", show_alert=True)
        return
    
    track = tracks[track_index]
    title = track.get("title", "")
    artist = track.get("artist", "")
    links = track.get("links", {})
    
    # Get URLs
    yandex_url = links.get("yandex_music")
    other_url = links.get("youtube") or links.get("spotify") or links.get("apple_music") or links.get("soundcloud")
    
    # Create music request
    telegram_user_id = callback.from_user.id
    result = await api_service.create_music_request(
        telegram_user_id=telegram_user_id,
        track_title=title,
        track_artist=artist,
        yandex_music_url=yandex_url,
        other_source_url=other_url
    )
    
    if not result:
        await callback.answer(t(locale, "messages.music.search_error"), show_alert=True)
        return
    
    if result.get("error"):
        error_msg = result.get("error", "Unknown error")
        await callback.answer(error_msg, show_alert=True)
        return
    
    # Success
    await callback.answer(t(locale, "messages.music.request_success"), show_alert=True)
    
    # Clear state and return to menu
    await state.clear()
    
    # Update message to show success and return to menu
    from bot.core.keyboards import get_main_menu_keyboard
    menu_photos = await api_service.get_menu_photos()
    has_menu_photos = len(menu_photos) > 0
    
    await safe_edit_message(
        callback,
        t(locale, "messages.music.request_success"),
        reply_markup=get_main_menu_keyboard(locale, has_menu_photos=has_menu_photos),
        locale=locale,
        screen_key="main_menu"
    )

