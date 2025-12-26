"""Repository for ticket type templates."""
from sqlalchemy.orm import Session
from api.models.ticket_type_template import TicketTypeTemplate


class TicketTypeTemplateRepository:
    """Repository for ticket type template operations."""
    
    @staticmethod
    def get_all(db: Session) -> list[TicketTypeTemplate]:
        """Get all ticket type templates."""
        return db.query(TicketTypeTemplate).all()
    
    @staticmethod
    def get_by_id(db: Session, template_id: int) -> TicketTypeTemplate | None:
        """Get a ticket type template by ID."""
        return db.query(TicketTypeTemplate).filter(TicketTypeTemplate.id == template_id).first()
    
    @staticmethod
    def create(db: Session, name: str, price: float, available_quantity: int, total_quantity: int, is_active: bool = True) -> TicketTypeTemplate:
        """Create a new ticket type template."""
        template = TicketTypeTemplate(
            name=name,
            price=price,
            available_quantity=available_quantity,
            total_quantity=total_quantity,
            is_active=is_active,
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def delete(db: Session, template_id: int) -> bool:
        """Delete a ticket type template."""
        template = db.query(TicketTypeTemplate).filter(TicketTypeTemplate.id == template_id).first()
        if not template:
            return False
        db.delete(template)
        db.commit()
        return True

