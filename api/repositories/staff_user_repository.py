"""Staff User repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.staff_user import StaffUser


class StaffUserRepository:
    """Repository for staff user operations."""
    
    @staticmethod
    def get_by_telegram_id(db: Session, telegram_user_id: int) -> Optional[StaffUser]:
        """Get staff user by Telegram user ID."""
        return db.query(StaffUser).filter(
            StaffUser.telegram_user_id == telegram_user_id
        ).first()
    
    @staticmethod
    def get_all(db: Session) -> List[StaffUser]:
        """Get all staff users."""
        return db.query(StaffUser).order_by(StaffUser.created_at.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, staff_user_id: int) -> Optional[StaffUser]:
        """Get staff user by ID."""
        return db.query(StaffUser).filter(StaffUser.id == staff_user_id).first()
    
    @staticmethod
    def create(
        db: Session,
        telegram_user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> StaffUser:
        """Create a new staff user."""
        staff_user = StaffUser(
            telegram_user_id=telegram_user_id,
            first_name=first_name,
            last_name=last_name,
        )
        db.add(staff_user)
        db.commit()
        db.refresh(staff_user)
        return staff_user
    
    @staticmethod
    def update(
        db: Session,
        staff_user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[StaffUser]:
        """Update a staff user."""
        staff_user = StaffUserRepository.get_by_id(db, staff_user_id)
        if not staff_user:
            return None
        
        if first_name is not None:
            staff_user.first_name = first_name
        if last_name is not None:
            staff_user.last_name = last_name
        
        db.commit()
        db.refresh(staff_user)
        return staff_user
    
    @staticmethod
    def delete(db: Session, staff_user_id: int) -> bool:
        """Delete a staff user."""
        staff_user = StaffUserRepository.get_by_id(db, staff_user_id)
        if not staff_user:
            return False
        db.delete(staff_user)
        db.commit()
        return True

