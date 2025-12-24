"""Order repository."""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
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
    
    @staticmethod
    def get_all(db: Session) -> List[Order]:
        """Get all orders."""
        return db.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.event),
            joinedload(Order.ticket_type),
            joinedload(Order.payment)
        ).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Get order by internal ID."""
        return db.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.event),
            joinedload(Order.ticket_type),
            joinedload(Order.payment)
        ).filter(Order.id == order_id).first()
    
    @staticmethod
    def delete(db: Session, order_id: int) -> bool:
        """Delete an order by its internal ID."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            db.delete(order)
            db.commit()
            return True
        return False

