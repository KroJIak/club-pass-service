"""Ticket purchase flow handlers."""
from datetime import datetime
import pytz
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.i18n import get_user_locale, t
from bot.core.states import PurchaseStates
from bot.core.keyboards import (
    get_back_keyboard,
    get_events_keyboard,
    get_ticket_types_keyboard,
    get_quantity_keyboard,
    get_confirm_order_keyboard,
)
from bot.core.message_manager import safe_edit_message
from bot.services.api_service import api_service

router = Router()


@router.callback_query(F.data == "menu_buy_ticket")
async def handle_select_event(callback: CallbackQuery, state: FSMContext):
    """Start purchase flow - show events list."""
    locale = get_user_locale(callback.from_user.language_code)
    await state.set_state(PurchaseStates.selecting_event)
    
    # Fetch events from API
    events = await api_service.get_events(active_only=True)
    
    if not events:
        text = t(locale, "messages.purchase.no_events")
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_back_keyboard(locale),
            locale=locale,
            screen_key="buy_ticket"
        )
        await callback.answer()
        return
    
    text = t(locale, "messages.purchase.select_event")
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_events_keyboard(locale, events),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("event_"))
async def handle_event_selected(callback: CallbackQuery, state: FSMContext):
    """Handle event selection."""
    locale = get_user_locale(callback.from_user.language_code)
    event_id = int(callback.data.split("_")[1])
    
    # Save selected event to state
    await state.update_data(event_id=event_id)
    await state.set_state(PurchaseStates.selecting_ticket_type)
    
    # Fetch event details and ticket types from API
    event = await api_service.get_event(event_id)
    if not event:
        await callback.answer("Event not found", show_alert=True)
        return
    
    ticket_types = await api_service.get_ticket_types(event_id)
    if not ticket_types:
        text = t(locale, "messages.purchase.no_ticket_types")
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_back_keyboard(locale),
            locale=locale,
            screen_key="buy_ticket"
        )
        await callback.answer()
        return
    
    event_name = event.get("name", "")
    event_description = event.get("description", "") or ""
    
    # Format DJs list with HTML code tags
    djs = event.get("djs", [])
    djs_list = ", ".join([f"<code>{dj}</code>" for dj in djs]) if djs else ""
    
    # Format dates: DD.MM, HH:MM
    start_date_str = event.get("start_date", "")
    start_time_str = event.get("start_time", "")
    end_date_str = event.get("end_date", "")
    end_time_str = event.get("end_time", "")
    
    # Format date without year: DD.MM
    def format_date_without_year(date_str: str) -> str:
        """Format date from DD.MM.YYYY to DD.MM."""
        if not date_str:
            return date_str
        parts = date_str.split('.')
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return date_str
    
    # Format start date: DD.MM, HH:MM
    start_date_short = format_date_without_year(start_date_str)
    start_date_formatted = f"{start_date_short}, {start_time_str}" if start_date_short and start_time_str else (start_date_short or start_time_str or "")
    
    # Format end date: DD.MM, HH:MM
    end_date_short = format_date_without_year(end_date_str) if end_date_str else ''
    end_date_formatted = f"{end_date_short}, {end_time_str}" if end_date_short and end_time_str else (end_date_short or end_time_str or "")
    
    text = t(
        locale,
        "messages.purchase.select_ticket_type",
        event_name=event_name,
        event_description=event_description,
        djs_list=djs_list,
        start_date=start_date_formatted,
        end_date=end_date_formatted,
    )
    
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_ticket_types_keyboard(locale, ticket_types),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ticket_type_"))
async def handle_ticket_type_selected(callback: CallbackQuery, state: FSMContext):
    """Handle ticket type selection."""
    locale = get_user_locale(callback.from_user.language_code)
    ticket_type_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    event_id = data.get("event_id")
    
    # Save selected ticket type to state
    await state.update_data(ticket_type_id=ticket_type_id)
    
    # Fetch ticket types to get details
    ticket_types = await api_service.get_ticket_types(event_id)
    ticket_type = next((tt for tt in ticket_types if tt.get("id") == ticket_type_id), None)
    
    if not ticket_type:
        await callback.answer("Ticket type not found", show_alert=True)
        return
    
    available_quantity = ticket_type.get("available_quantity", 0)
    
    # If only 1 ticket available, skip quantity selection and go directly to confirmation
    if available_quantity == 1:
        # Set quantity to 1 and go directly to confirmation
        # Mark that we skipped quantity selection so back button works correctly
        await state.update_data(quantity=1, skipped_quantity_selection=True)
        await state.set_state(PurchaseStates.confirming_order)
        
        # Fetch full details from API
        event = await api_service.get_event(event_id)
        if not event:
            await callback.answer("Event not found", show_alert=True)
            return
        
        price_per_ticket = float(ticket_type.get("price", 0))
        total_price = price_per_ticket * 1
        
        # Format prices without .0 if integer
        price_per_ticket_formatted = int(price_per_ticket) if price_per_ticket.is_integer() else price_per_ticket
        total_price_formatted = int(total_price) if total_price.is_integer() else total_price
        
        event_name = event.get("name", "")
        
        # Format dates: DD.MM, HH:MM
        start_date_str = event.get("start_date", "")
        start_time_str = event.get("start_time", "")
        end_date_str = event.get("end_date", "")
        end_time_str = event.get("end_time", "")
        
        # Format date without year: DD.MM
        def format_date_without_year(date_str: str) -> str:
            """Format date from DD.MM.YYYY to DD.MM."""
            if not date_str:
                return date_str
            parts = date_str.split('.')
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
            return date_str
        
        # Format start date: DD.MM, HH:MM
        start_date_short = format_date_without_year(start_date_str)
        start_date_formatted = f"{start_date_short}, {start_time_str}" if start_date_short and start_time_str else (start_date_short or start_time_str or "")
        
        # Format end date: DD.MM, HH:MM
        end_date_short = format_date_without_year(end_date_str) if end_date_str else ''
        end_date_formatted = f"{end_date_short}, {end_time_str}" if end_date_short and end_time_str else (end_date_short or end_time_str or "")
        
        text = t(
            locale,
            "messages.purchase.confirm_order",
            event_name=event_name,
            start_date=start_date_formatted,
            end_date=end_date_formatted,
            ticket_type_name=ticket_type.get("name", ""),
            quantity=1,
            price_per_ticket=price_per_ticket_formatted,
            total_price=total_price_formatted,
        )
        
        from bot.core.keyboards import get_confirm_order_keyboard
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_confirm_order_keyboard(locale, total_price_formatted),
            locale=locale,
            screen_key="buy_ticket"
        )
        await callback.answer()
        return
    
    # If more than 1 ticket available, show quantity selection
    # Clear the flag since we're going through quantity selection
    await state.update_data(skipped_quantity_selection=False)
    await state.set_state(PurchaseStates.selecting_quantity)
    
    price = float(ticket_type.get("price", 0))
    price_formatted = int(price) if price.is_integer() else price
    text = t(
        locale,
        "messages.purchase.select_quantity",
        ticket_type_name=ticket_type.get("name", ""),
        price=price_formatted,
        available=available_quantity,
    )
    
    max_quantity = min(available_quantity, 5)
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_quantity_keyboard(locale, max_quantity),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("quantity_"))
async def handle_quantity_selected(callback: CallbackQuery, state: FSMContext):
    """Handle quantity selection."""
    locale = get_user_locale(callback.from_user.language_code)
    quantity = int(callback.data.split("_")[1])
    
    # Save quantity to state
    # Clear the flag since we went through quantity selection
    await state.update_data(quantity=quantity, skipped_quantity_selection=False)
    await state.set_state(PurchaseStates.confirming_order)
    
    # Get all selected data
    data = await state.get_data()
    event_id = data.get("event_id")
    ticket_type_id = data.get("ticket_type_id")
    
    # Fetch full details from API
    event = await api_service.get_event(event_id)
    if not event:
        await callback.answer("Event not found", show_alert=True)
        return
    
    ticket_types = await api_service.get_ticket_types(event_id)
    ticket_type = next((tt for tt in ticket_types if tt.get("id") == ticket_type_id), None)
    if not ticket_type:
        await callback.answer("Ticket type not found", show_alert=True)
        return
    
    price_per_ticket = float(ticket_type.get("price", 0))
    total_price = price_per_ticket * quantity
    
    # Format prices without .0 if integer
    price_per_ticket_formatted = int(price_per_ticket) if price_per_ticket.is_integer() else price_per_ticket
    total_price_formatted = int(total_price) if total_price.is_integer() else total_price
    
    event_name = event.get("name", "")
    
    # Format dates: DD.MM, HH:MM
    start_date_str = event.get("start_date", "")
    start_time_str = event.get("start_time", "")
    end_date_str = event.get("end_date", "")
    end_time_str = event.get("end_time", "")
    
    # Format date without year: DD.MM
    def format_date_without_year(date_str: str) -> str:
        """Format date from DD.MM.YYYY to DD.MM."""
        if not date_str:
            return date_str
        parts = date_str.split('.')
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return date_str
    
    # Format start date: DD.MM, HH:MM
    start_date_short = format_date_without_year(start_date_str)
    start_date_formatted = f"{start_date_short}, {start_time_str}" if start_date_short and start_time_str else (start_date_short or start_time_str or "")
    
    # Format end date: DD.MM, HH:MM
    end_date_short = format_date_without_year(end_date_str) if end_date_str else ''
    end_date_formatted = f"{end_date_short}, {end_time_str}" if end_date_short and end_time_str else (end_date_short or end_time_str or "")
    
    text = t(
        locale,
        "messages.purchase.confirm_order",
        event_name=event_name,
        start_date=start_date_formatted,
        end_date=end_date_formatted,
        ticket_type_name=ticket_type.get("name", ""),
        quantity=quantity,
        price_per_ticket=price_per_ticket_formatted,
        total_price=total_price_formatted,
    )
    
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_confirm_order_keyboard(locale, total_price_formatted),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_order")
async def handle_confirm_order(callback: CallbackQuery, state: FSMContext):
    """Handle order confirmation - proceed to payment."""
    locale = get_user_locale(callback.from_user.language_code)
    
    # Get order data
    data = await state.get_data()
    event_id = data.get("event_id")
    ticket_type_id = data.get("ticket_type_id")
    quantity = data.get("quantity")
    user_id = callback.from_user.id
    
    if not all([event_id, ticket_type_id, quantity]):
        await callback.answer("Missing order data", show_alert=True)
        return
    
    # Validation checks before confirming order
    # 1. Check if event exists and is active
    event = await api_service.get_event(event_id)
    if not event:
        error_text = t(locale, "messages.purchase.event_not_found", default="❌ Событие не найдено")
        await callback.answer(error_text, show_alert=True)
        return
    
    if not event.get("is_active", False):
        error_text = t(locale, "messages.purchase.event_inactive", default="❌ Событие неактивно")
        await callback.answer(error_text, show_alert=True)
        return
    
    # 2. Check if ticket type exists
    ticket_types = await api_service.get_ticket_types(event_id)
    ticket_type = next((tt for tt in ticket_types if tt.get("id") == ticket_type_id), None)
    if not ticket_type:
        error_text = t(locale, "messages.purchase.ticket_type_not_found", default="❌ Тип билета не найден")
        await callback.answer(error_text, show_alert=True)
        return
    
    # 3. Check if enough tickets are available
    available_quantity = ticket_type.get("available_quantity", 0)
    if available_quantity < quantity:
        error_text = t(
            locale,
            "messages.purchase.not_enough_tickets",
            default="❌ Недостаточно билетов. Доступно: {available}",
            available=available_quantity
        )
        await callback.answer(error_text, show_alert=True)
        return
    
    # 4. Check if event hasn't ended yet
    end_date_str = event.get("end_date", "")
    end_time_str = event.get("end_time", "")
    if end_date_str and end_time_str:
        try:
            # Parse end date/time: "DD.MM.YYYY HH:MM"
            end_dt = datetime.strptime(f"{end_date_str} {end_time_str}", "%d.%m.%Y %H:%M")
            # Use Europe/Moscow timezone (default for Russian events)
            tz = pytz.timezone("Europe/Moscow")
            end_dt_tz = tz.localize(end_dt)
            current_time = datetime.now(tz)
            
            if end_dt_tz <= current_time:
                error_text = t(locale, "messages.purchase.event_ended", default="❌ Событие уже закончилось")
                await callback.answer(error_text, show_alert=True)
                return
        except (ValueError, Exception) as e:
            # If date parsing fails, log but continue (don't block order)
            # This is a fallback - ideally dates should always be valid
            pass
    
    # Create order in API and get invoice data
    order_data = await api_service.create_order(
        user_id=user_id,
        event_id=event_id,
        ticket_type_id=ticket_type_id,
        quantity=quantity,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )
    
    if not order_data:
        text = t(locale, "messages.purchase.order_error")
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_back_keyboard(locale),
            locale=locale,
            screen_key="buy_ticket"
        )
        await callback.answer()
        return
    
    # MOCK MODE: Skip payment and create tickets directly
    # TODO: Remove this when YooKassa is configured
    result = await api_service.complete_order_mock(order_data['order_id'])
    
    if not result:
        text = t(locale, "messages.purchase.order_error")
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_back_keyboard(locale),
            locale=locale,
            screen_key="buy_ticket"
        )
        await callback.answer()
        return
    
    tickets_created = result.get("tickets_created", 0)
    
    if tickets_created > 0:
        text = t(
            locale,
            "messages.purchase.payment_success",
            tickets_count=tickets_created,
        )
    else:
        text = t(locale, "messages.purchase.payment_processed")
    
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="buy_ticket"
    )
    
    # Clear purchase state
    await state.clear()
    
    await callback.answer()
    
    # REAL PAYMENT MODE (commented out until YooKassa is configured):
    # # Send invoice to user
    # try:
    #     await callback.bot.send_invoice(
    #         chat_id=callback.from_user.id,
    #         title=order_data["invoice_title"],
    #         description=order_data["invoice_description"],
    #         payload=order_data["invoice_payload"],
    #         provider_token=order_data["provider_token"],
    #         currency="RUB",
    #         prices=order_data["invoice_prices"],
    #     )
    #     
    #     # Save order_id to state for payment processing
    #     await state.update_data(order_id=order_data["order_id"], payment_id=order_data["payment_id"])
    #     
    #     text = t(locale, "messages.purchase.invoice_sent")
    #     await safe_edit_message(
    #         callback,
    #         text,
    #         reply_markup=get_back_keyboard(locale),
    #         locale=locale,
    #         screen_key="buy_ticket"
    #     )
    # except Exception as e:
    #     print(f"Error sending invoice: {e}")
    #     text = t(locale, "messages.purchase.invoice_error")
    #     await safe_edit_message(
    #         callback,
    #         text,
    #         reply_markup=get_back_keyboard(locale),
    #         locale=locale,
    #         screen_key="buy_ticket"
    #     )


