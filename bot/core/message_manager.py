"""Message formatting and management."""
from typing import Dict, Any


def format_event_message(event: Dict[str, Any]) -> str:
    """Format event information message."""
    return (
        f"🎉 <b>{event.get('name', 'Событие')}</b>\n\n"
        f"📅 Дата: {event.get('date', 'Не указано')}\n"
        f"🕐 Время: {event.get('time', 'Не указано')}\n"
        f"📍 Место: {event.get('location', 'Не указано')}\n\n"
        f"{event.get('description', '')}"
    )


def format_ticket_info(ticket: Dict[str, Any]) -> str:
    """Format ticket information message."""
    return (
        f"🎫 <b>Билет #{ticket.get('id', 'N/A')}</b>\n\n"
        f"🎉 Событие: {ticket.get('event_name', 'Не указано')}\n"
        f"📅 Дата: {ticket.get('date', 'Не указано')}\n"
        f"🎟️ Тип: {ticket.get('ticket_type', 'Не указано')}\n"
        f"🔑 Код: <code>{ticket.get('code', 'N/A')}</code>"
    )


def format_order_summary(order: Dict[str, Any]) -> str:
    """Format order summary message."""
    return (
        f"📋 <b>Подтверждение заказа</b>\n\n"
        f"🎉 Событие: {order.get('event_name', 'Не указано')}\n"
        f"🎟️ Тип билета: {order.get('ticket_type_name', 'Не указано')}\n"
        f"🔢 Количество: {order.get('quantity', 0)}\n"
        f"💰 Сумма: {order.get('total_amount', 0)} ₽"
    )
