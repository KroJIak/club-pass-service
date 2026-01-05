"""Repository for support message photos."""
from sqlalchemy.orm import Session
from typing import List, Optional
from api.models.support_message_photo import SupportMessagePhoto


class SupportMessagePhotoRepository:
    """Repository for support message photo operations."""
    
    @staticmethod
    def create(
        db: Session,
        support_message_id: int,
        file_path: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        is_admin_photo: bool = False,
    ) -> SupportMessagePhoto:
        """Create a new support message photo."""
        photo = SupportMessagePhoto(
            support_message_id=support_message_id,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            is_admin_photo=is_admin_photo,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo
    
    @staticmethod
    def get_by_support_message_id(
        db: Session,
        support_message_id: int,
        is_admin_photo: Optional[bool] = None,
    ) -> List[SupportMessagePhoto]:
        """Get all photos for a support message."""
        query = db.query(SupportMessagePhoto).filter(
            SupportMessagePhoto.support_message_id == support_message_id,
            SupportMessagePhoto.is_deleted == False
        )
        
        if is_admin_photo is not None:
            query = query.filter(SupportMessagePhoto.is_admin_photo == is_admin_photo)
        
        return query.order_by(SupportMessagePhoto.created_at.asc()).all()
    
    @staticmethod
    def get_by_id(db: Session, photo_id: int) -> Optional[SupportMessagePhoto]:
        """Get a photo by ID."""
        return db.query(SupportMessagePhoto).filter(
            SupportMessagePhoto.id == photo_id,
            SupportMessagePhoto.is_deleted == False
        ).first()
    
    @staticmethod
    def delete(db: Session, photo_id: int) -> bool:
        """Delete a photo."""
        photo = db.query(SupportMessagePhoto).filter(SupportMessagePhoto.id == photo_id).first()
        if not photo:
            return False
        db.delete(photo)
        db.commit()
        return True
    
    @staticmethod
    def delete_by_support_message_id(db: Session, support_message_id: int) -> int:
        """Delete all photos for a support message. Returns number of deleted photos."""
        photos = db.query(SupportMessagePhoto).filter(
            SupportMessagePhoto.support_message_id == support_message_id
        ).all()
        count = len(photos)
        for photo in photos:
            db.delete(photo)
        db.commit()
        return count


