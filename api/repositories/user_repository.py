"""User repository."""
from typing import Optional
from sqlalchemy.orm import Session
from api.models.user import User
from api.api.v1.schemas import UserCreate


class UserRepository:
    """Repository for user operations."""
    
    @staticmethod
    def get_by_telegram_id(db: Session, telegram_user_id: int) -> Optional[User]:
        """Get user by Telegram user ID."""
        return db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
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
    
    @staticmethod
    def get_or_create(db: Session, user_data: UserCreate) -> User:
        """Get existing user or create a new one."""
        user = UserRepository.get_by_telegram_id(db, user_data.telegram_user_id)
        if user:
            # Update user info if provided
            updated = False
            if user_data.username is not None:
                user.username = user_data.username
                updated = True
            if user_data.first_name is not None:
                user.first_name = user_data.first_name
                updated = True
            if user_data.last_name is not None:
                user.last_name = user_data.last_name
                updated = True
            if updated:
                from datetime import datetime
                user.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(user)
            return user
        return UserRepository.create(db, user_data)
