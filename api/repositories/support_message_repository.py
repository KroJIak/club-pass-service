"""Repository for support messages."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from api.models.support_message import SupportMessage, SupportMessageStatus


class SupportMessageRepository:
    """Repository for support message operations."""
    
    @staticmethod
    def get_all(db: Session, status: Optional[SupportMessageStatus] = None) -> List[SupportMessage]:
        """Get all support messages, optionally filtered by status."""
        query = db.query(SupportMessage)
        if status:
            query = query.filter(SupportMessage.status == status)
        return query.order_by(SupportMessage.created_at.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, message_id: int) -> Optional[SupportMessage]:
        """Get a support message by ID."""
        return db.query(SupportMessage).filter(SupportMessage.id == message_id).first()
    
    @staticmethod
    def create(db: Session, user_id: int, message: str) -> SupportMessage:
        """Create a new support message."""
        support_message = SupportMessage(
            user_id=user_id,
            message=message,
            status=SupportMessageStatus.NEW,
        )
        db.add(support_message)
        db.commit()
        db.refresh(support_message)
        return support_message
    
    @staticmethod
    def update(db: Session, message_id: int, status: Optional[SupportMessageStatus] = None, 
               admin_response: Optional[str] = None, responded_by: Optional[str] = None) -> Optional[SupportMessage]:
        """Update a support message."""
        support_message = db.query(SupportMessage).filter(SupportMessage.id == message_id).first()
        if not support_message:
            return None
        
        if status is not None:
            support_message.status = status
        if admin_response is not None:
            support_message.admin_response = admin_response
            if admin_response and not support_message.responded_at:
                support_message.responded_at = datetime.utcnow()
        if responded_by is not None:
            support_message.responded_by = responded_by
        
        db.commit()
        db.refresh(support_message)
        return support_message
    
    @staticmethod
    def delete(db: Session, message_id: int) -> bool:
        """Delete a support message."""
        support_message = db.query(SupportMessage).filter(SupportMessage.id == message_id).first()
        if not support_message:
            return False
        db.delete(support_message)
        db.commit()
        return True

