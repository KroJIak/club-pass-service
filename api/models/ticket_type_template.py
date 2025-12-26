"""TicketTypeTemplate ORM model."""
from sqlalchemy import Column, Integer, String, Numeric
from api.core.db import Base


class TicketTypeTemplate(Base):
    """Ticket type template model."""
    __tablename__ = "ticket_type_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    total_quantity = Column(Integer, default=0, nullable=False)

