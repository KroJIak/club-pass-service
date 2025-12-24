"""My tickets handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot.core.i18n import get_user_locale, t
from bot.core.keyboards import get_back_keyboard, get_tickets_keyboard
from bot.core.message_manager import safe_edit_message
from bot.core.qr_generator import generate_qr_code
from bot.services.api_service import api_service

router = Router()


@router.callback_query(F.data == "menu_my_tickets")
async def handle_my_tickets(callback: CallbackQuery, state: FSMContext):
    """Handle 'My tickets' button - show list of user tickets."""
    locale = get_user_locale(callback.from_user.language_code)
    await state.clear()
    
    # Fetch tickets from API
    user_id = callback.from_user.id
    tickets = await api_service.get_user_tickets(user_id, active_only=True)
    
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
    
    # Format tickets for keyboard
    formatted_tickets = []
    for ticket in tickets:
        event = ticket.get("event", {})
        ticket_type = ticket.get("ticket_type", {})
        event_name = event.get("name", "")
        
        formatted_tickets.append({
            "id": ticket.get("id"),
            "event_name": event_name,
            "event_date": event.get("date", ""),
            "event_time": event.get("time", ""),
            "ticket_type": ticket_type.get("name", ""),
            "status": ticket.get("status", "active"),
        })
    
    text = t(locale, "messages.tickets.select_ticket")
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_tickets_keyboard(locale, formatted_tickets),
        locale=locale,
        screen_key="my_tickets"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ticket_"))
async def handle_ticket_selected(callback: CallbackQuery, state: FSMContext):
    """Handle ticket selection - show QR code."""
    locale = get_user_locale(callback.from_user.language_code)
    ticket_id = int(callback.data.split("_")[1])
    
    # Fetch ticket details from API
    ticket = await api_service.get_ticket(ticket_id)
    if not ticket:
        await callback.answer("Ticket not found", show_alert=True)
        return
    
    # Extract data from API response
    event = ticket.get("event", {})
    ticket_type = ticket.get("ticket_type", {})
    event_name = event.get("name", "")
    token = ticket.get("token", "")
    
    # Generate QR code
    qr_bytes = generate_qr_code(token)
    qr_file = BufferedInputFile(qr_bytes, filename="ticket_qr.png")
    
    # Format ticket info text
    text = t(
        locale,
        "messages.tickets.ticket_info",
        event_name=event_name,
        event_date=event.get("date", ""),
        event_time=event.get("time", ""),
        ticket_type=ticket_type.get("name", ""),
        ticket_token=token,
    )
    
    # Create back to tickets list keyboard
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    back_builder = InlineKeyboardBuilder()
    back_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.back"),
        callback_data="back_to_tickets_list"
    ))
    back_keyboard = back_builder.as_markup()
    
    # Edit existing message with QR code
    await safe_edit_message(
        callback,
        text,
        reply_markup=back_keyboard,
        parse_mode="HTML",
        photo_input=qr_file,
    )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_tickets_list")
async def handle_back_to_tickets_list(callback: CallbackQuery, state: FSMContext):
    """Go back to tickets list from ticket detail."""
    await handle_my_tickets(callback, state)
