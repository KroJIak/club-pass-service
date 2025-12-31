"""Repository for support messages."""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from api.models.support_message import SupportMessage, SupportMessageStatus


class SupportMessageRepository:
    """Repository for support message operations."""
    
    @staticmethod
    def get_all(
        db: Session,
        status: Optional[SupportMessageStatus] = None,
        user_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> List[SupportMessage]:
        """Get all support messages with optional filters."""
        query = db.query(SupportMessage)
        
        if status:
            query = query.filter(SupportMessage.status == status)
        
        if user_id:
            query = query.filter(SupportMessage.user_id == user_id)
        
        if date_from:
            query = query.filter(SupportMessage.created_at >= date_from)
        
        if date_to:
            # Add one day to include the entire end date
            date_to_end = datetime.combine(date_to.date(), datetime.max.time()) if hasattr(date_to, 'date') else date_to
            query = query.filter(SupportMessage.created_at <= date_to_end)
        
        if search:
            search_lower = search.lower()
            query = query.filter(
                or_(
                    func.lower(SupportMessage.message).contains(search_lower),
                    func.lower(SupportMessage.admin_response).contains(search_lower)
                )
            )
        
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

