"""Payments endpoints and YooKassa webhooks."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.core.db import get_db
from api.services.payment_service import PaymentService
from api.repositories.user_repository import UserRepository
from api.api.v1.schemas import OrderCreate, OrderResponse, UserCreate
from api.core.config import settings

router = APIRouter()


class ProcessPaymentRequest(BaseModel):
    """Request schema for processing payment."""
    order_id: str
    telegram_payment_charge_id: str


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    """Create an order and prepare payment invoice."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creating order: user_id={order_data.user_id}, event_id={order_data.event_id}, ticket_type_id={order_data.ticket_type_id}, quantity={order_data.quantity}")
        
        # Get or create user
        user_data = UserCreate(
            telegram_user_id=order_data.user_id,
            username=order_data.username,
            first_name=order_data.first_name,
            last_name=order_data.last_name,
        )
        user = UserRepository.get_or_create(db, user_data)
        logger.info(f"User found/created: id={user.id}, telegram_user_id={user.telegram_user_id}")
        
        # Create payment invoice
        invoice_data = PaymentService.create_payment_invoice(
            db=db,
            user_id=user.id,
            event_id=order_data.event_id,
            ticket_type_id=order_data.ticket_type_id,
            quantity=order_data.quantity,
        )
        logger.info(f"Payment invoice created: order_id={invoice_data['order_id']}, payment_id={invoice_data['payment_id']}")
        
        return OrderResponse(**invoice_data)
    except ValueError as e:
        logger.error(f"Validation error creating payment invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating payment invoice: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/payments/process")
async def process_payment(
    payment_data: ProcessPaymentRequest,
    db: Session = Depends(get_db),
):
    """Process successful payment and create tickets."""
    try:
        result = PaymentService.handle_payment_success(
            db=db,
            order_id=payment_data.order_id,
            telegram_payment_charge_id=payment_data.telegram_payment_charge_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/orders/{order_id}/complete-mock")
async def complete_order_mock(
    order_id: str,
    db: Session = Depends(get_db),
):
    """Mock payment completion - creates tickets without real payment (for testing)."""
    try:
        result = PaymentService.handle_payment_success(
            db=db,
            order_id=order_id,
            telegram_payment_charge_id="MOCK_PAYMENT_" + order_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
