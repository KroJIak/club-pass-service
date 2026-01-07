"""Admin account repository."""
from typing import Optional, List
from sqlalchemy.orm import Session
from api.models.admin_account import AdminAccount


class AdminAccountRepository:
    """Repository for admin account operations."""
    
    @staticmethod
    def get_by_id(db: Session, account_id: int) -> Optional[AdminAccount]:
        """Get account by ID."""
        return db.query(AdminAccount).filter(
            AdminAccount.id == account_id,
            AdminAccount.is_deleted == False
        ).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[AdminAccount]:
        """Get account by username."""
        return db.query(AdminAccount).filter(
            AdminAccount.username == username,
            AdminAccount.is_deleted == False
        ).first()
    
    @staticmethod
    def get_all(db: Session) -> List[AdminAccount]:
        """Get all accounts."""
        return db.query(AdminAccount).filter(
            AdminAccount.is_deleted == False
        ).order_by(AdminAccount.created_at.desc()).all()
    
    @staticmethod
    def get_by_group(db: Session, group_id: int) -> List[AdminAccount]:
        """Get all accounts in a group."""
        return db.query(AdminAccount).filter(
            AdminAccount.group_id == group_id,
            AdminAccount.is_deleted == False
        ).order_by(AdminAccount.created_at.desc()).all()
    
    @staticmethod
    def create(db: Session, group_id: int, username: str, password_hash: str, is_active: bool = True) -> AdminAccount:
        """Create a new account."""
        account = AdminAccount(
            group_id=group_id,
            username=username,
            password_hash=password_hash,
            is_active=is_active
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def update(db: Session, account_id: int, group_id: Optional[int] = None, username: Optional[str] = None, 
               password_hash: Optional[str] = None, is_active: Optional[bool] = None, language: Optional[str] = None) -> Optional[AdminAccount]:
        """Update account."""
        account = AdminAccountRepository.get_by_id(db, account_id)
        if not account:
            return None
        
        if group_id is not None:
            account.group_id = group_id
        if username is not None:
            account.username = username
        if password_hash is not None:
            account.password_hash = password_hash
        if is_active is not None:
            account.is_active = is_active
        if language is not None:
            account.language = language
        
        db.commit()
        db.refresh(account)
        return account
    
    @staticmethod
    def delete(db: Session, account_id: int, hard: bool = False) -> bool:
        """Delete account (soft delete by default)."""
        account = AdminAccountRepository.get_by_id(db, account_id)
        if not account:
            return False
        
        if hard:
            db.delete(account)
        else:
            from datetime import datetime
            account.is_deleted = True
            account.deleted_at = datetime.utcnow()
        
        db.commit()
        return True

