"""Payment repository."""
from typing import Optional, List
from sqlalchemy.orm import Session
from api.models.payment import Payment, PaymentStatus
from decimal import Decimal
import uuid


class PaymentRepository:
    """Repository for payment operations."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        amount: Decimal,
        order_id: Optional[str] = None,
    ) -> Payment:
        """Create a new payment."""
        if not order_id:
            order_id = str(uuid.uuid4())
        
        payment = Payment(
            user_id=user_id,
            order_id=order_id,
            amount=amount,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_all(db: Session) -> List[Payment]:
        """Get all payments."""
        from sqlalchemy.orm import joinedload
        return db.query(Payment).options(
            joinedload(Payment.user)
        ).order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, payment_id: int) -> Optional[Payment]:
        """Get payment by ID."""
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    @staticmethod
    def get_by_order_id(db: Session, order_id: str) -> Optional[Payment]:
        """Get payment by order ID."""
        return db.query(Payment).filter(Payment.order_id == order_id).first()
    
    @staticmethod
    def get_by_yookassa_payment_id(db: Session, yookassa_payment_id: str) -> Optional[Payment]:
        """Get payment by YooKassa payment ID."""
        return db.query(Payment).filter(Payment.yookassa_payment_id == yookassa_payment_id).first()
    
    @staticmethod
    def update_status(
        db: Session,
        payment_id: int,
        status: PaymentStatus,
        telegram_payment_charge_id: Optional[str] = None,
        yookassa_payment_id: Optional[str] = None,
    ) -> Optional[Payment]:
        """Update payment status."""
        payment = PaymentRepository.get_by_id(db, payment_id)
        if not payment:
            return None
        
        payment.status = status
        if telegram_payment_charge_id:
            payment.telegram_payment_charge_id = telegram_payment_charge_id
        if yookassa_payment_id:
            payment.yookassa_payment_id = yookassa_payment_id
        
        db.commit()
        db.refresh(payment)
        return payment
