"""Ticket purchase flow handlers."""
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

router = Router()


@router.callback_query(F.data == "menu_buy_ticket")
async def handle_select_event(callback: CallbackQuery, state: FSMContext):
    """Start purchase flow - show events list."""
    locale = get_user_locale(callback.from_user.language_code)
    await state.set_state(PurchaseStates.selecting_event)
    
    # TODO: Fetch events from API
    # For now, use mock data
    events = [
        {"id": 1, "name": "Новогодняя вечеринка", "date": "31.12.2024", "time": "22:00"},
        {"id": 2, "name": "House Music Night", "date": "05.01.2025", "time": "23:00"},
    ]
    
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
    
    # TODO: Fetch event details and ticket types from API
    # For now, use mock data
    event = {"id": event_id, "name": "Новогодняя вечеринка", "date": "31.12.2024", "time": "22:00"}
    ticket_types = [
        {"id": 1, "name": "Обычный", "price": 1500, "available": 50},
        {"id": 2, "name": "VIP", "price": 3000, "available": 20},
    ]
    
    text = t(
        locale,
        "messages.purchase.select_ticket_type",
        event_name=event.get("name", ""),
        event_date=event.get("date", ""),
        event_time=event.get("time", ""),
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
    
    # Save selected ticket type to state
    await state.update_data(ticket_type_id=ticket_type_id)
    await state.set_state(PurchaseStates.selecting_quantity)
    
    # TODO: Fetch ticket type details from API
    # For now, use mock data
    ticket_type = {"id": ticket_type_id, "name": "Обычный", "price": 1500, "available": 50}
    
    text = t(
        locale,
        "messages.purchase.select_quantity",
        ticket_type_name=ticket_type.get("name", ""),
        price=ticket_type.get("price", 0),
        available=ticket_type.get("available", 0),
    )
    
    max_quantity = min(ticket_type.get("available", 5), 5)
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
    await state.update_data(quantity=quantity)
    await state.set_state(PurchaseStates.confirming_order)
    
    # Get all selected data
    data = await state.get_data()
    event_id = data.get("event_id")
    ticket_type_id = data.get("ticket_type_id")
    
    # TODO: Fetch full details from API
    # For now, use mock data
    event = {"id": event_id, "name": "Новогодняя вечеринка", "date": "31.12.2024", "time": "22:00"}
    ticket_type = {"id": ticket_type_id, "name": "Обычный", "price": 1500}
    
    total_price = ticket_type.get("price", 0) * quantity
    
    text = t(
        locale,
        "messages.purchase.confirm_order",
        event_name=event.get("name", ""),
        event_date=event.get("date", ""),
        event_time=event.get("time", ""),
        ticket_type_name=ticket_type.get("name", ""),
        quantity=quantity,
        price_per_ticket=ticket_type.get("price", 0),
        total_price=total_price,
    )
    
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_confirm_order_keyboard(locale),
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
    
    # TODO: Create order in API and initiate YooKassa payment
    # For now, show placeholder
    text = t(locale, "messages.purchase.processing_payment")
    
    await safe_edit_message(
        callback,
        text,
        reply_markup=get_back_keyboard(locale),
        locale=locale,
        screen_key="buy_ticket"
    )
    await callback.answer()
    
    # TODO: After payment is processed, clear state
    # await state.clear()


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


@router.callback_query(F.data == "back_to_events")
async def handle_back_to_events(callback: CallbackQuery, state: FSMContext):
    """Go back to events selection."""
    await handle_select_event(callback, state)


@router.callback_query(F.data == "back_to_ticket_types")
async def handle_back_to_ticket_types(callback: CallbackQuery, state: FSMContext):
    """Go back to ticket types selection."""
    locale = get_user_locale(callback.from_user.language_code)
    data = await state.get_data()
    event_id = data.get("event_id")
    
    if not event_id:
        await handle_select_event(callback, state)
        return
    
    # Simulate event selection to show ticket types
    callback.data = f"event_{event_id}"
    await handle_event_selected(callback, state)
