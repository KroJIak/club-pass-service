"""My tickets handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot.core.i18n import get_user_locale, t
from bot.core.keyboards import get_back_keyboard, get_tickets_keyboard
from bot.core.message_manager import safe_edit_message
from bot.core.qr_generator import generate_qr_code

router = Router()


@router.callback_query(F.data == "menu_my_tickets")
async def handle_my_tickets(callback: CallbackQuery, state: FSMContext):
    """Handle 'My tickets' button - show list of user tickets."""
    locale = get_user_locale(callback.from_user.language_code)
    await state.clear()
    
    # TODO: Fetch tickets from API
    # For now, use mock data
    user_id = callback.from_user.id
    tickets = [
        {
            "id": 1,
            "token": "TKT-12345-ABCDE",
            "event_djs": "DJ. DIMSY, EMPYZ, JEWGEN, ZIPSI",
            "event_date": "31.12.2024",
            "event_time": "22:00",
            "ticket_type": "Обычный",
            "status": "active",
        },
        {
            "id": 2,
            "token": "TKT-67890-FGHIJ",
            "event_djs": "DJ. DIMSY, EMPYZ",
            "event_date": "05.01.2025",
            "event_time": "23:00",
            "ticket_type": "VIP",
            "status": "active",
        },
    ]
    
    if not tickets:
        text = t(locale, "messages.tickets.no_tickets")
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_back_keyboard(locale),
            locale=locale,
            screen_key="my_tickets"
        )
        await callback.answer()
        return
    
    text = t(locale, "messages.tickets.select_ticket")
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_tickets_keyboard(locale, tickets),
        locale=locale,
        screen_key="my_tickets"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ticket_"))
async def handle_ticket_selected(callback: CallbackQuery, state: FSMContext):
    """Handle ticket selection - show QR code."""
    locale = get_user_locale(callback.from_user.language_code)
    ticket_id = int(callback.data.split("_")[1])
    
    # TODO: Fetch ticket details from API
    # For now, use mock data
    ticket = {
        "id": ticket_id,
        "token": f"TKT-{ticket_id:05d}-ABCDE",
        "event_djs": "DJ. DIMSY, EMPYZ, JEWGEN, ZIPSI",
        "event_date": "31.12.2024",
        "event_time": "22:00",
        "ticket_type": "Обычный",
        "status": "active",
    }
    
    # Generate QR code
    qr_bytes = generate_qr_code(ticket.get("token", ""))
    qr_file = BufferedInputFile(qr_bytes, filename="ticket_qr.png")
    
    # Format ticket info text
    text = t(
        locale,
        "messages.tickets.ticket_info",
        event_djs=ticket.get("event_djs", ""),
        event_date=ticket.get("event_date", ""),
        event_time=ticket.get("event_time", ""),
        ticket_type=ticket.get("ticket_type", ""),
        ticket_token=ticket.get("token", ""),
    )
    
    # Send QR code as photo
    await callback.message.delete()
    
    # Create back to tickets list keyboard
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    back_builder = InlineKeyboardBuilder()
    back_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.back"),
        callback_data="back_to_tickets_list"
    ))
    
    new_message = await callback.message.answer_photo(
        photo=qr_file,
        caption=text,
        reply_markup=back_builder.as_markup(),
        parse_mode="HTML",
    )
    
    # Update system message tracking
    from bot.core.middleware import temporary_messages_middleware
    user_id = callback.from_user.id
    temporary_messages_middleware.set_last_system_message(
        user_id, new_message.chat.id, new_message.message_id
    )
    await temporary_messages_middleware.flush_pending_user_messages(callback.bot, user_id)
    
    await callback.answer()
