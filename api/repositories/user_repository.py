"""User repository."""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from api.models.user import User
from api.api.v1.schemas import UserCreate, UserUpdate


class UserRepository:
    """Repository for user operations."""
    
    @staticmethod
    def get_by_telegram_id(db: Session, telegram_user_id: int) -> Optional[User]:
        """Get user by Telegram user ID."""
        return db.query(User).filter(
            User.telegram_user_id == telegram_user_id,
            User.is_deleted == False
        ).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
    
    @staticmethod
    def get_all(db: Session) -> List[User]:
        """Get all users."""
        return db.query(User).filter(User.is_deleted == False).order_by(User.created_at.desc()).all()
    
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            user = User(
                telegram_user_id=user_data.telegram_user_id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def update(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        
        updated = False
        if user_data.username is not None and user.username != user_data.username:
            user.username = user_data.username
            updated = True
        if user_data.first_name is not None and user.first_name != user_data.first_name:
            user.first_name = user_data.first_name
            updated = True
        if user_data.last_name is not None and user.last_name != user_data.last_name:
            user.last_name = user_data.last_name
            updated = True
        
        if updated:
            # Don't manually set updated_at - let SQLAlchemy handle it via onupdate
            db.commit()
            db.refresh(user)
        
        return user
    
    @staticmethod
    def soft_delete(db: Session, user_id: int) -> bool:
        """Soft delete a user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user or user.is_deleted:
            return False
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, user_id: int, hard: bool = False) -> bool:
        """Delete a user."""
        if not hard:
            return UserRepository.soft_delete(db, user_id)
        
        from api.models.payment import Payment
        from api.models.ticket import Ticket
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Explicitly delete related tickets first to avoid constraint violations
        # Tickets have CASCADE, but SQLAlchemy may try to set user_id to NULL which violates NOT NULL
        tickets = db.query(Ticket).filter(Ticket.user_id == user_id).all()
        for ticket in tickets:
            db.delete(ticket)
        
        # Explicitly delete related payments first to avoid constraint violations
        # Payments have CASCADE, but SQLAlchemy may not handle it correctly
        payments = db.query(Payment).filter(Payment.user_id == user_id).all()
        for payment in payments:
            db.delete(payment)
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def get_or_create(db: Session, user_data: UserCreate) -> User:
        """Get existing user or create a new one."""
        try:
            # Check for existing user including deleted ones for get_or_create
            user = db.query(User).filter(User.telegram_user_id == user_data.telegram_user_id).first()
            if user and not user.is_deleted:
                # Update user info if provided
                updated = False
                if user_data.username is not None and user.username != user_data.username:
                    user.username = user_data.username
                    updated = True
                if user_data.first_name is not None and user.first_name != user_data.first_name:
                    user.first_name = user_data.first_name
                    updated = True
                if user_data.last_name is not None and user.last_name != user_data.last_name:
                    user.last_name = user_data.last_name
                    updated = True
                if updated:
                    # Don't manually set updated_at - let SQLAlchemy handle it via onupdate
                    db.commit()
                    db.refresh(user)
                return user
            return UserRepository.create(db, user_data)
        except Exception as e:
            db.rollback()
            raise
