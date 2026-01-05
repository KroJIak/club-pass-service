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
from bot.services.api_service import api_service

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "menu_add_music")
async def handle_add_music(callback: CallbackQuery, state: FSMContext):
    """Handle 'Add music' button - check ticket and request song title."""
    locale = get_user_locale(callback.from_user.language_code)
    
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
    
    # Request song title
    text = t(locale, "messages.music.enter_title")
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
    song_title = message.text.strip()
    
    if not song_title:
        await message.answer(t(locale, "messages.music.enter_title"))
        return
    
    # Search for music
    search_result = await api_service.search_music(song_title)
    
    if not search_result or not search_result.get("tracks"):
        await message.answer(t(locale, "messages.music.no_results"))
        return
    
    tracks = search_result.get("tracks", [])
    
    # Format results as quote with hyperlinks
    result_lines = []
    for i, track in enumerate(tracks[:10], 1):  # Limit to 10 results
        title = track.get("title", "Unknown")
        artist = track.get("artist", "Unknown")
        
        # Get first available link
        links = track.get("links", {})
        url = None
        for link_key in ["yandex_music", "youtube", "spotify", "apple_music", "soundcloud"]:
            if links.get(link_key):
                url = links[link_key]
                break
        
        if url:
            result_lines.append(f"{i}. <a href=\"{url}\">{artist} - {title}</a>")
        else:
            result_lines.append(f"{i}. {artist} - {title}")
    
    result_text = "\n".join(result_lines)
    quote_text = f"<blockquote>{result_text}</blockquote>"
    
    # Create inline keyboard with track numbers
    builder = InlineKeyboardBuilder()
    for i in range(1, min(len(tracks) + 1, 11)):  # Max 10 buttons
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"select_track_{i}"))
    builder.adjust(5)  # 5 buttons per row
    builder.row(InlineKeyboardButton(
        text=t(locale, "buttons.back_to_menu"),
        callback_data="back_to_menu"
    ))
    
    # Save tracks in state
    await state.update_data(tracks=tracks, song_title=song_title)
    
    # Send results
    await message.answer(
        quote_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
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
    
    # Update message to show success
    await safe_edit_message(
        callback,
        t(locale, "messages.music.request_success"),
        reply_markup=get_back_keyboard(locale),
        locale=locale
    )

