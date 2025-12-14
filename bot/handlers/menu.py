"""Main menu handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import get_main_menu_keyboard, get_support_cancel_keyboard
from bot.core.config import settings
from bot.core.states import SupportStates
from bot.core.message_manager import safe_edit_message, delete_temporary_user_messages

router = Router()


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Handle back to menu callback."""
    await state.clear()
    
    menu_text = (
        f"👋 <b>{settings.CLUB_NAME}</b>\n\n"
        "Выберите действие:"
    )
    
    await safe_edit_message(
        callback,
        menu_text,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_buy_ticket")
async def handle_buy_ticket(callback: CallbackQuery, state: FSMContext):
    """Handle 'Buy ticket' button."""
    await callback.answer("🚧 Функция покупки билетов находится в разработке", show_alert=True)


@router.callback_query(F.data == "menu_my_tickets")
async def handle_my_tickets(callback: CallbackQuery):
    """Handle 'My tickets' button."""
    await callback.answer("🚧 Функция просмотра билетов находится в разработке", show_alert=True)


@router.callback_query(F.data == "menu_events")
async def handle_upcoming_events(callback: CallbackQuery):
    """Handle 'Upcoming events' button."""
    await callback.answer("🚧 Функция просмотра событий находится в разработке", show_alert=True)


@router.callback_query(F.data == "menu_club_info")
async def handle_club_info(callback: CallbackQuery):
    """Handle 'Club info' button."""
    info_text = (
        f"<b>{settings.CLUB_NAME}</b>\n\n"
        f"📍 Адрес: {settings.CLUB_ADDRESS}\n"
    )
    
    if settings.CLUB_PHONE:
        info_text += f"📞 Телефон: {settings.CLUB_PHONE}\n"
    
    if settings.CLUB_EMAIL:
        info_text += f"📧 Email: {settings.CLUB_EMAIL}\n"
    
    info_text += "\n🎉 Лучшие вечеринки каждую неделю!"
    
    await safe_edit_message(
        callback,
        info_text,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_support")
async def handle_support(callback: CallbackQuery, state: FSMContext):
    """Handle 'Support' button - request message from user."""
    support_text = (
        "💬 <b>Поддержка</b>\n\n"
        "Напишите ваше сообщение в поддержку, и мы обязательно ответим.\n\n"
        "Просто отправьте текст вашего сообщения:"
    )
    
    await safe_edit_message(
        callback,
        support_text,
        reply_markup=get_support_cancel_keyboard()
    )
    await callback.answer()
    
    # Set state to wait for support message
    await state.set_state(SupportStates.waiting_message)


@router.callback_query(F.data == "cancel_support")
async def handle_cancel_support(callback: CallbackQuery, state: FSMContext):
    """Handle cancel support message."""
    await state.clear()
    
    menu_text = (
        f"👋 <b>{settings.CLUB_NAME}</b>\n\n"
        "Выберите действие:"
    )
    
    await safe_edit_message(
        callback,
        menu_text,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer("Отменено")


@router.message(SupportStates.waiting_message, F.text)
async def handle_support_message(message: Message, state: FSMContext):
    """Handle support message from user."""
    support_message = message.text
    
    # TODO: Send message to support/admin
    # For now, just confirm receipt
    
    # This message is NOT temporary - it's feedback, should remain
    # Don't delete it - it's not a temporary message
    
    confirmation_text = (
        "✅ <b>Сообщение получено</b>\n\n"
        "Ваше сообщение отправлено в поддержку. Мы свяжемся с вами в ближайшее время.\n\n"
        "Выберите действие:"
    )
    
    # Send confirmation (don't delete user's message - it's feedback, not temporary)
    await message.answer(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    
    await state.clear()
