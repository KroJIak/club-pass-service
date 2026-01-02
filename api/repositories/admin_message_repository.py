"""Repository for admin messages."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from api.models.admin_message import AdminMessage


class AdminMessageRepository:
    """Repository for admin message operations."""
    
    @staticmethod
    def get_all(
        db: Session,
        user_id: Optional[int] = None,
        sent_by: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[AdminMessage]:
        """Get all admin messages with optional filters."""
        query = db.query(AdminMessage)
        
        if user_id:
            query = query.filter(AdminMessage.user_id == user_id)
        
        if sent_by:
            query = query.filter(AdminMessage.sent_by == sent_by)
        
        if date_from:
            query = query.filter(AdminMessage.created_at >= date_from)
        
        if date_to:
            # Add one day to include the entire end date
            date_to_end = datetime.combine(date_to.date(), datetime.max.time()) if hasattr(date_to, 'date') else date_to
            query = query.filter(AdminMessage.created_at <= date_to_end)
        
        query = query.order_by(AdminMessage.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def count(
        db: Session,
        user_id: Optional[int] = None,
        sent_by: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> int:
        """Count admin messages with optional filters."""
        query = db.query(AdminMessage)
        
        if user_id:
            query = query.filter(AdminMessage.user_id == user_id)
        
        if sent_by:
            query = query.filter(AdminMessage.sent_by == sent_by)
        
        if date_from:
            query = query.filter(AdminMessage.created_at >= date_from)
        
        if date_to:
            date_to_end = datetime.combine(date_to.date(), datetime.max.time()) if hasattr(date_to, 'date') else date_to
            query = query.filter(AdminMessage.created_at <= date_to_end)
        
        return query.count()
    
    @staticmethod
    def get_by_id(db: Session, message_id: int) -> Optional[AdminMessage]:
        """Get an admin message by ID."""
        return db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        message: Optional[str],
        sent_by: str,
    ) -> AdminMessage:
        """Create a new admin message."""
        admin_message = AdminMessage(
            user_id=user_id,
            message=message,
            sent_by=sent_by,
        )
        db.add(admin_message)
        db.commit()
        db.refresh(admin_message)
        return admin_message
    
    @staticmethod
    def delete(db: Session, message_id: int) -> bool:
        """Delete an admin message."""
        admin_message = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
        if not admin_message:
            return False
        db.delete(admin_message)
        db.commit()
        return True

