"""Keyboards for staff bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.config import settings


def get_mini_app_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with mini app button."""
    from aiogram.types import WebAppInfo
    
    builder = InlineKeyboardBuilder()
    
    if settings.MINI_APP_URL:
        builder.add(InlineKeyboardButton(
            text="📱 Открыть приложение",
            web_app=WebAppInfo(url=settings.MINI_APP_URL)
        ))
    
    return builder.as_markup()

