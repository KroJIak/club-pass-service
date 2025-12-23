"""Promocode repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.promocode import Promocode


class PromocodeRepository:
    """Repository for promocode operations."""
    
    @staticmethod
    def get_all(db: Session) -> List[Promocode]:
        """Get all promocodes."""
        return db.query(Promocode).order_by(Promocode.created_at.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, promocode_id: int) -> Optional[Promocode]:
        """Get promocode by ID."""
        return db.query(Promocode).filter(Promocode.id == promocode_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Promocode]:
        """Get promocode by code."""
        return db.query(Promocode).filter(Promocode.code == code).first()
    
    @staticmethod
    def create(
        db: Session,
        code: str,
        discount_percent: Optional[float] = None,
        discount_amount: Optional[float] = None,
        valid_from = None,
        valid_until = None,
        usage_limit: Optional[int] = None,
        is_active: bool = True,
    ) -> Promocode:
        """Create a new promocode."""
        promocode = Promocode(
            code=code,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            valid_from=valid_from,
            valid_until=valid_until,
            usage_limit=usage_limit,
            is_active=is_active,
        )
        db.add(promocode)
        db.commit()
        db.refresh(promocode)
        return promocode
    
    @staticmethod
    def update(
        db: Session,
        promocode_id: int,
        code: Optional[str] = None,
        discount_percent: Optional[float] = None,
        discount_amount: Optional[float] = None,
        valid_from = None,
        valid_until = None,
        usage_limit: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Promocode]:
        """Update a promocode."""
        promocode = PromocodeRepository.get_by_id(db, promocode_id)
        if not promocode:
            return None
        
        if code is not None:
            promocode.code = code
        if discount_percent is not None:
            promocode.discount_percent = discount_percent
        if discount_amount is not None:
            promocode.discount_amount = discount_amount
        if valid_from is not None:
            promocode.valid_from = valid_from
        if valid_until is not None:
            promocode.valid_until = valid_until
        if usage_limit is not None:
            promocode.usage_limit = usage_limit
        if is_active is not None:
            promocode.is_active = is_active
        
        db.commit()
        db.refresh(promocode)
        return promocode
    
    @staticmethod
    def delete(db: Session, promocode_id: int) -> bool:
        """Delete a promocode (soft delete by setting is_active=False)."""
        promocode = PromocodeRepository.get_by_id(db, promocode_id)
        if not promocode:
            return False
        
        promocode.is_active = False
        db.commit()
        return True

