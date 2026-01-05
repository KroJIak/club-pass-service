"""Repository for menu photos."""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from api.models.menu_photo import MenuPhoto


class MenuPhotoRepository:
    """Repository for menu photo operations."""
    
    @staticmethod
    def get_all(db: Session) -> List[MenuPhoto]:
        """Get all menu photos, sorted by display_order."""
        return db.query(MenuPhoto).filter(
            MenuPhoto.is_deleted == False
        ).order_by(MenuPhoto.display_order.asc()).all()
    
    @staticmethod
    def get_by_id(db: Session, photo_id: int) -> Optional[MenuPhoto]:
        """Get a menu photo by ID."""
        return db.query(MenuPhoto).filter(
            MenuPhoto.id == photo_id,
            MenuPhoto.is_deleted == False
        ).first()
    
    @staticmethod
    def create(
        db: Session,
        file_path: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        display_order: int,
    ) -> MenuPhoto:
        """Create a new menu photo."""
        menu_photo = MenuPhoto(
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            display_order=display_order,
        )
        db.add(menu_photo)
        db.commit()
        db.refresh(menu_photo)
        return menu_photo
    
    @staticmethod
    def soft_delete(db: Session, photo_id: int) -> bool:
        """Soft delete a menu photo."""
        menu_photo = MenuPhotoRepository.get_by_id(db, photo_id)
        if not menu_photo or menu_photo.is_deleted:
            return False
        menu_photo.is_deleted = True
        menu_photo.deleted_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, photo_id: int, hard: bool = False) -> bool:
        """Delete a menu photo."""
        if not hard:
            return MenuPhotoRepository.soft_delete(db, photo_id)
        
        menu_photo = db.query(MenuPhoto).filter(MenuPhoto.id == photo_id).first()
        if not menu_photo:
            return False
        db.delete(menu_photo)
        db.commit()
        return True
    
    @staticmethod
    def reorder(db: Session, photo_orders: List[Dict[str, int]]) -> bool:
        """Update display order for multiple photos.
        
        Args:
            photo_orders: List of dicts with 'id' and 'display_order' keys
                          Example: [{"id": 1, "display_order": 0}, {"id": 2, "display_order": 1}]
        """
        try:
            for photo_order in photo_orders:
                photo_id = photo_order.get('id')
                display_order = photo_order.get('display_order')
                if photo_id is None or display_order is None:
                    continue
                
                menu_photo = db.query(MenuPhoto).filter(MenuPhoto.id == photo_id).first()
                if menu_photo:
                    menu_photo.display_order = display_order
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def get_count(db: Session) -> int:
        """Get count of active menu photos."""
        return db.query(MenuPhoto).filter(MenuPhoto.is_deleted == False).count()
    
    @staticmethod
    def get_max_display_order(db: Session) -> int:
        """Get maximum display_order value for new photos."""
        result = db.query(MenuPhoto).filter(
            MenuPhoto.is_deleted == False
        ).order_by(MenuPhoto.display_order.desc()).first()
        if result:
            return result.display_order + 1
        return 0

