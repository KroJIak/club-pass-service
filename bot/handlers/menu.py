"""Main menu handlers."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import get_main_menu_keyboard

router = Router()


@router.message(F.text == "🎫 Купить билет")
async def handle_buy_ticket(message: Message, state: FSMContext):
    """Handle 'Buy ticket' button."""
    # TODO: Implement purchase flow
    await message.answer(
        "🚧 Функция покупки билетов находится в разработке.\n"
        "Скоро здесь можно будет купить билеты на вечеринки!",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "🎟️ Мои билеты")
async def handle_my_tickets(message: Message):
    """Handle 'My tickets' button."""
    # TODO: Implement tickets view
    await message.answer(
        "🚧 Функция просмотра билетов находится в разработке.\n"
        "Скоро здесь можно будет посмотреть все ваши билеты!",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "🎉 Ближайшие вечеринки")
async def handle_upcoming_events(message: Message):
    """Handle 'Upcoming events' button."""
    # TODO: Implement events list
    await message.answer(
        "🚧 Функция просмотра событий находится в разработке.\n"
        "Скоро здесь можно будет посмотреть все предстоящие вечеринки!",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "ℹ️ Инфо о клубе")
async def handle_club_info(message: Message):
    """Handle 'Club info' button."""
    from bot.core.config import settings
    
    info_text = (
        f"<b>{settings.CLUB_NAME}</b>\n\n"
        f"📍 Адрес: {settings.CLUB_ADDRESS}\n"
    )
    
    if settings.CLUB_PHONE:
        info_text += f"📞 Телефон: {settings.CLUB_PHONE}\n"
    
    if settings.CLUB_EMAIL:
        info_text += f"📧 Email: {settings.CLUB_EMAIL}\n"
    
    info_text += "\n🎉 Лучшие вечеринки каждую неделю!"
    
    await message.answer(info_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.message(F.text == "💬 Поддержка")
async def handle_support(message: Message):
    """Handle 'Support' button."""
    from bot.core.config import settings
    
    support_text = "💬 <b>Поддержка</b>\n\n"
    
    if settings.SUPPORT_USERNAME:
        support_text += f"Telegram: @{settings.SUPPORT_USERNAME}\n"
    
    if settings.SUPPORT_PHONE:
        support_text += f"Телефон: {settings.SUPPORT_PHONE}\n"
    
    if not settings.SUPPORT_USERNAME and not settings.SUPPORT_PHONE:
        support_text += "Свяжитесь с нами через администратора клуба."
    
    await message.answer(support_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Handle back to menu callback."""
    await state.clear()
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=None
    )
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