@router.callback_query(F.data == "cancel_order")
async def handle_cancel_order(callback: CallbackQuery, state: FSMContext):
    """Handle order cancellation."""
    locale = get_user_locale(callback.from_user.language_code)
    await state.clear()
    
    text = t(locale, "messages.purchase.order_cancelled")
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_quantity")
async def handle_back_to_quantity(callback: CallbackQuery, state: FSMContext):
    """Go back to quantity selection."""
    locale = get_user_locale(callback.from_user.language_code)
    data = await state.get_data()
    event_id = data.get("event_id")
    ticket_type_id = data.get("ticket_type_id")
    skipped_quantity_selection = data.get("skipped_quantity_selection", False)
    
    # If we skipped quantity selection (because only 1 ticket was available),
    # go back to ticket types selection instead
    if skipped_quantity_selection:
        await handle_back_to_ticket_types(callback, state)
        return
    
    if not ticket_type_id or not event_id:
        # If no ticket_type_id or event_id, go back to ticket types
        await handle_back_to_ticket_types(callback, state)
        return
    
    await state.set_state(PurchaseStates.selecting_quantity)
    # Clear quantity when going back
    await state.update_data(quantity=None)
    
    # Fetch ticket type details from API
    ticket_types = await api_service.get_ticket_types(event_id)
    ticket_type = next((tt for tt in ticket_types if tt.get("id") == ticket_type_id), None)
    
    if not ticket_type:
        await callback.answer("Ticket type not found", show_alert=True)
        return
    
    price = float(ticket_type.get("price", 0))
    price_formatted = int(price) if price.is_integer() else price
    text = t(
        locale,
        "messages.purchase.select_quantity",
        ticket_type_name=ticket_type.get("name", ""),
        price=price_formatted,
        available=ticket_type.get("available_quantity", 0),
    )
    
    max_quantity = min(ticket_type.get("available_quantity", 5), 5)
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_quantity_keyboard(locale, max_quantity),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_events")
async def handle_back_to_events(callback: CallbackQuery, state: FSMContext):
    """Go back to events selection."""
    locale = get_user_locale(callback.from_user.language_code)
    await state.set_state(PurchaseStates.selecting_event)
    # Clear event_id from state when going back
    await state.update_data(event_id=None, ticket_type_id=None, quantity=None)
    
    # Fetch events from API
    events = await api_service.get_events(active_only=True)
    
    if not events:
        text = t(locale, "messages.purchase.no_events")
        await safe_edit_message(
            callback,
            text,
            reply_markup=get_back_keyboard(locale),
            locale=locale,
            screen_key="buy_ticket"
        )
        await callback.answer()
        return
    
    text = t(locale, "messages.purchase.select_event")
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_events_keyboard(locale, events),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_ticket_types")
async def handle_back_to_ticket_types(callback: CallbackQuery, state: FSMContext):
    """Go back to ticket types selection."""
    locale = get_user_locale(callback.from_user.language_code)
    data = await state.get_data()
    event_id = data.get("event_id")
    
    if not event_id:
        # If no event_id, go back to events
        await handle_back_to_events(callback, state)
        return
    
    await state.set_state(PurchaseStates.selecting_ticket_type)
    # Clear ticket_type_id and quantity when going back
    await state.update_data(ticket_type_id=None, quantity=None)
    
    # Fetch event details and ticket types from API
    event = await api_service.get_event(event_id)
    if not event:
        await callback.answer("Event not found", show_alert=True)
        return
    
    ticket_types = await api_service.get_ticket_types(event_id)
    
    event_name = event.get("name", "")
    event_description = event.get("description", "") or ""
    
    # Format DJs list with HTML code tags
    djs = event.get("djs", [])
    djs_list = ", ".join([f"<code>{dj}</code>" for dj in djs]) if djs else ""
    
    # Format dates: DD.MM, HH:MM
    start_date_str = event.get("start_date", "")
    start_time_str = event.get("start_time", "")
    end_date_str = event.get("end_date", "")
    end_time_str = event.get("end_time", "")
    
    # Format date without year: DD.MM
    def format_date_without_year(date_str: str) -> str:
        """Format date from DD.MM.YYYY to DD.MM."""
        if not date_str:
            return date_str
        parts = date_str.split('.')
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return date_str
    
    # Format start date: DD.MM, HH:MM
    start_date_short = format_date_without_year(start_date_str)
    start_date_formatted = f"{start_date_short}, {start_time_str}" if start_date_short and start_time_str else (start_date_short or start_time_str or "")
    
    # Format end date: DD.MM, HH:MM
    end_date_short = format_date_without_year(end_date_str) if end_date_str else ''
    end_date_formatted = f"{end_date_short}, {end_time_str}" if end_date_short and end_time_str else (end_date_short or end_time_str or "")
    
    text = t(
        locale,
        "messages.purchase.select_ticket_type",
        event_name=event_name,
        event_description=event_description,
        djs_list=djs_list,
        start_date=start_date_formatted,
        end_date=end_date_formatted,
    )
    
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_ticket_types_keyboard(locale, ticket_types),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()
