"""Payment and YooKassa integration service."""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid

from api.core.config import settings
from api.repositories.payment_repository import PaymentRepository
from api.repositories.user_repository import UserRepository
from api.repositories.event_repository import EventRepository
from api.repositories.ticket_type_repository import TicketTypeRepository
from api.repositories.ticket_repository import TicketRepository
from api.repositories.order_repository import OrderRepository
from api.models.payment import PaymentStatus
from api.services.ticket_service import TicketService


class PaymentService:
    """Service for payment operations."""
    
    @staticmethod
    def create_payment_invoice(
        db: Session,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
        quantity: int,
        promocode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create payment and prepare invoice data for Telegram sendInvoice.
        
        Args:
            db: Database session
            user_id: User ID
            event_id: Event ID
            ticket_type_id: Ticket type ID
            quantity: Quantity of tickets
            promocode: Optional promocode
        
        Returns:
            Dictionary with invoice data for sendInvoice
        
        Raises:
            ValueError: If event, ticket type not found or not enough availability
        """
        # Validate event
        event = EventRepository.get_active_by_id(db, event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found or not active")
        
        # Validate ticket type
        ticket_type = TicketTypeRepository.get_active_by_id(db, ticket_type_id)
        if not ticket_type:
            raise ValueError(f"Ticket type with id {ticket_type_id} not found or not active")
        
        if ticket_type.event_id != event_id:
            raise ValueError(f"Ticket type {ticket_type_id} does not belong to event {event_id}")
        
        # Check availability
        if not TicketTypeRepository.check_availability(db, ticket_type_id, quantity):
            raise ValueError(f"Not enough tickets available (requested: {quantity}, available: {ticket_type.available_quantity})")
        
        # Calculate total amount
        total_amount = ticket_type.price * quantity
        
        # Apply promocode discount if provided
        # TODO: Implement promocode logic
        if promocode:
            # For now, skip promocode
            pass
        
        # Create order record
        order = OrderRepository.create(
            db=db,
            user_id=user_id,
            event_id=event_id,
            ticket_type_id=ticket_type_id,
            quantity=quantity,
            promocode=promocode,
        )
        
        # Create payment record
        payment = PaymentRepository.create(
            db=db,
            user_id=user_id,
            amount=total_amount,
            order_id=order.order_id,
        )
        
        # Link payment to order
        OrderRepository.link_payment(db, order.order_id, payment.id)
        
        # Format event info for invoice
        djs_text = ", ".join(event.djs) if event.djs else event.name
        event_info = f"{djs_text}\n{event.date} {event.time}"
        
        # Prepare invoice data
        invoice_title = f"Билеты: {ticket_type.name}"
        invoice_description = (
            f"🎫 {ticket_type.name}\n"
            f"🎉 {event_info}\n"
            f"🔢 Количество: {quantity}\n"
            f"💰 Сумма: {total_amount} ₽"
        )
        
        # Invoice payload (will be used to identify payment in webhook)
        invoice_payload = f"order_{order.order_id}"
        
        # Prices for invoice (in kopecks)
        prices = [
            {
                "label": f"{ticket_type.name} x{quantity}",
                "amount": int(total_amount * 100)  # Convert to kopecks
            }
        ]
        
        # Provider token from BotFather (after connecting bot to YooKassa)
        # For now, we'll need to get it from settings or use bot token
        # According to docs, provider_token is obtained from BotFather
        provider_token = settings.YOOKASSA_SECRET_KEY or settings.TELEGRAM_BOT_TOKEN
        
        if not provider_token:
            raise ValueError("Provider token not configured. Please set YOOKASSA_SECRET_KEY or TELEGRAM_BOT_TOKEN")
        
        return {
            "order_id": order.order_id,
            "payment_id": payment.id,
            "amount": total_amount,
            "invoice_title": invoice_title,
            "invoice_description": invoice_description,
            "invoice_payload": invoice_payload,
            "invoice_prices": prices,
            "provider_token": provider_token,
        }
    
    @staticmethod
    def handle_payment_success(
        db: Session,
        order_id: str,
        telegram_payment_charge_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handle successful payment - create tickets.
        
        Args:
            db: Database session
            order_id: Order ID from invoice payload
            telegram_payment_charge_id: Telegram payment charge ID
        
        Returns:
            Dictionary with created tickets info
        
        Raises:
            ValueError: If payment not found or already processed
        """
        # Extract order_id from payload (format: "order_{uuid}")
        if order_id.startswith("order_"):
            order_id = order_id.replace("order_", "")
        
        # Get payment by order_id
        payment = PaymentRepository.get_by_order_id(db, order_id)
        if not payment:
            raise ValueError(f"Payment with order_id {order_id} not found")
        
        if payment.status == PaymentStatus.SUCCEEDED:
            # Already processed, return existing tickets
            tickets = TicketRepository.get_by_user_id(db, payment.user_id)
            return {
                "payment_id": payment.id,
                "tickets_created": len([t for t in tickets if t.created_at >= payment.created_at]),
                "message": "Payment already processed"
            }
        
        # Update payment status
        PaymentRepository.update_status(
            db,
            payment.id,
            PaymentStatus.SUCCEEDED,
            telegram_payment_charge_id=telegram_payment_charge_id,
        )
        
        # Get order details
        order = OrderRepository.get_by_order_id(db, order_id)
        if not order:
            raise ValueError(f"Order with id {order_id} not found")
        
        # Create tickets
        tickets = TicketService.create_tickets_for_order(
            db=db,
            user_id=payment.user_id,
            event_id=order.event_id,
            ticket_type_id=order.ticket_type_id,
            quantity=order.quantity,
        )
        
        return {
            "payment_id": payment.id,
            "order_id": order_id,
            "tickets_created": len(tickets),
            "ticket_ids": [t.id for t in tickets],
            "status": "succeeded",
            "message": "Payment processed successfully and tickets created"
        }
    
    @staticmethod
    def handle_payment_failure(
        db: Session,
        order_id: str,
    ) -> None:
        """
        Handle failed payment.
        
        Args:
            db: Database session
            order_id: Order ID
        """
        if order_id.startswith("order_"):
            order_id = order_id.replace("order_", "")
        
        payment = PaymentRepository.get_by_order_id(db, order_id)
        if payment and payment.status == PaymentStatus.PENDING:
            PaymentRepository.update_status(
                db,
                payment.id,
                PaymentStatus.CANCELLED,
            )
