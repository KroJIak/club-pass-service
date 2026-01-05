"""Repository for ticket type templates."""
from sqlalchemy.orm import Session
from api.models.ticket_type_template import TicketTypeTemplate


class TicketTypeTemplateRepository:
    """Repository for ticket type template operations."""
    
    @staticmethod
    def get_all(db: Session) -> list[TicketTypeTemplate]:
        """Get all ticket type templates."""
        return db.query(TicketTypeTemplate).filter(TicketTypeTemplate.is_deleted == False).all()
    
    @staticmethod
    def get_by_id(db: Session, template_id: int) -> TicketTypeTemplate | None:
        """Get a ticket type template by ID."""
        return db.query(TicketTypeTemplate).filter(
            TicketTypeTemplate.id == template_id,
            TicketTypeTemplate.is_deleted == False
        ).first()
    
    @staticmethod
    def create(db: Session, name: str, price: float, available_quantity: int, total_quantity: int) -> TicketTypeTemplate:
        """Create a new ticket type template."""
        template = TicketTypeTemplate(
            name=name,
            price=price,
            available_quantity=available_quantity,
            total_quantity=total_quantity,
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def soft_delete(db: Session, template_id: int) -> bool:
        """Soft delete a ticket type template."""
        from datetime import datetime
        template = TicketTypeTemplateRepository.get_by_id(db, template_id)
        if not template or template.is_deleted:
            return False
        template.is_deleted = True
        template.deleted_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, template_id: int, hard: bool = False) -> bool:
        """Delete a ticket type template."""
        if not hard:
            return TicketTypeTemplateRepository.soft_delete(db, template_id)
        
        template = db.query(TicketTypeTemplate).filter(TicketTypeTemplate.id == template_id).first()
        if not template:
            return False
        db.delete(template)
        db.commit()
        return True

