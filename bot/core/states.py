"""FSM states for bot."""
from aiogram.fsm.state import State, StatesGroup


class PurchaseStates(StatesGroup):
    """States for ticket purchase flow."""
    selecting_event = State()  # Выбор события
    selecting_ticket_type = State()  # Выбор типа билета
    selecting_quantity = State()  # Выбор количества
    confirming_order = State()  # Подтверждение заказа
    processing_payment = State()  # Обработка оплаты


class SupportStates(StatesGroup):
    """States for support flow."""
    waiting_message = State()  # Ожидание сообщения от пользователя


class MusicStates(StatesGroup):
    """States for music request flow."""
    waiting_title = State()  # Ожидание названия песни
