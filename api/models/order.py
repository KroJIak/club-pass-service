"""Order ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from api.core.db import Base


class Order(Base):
    """Order model - stores order details before payment."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, nullable=False, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="orders")
    event = relationship("Event", backref="orders")
    ticket_type = relationship("TicketType", backref="orders")
    payment = relationship("Payment", backref="order")

