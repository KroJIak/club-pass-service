"""Repository for admin message photos."""
from sqlalchemy.orm import Session
from typing import List, Optional
from api.models.admin_message_photo import AdminMessagePhoto


class AdminMessagePhotoRepository:
    """Repository for admin message photo operations."""
    
    @staticmethod
    def create(
        db: Session,
        admin_message_id: int,
        file_path: str,
        file_name: str,
        file_size: int,
        mime_type: str,
    ) -> AdminMessagePhoto:
        """Create a new admin message photo."""
        photo = AdminMessagePhoto(
            admin_message_id=admin_message_id,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo
    
    @staticmethod
    def get_by_admin_message_id(
        db: Session,
        admin_message_id: int,
    ) -> List[AdminMessagePhoto]:
        """Get all photos for an admin message."""
        return db.query(AdminMessagePhoto).filter(
            AdminMessagePhoto.admin_message_id == admin_message_id
        ).order_by(AdminMessagePhoto.created_at.asc()).all()
    
    @staticmethod
    def get_by_id(db: Session, photo_id: int) -> Optional[AdminMessagePhoto]:
        """Get a photo by ID."""
        return db.query(AdminMessagePhoto).filter(AdminMessagePhoto.id == photo_id).first()
    
    @staticmethod
    def delete(db: Session, photo_id: int) -> bool:
        """Delete a photo."""
        photo = db.query(AdminMessagePhoto).filter(AdminMessagePhoto.id == photo_id).first()
        if not photo:
            return False
        db.delete(photo)
        db.commit()
        return True
    
    @staticmethod
    def delete_by_admin_message_id(db: Session, admin_message_id: int) -> int:
        """Delete all photos for an admin message. Returns number of deleted photos."""
        photos = db.query(AdminMessagePhoto).filter(
            AdminMessagePhoto.admin_message_id == admin_message_id
        ).all()
        count = len(photos)
        for photo in photos:
            db.delete(photo)
        db.commit()
        return count

