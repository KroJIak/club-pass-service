"""Order repository."""
from typing import Optional
from sqlalchemy.orm import Session
import uuid
from api.models.order import Order


class OrderRepository:
    """Repository for order operations."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
        quantity: int,
        promocode: Optional[str] = None,
    ) -> Order:
        """Create a new order."""
        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            user_id=user_id,
            event_id=event_id,
            ticket_type_id=ticket_type_id,
            quantity=quantity,
            promocode=promocode,
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_by_order_id(db: Session, order_id: str) -> Optional[Order]:
        """Get order by order_id."""
        return db.query(Order).filter(Order.order_id == order_id).first()
    
    @staticmethod
    def link_payment(db: Session, order_id: str, payment_id: int) -> Optional[Order]:
        """Link payment to order."""
        order = OrderRepository.get_by_order_id(db, order_id)
        if order:
            order.payment_id = payment_id
            db.commit()
            db.refresh(order)
        return order

