"""My tickets handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
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
    
    # Create keyboard with back and refund buttons
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.refund_ticket"),
        callback_data=f"refund_ticket_{ticket_id}"
    ))
    keyboard_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.back"),
        callback_data="back_to_tickets_list"
    ))
    keyboard_builder.adjust(1)
    ticket_keyboard = keyboard_builder.as_markup()
    
    # Save ticket_id to state for refund confirmation
    await state.update_data(ticket_id=ticket_id)
    
    # Edit existing message with QR code
    await safe_edit_message(
        callback,
        text,
        reply_markup=ticket_keyboard,
        parse_mode="HTML",
        photo_input=qr_file,
    )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_tickets_list")
async def handle_back_to_tickets_list(callback: CallbackQuery, state: FSMContext):
    """Go back to tickets list from ticket detail."""
    await handle_my_tickets(callback, state)


@router.callback_query(F.data.startswith("refund_ticket_"))
async def handle_refund_ticket_click(callback: CallbackQuery, state: FSMContext):
    """Handle refund ticket button click - show confirmation dialog."""
    locale = get_user_locale(callback.from_user.language_code)
    ticket_id = int(callback.data.split("_")[2])
    
    # Save ticket_id to state
    await state.update_data(ticket_id=ticket_id)
    
    # Get confirmation text
    text = t(locale, "messages.tickets.refund_confirm")
    
    # Create confirmation keyboard
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from bot.core.message_manager import get_screen_image
    
    confirm_builder = InlineKeyboardBuilder()
    confirm_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.yes"),
        callback_data="refund_confirm_yes"
    ))
    confirm_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.no"),
        callback_data="refund_confirm_no"
    ))
    confirm_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.back_to_menu"),
        callback_data="back_to_menu"
    ))
    confirm_builder.adjust(2, 1)
    confirm_keyboard = confirm_builder.as_markup()
    
    # Get banner image
    photo_input = get_screen_image(locale, "refund_confirm")
    
    # Edit existing message with confirmation dialog
    await safe_edit_message(
        callback,
        text,
        reply_markup=confirm_keyboard,
        parse_mode="HTML",
        photo_input=photo_input,
    )
    
    await callback.answer()


@router.callback_query(F.data == "refund_confirm_yes")
async def handle_refund_confirm_yes(callback: CallbackQuery, state: FSMContext):
    """Handle refund confirmation - process refund."""
    locale = get_user_locale(callback.from_user.language_code)
    
    # Get ticket_id from state
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    
    if not ticket_id:
        await callback.answer("Ticket ID not found", show_alert=True)
        return
    
    # Call API to refund ticket
    result = await api_service.refund_ticket(ticket_id)
    
    if not result:
        text = t(locale, "messages.tickets.refund_error")
        await callback.message.edit_caption(
            caption=text,
            reply_markup=None,
            parse_mode="HTML",
        )
        await callback.answer()
        return
    
    # Check for specific error messages
    error_detail = result.get("detail") if isinstance(result, dict) else None
    if error_detail:
        if "already refunded" in error_detail.lower():
            text = t(locale, "messages.tickets.refund_already_refunded")
        elif "cannot refund" in error_detail.lower() or "used" in error_detail.lower():
            text = t(locale, "messages.tickets.refund_cannot_refund")
        else:
            text = t(locale, "messages.tickets.refund_error")
        
        await callback.message.edit_caption(
            caption=text,
            reply_markup=None,
            parse_mode="HTML",
        )
        await callback.answer()
        return
    
    # Success
    text = t(locale, "messages.tickets.refund_success")
    
    # Create keyboard with back to menu button
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    back_builder = InlineKeyboardBuilder()
    back_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.back_to_menu"),
        callback_data="back_to_menu"
    ))
    back_keyboard = back_builder.as_markup()
    
    await callback.message.edit_caption(
        caption=text,
        reply_markup=back_keyboard,
        parse_mode="HTML",
    )
    
    # Clear state
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "refund_confirm_no")
async def handle_refund_confirm_no(callback: CallbackQuery, state: FSMContext):
    """Handle refund cancellation - go back to ticket."""
    locale = get_user_locale(callback.from_user.language_code)
    
    # Get ticket_id from state
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    
    if not ticket_id:
        await callback.answer("Ticket ID not found", show_alert=True)
        return
    
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
    
    # Create keyboard with back and refund buttons
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.refund_ticket"),
        callback_data=f"refund_ticket_{ticket_id}"
    ))
    keyboard_builder.add(InlineKeyboardButton(
        text=t(locale, "buttons.back"),
        callback_data="back_to_tickets_list"
    ))
    keyboard_builder.adjust(1)
    ticket_keyboard = keyboard_builder.as_markup()
    
    # Edit message back to ticket view
    await callback.message.edit_media(
        media=InputMediaPhoto(media=qr_file, caption=text, parse_mode="HTML"),
        reply_markup=ticket_keyboard,
    )
    
    await callback.answer()
