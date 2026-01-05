"""Repository for music queue."""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from api.models.music_queue import MusicQueue


class MusicQueueRepository:
    """Repository for music queue operations."""
    
    @staticmethod
    def get_all(db: Session) -> List[MusicQueue]:
        """Get all music queue items, sorted by queue_order."""
        return db.query(MusicQueue).filter(
            MusicQueue.is_deleted == False
        ).order_by(MusicQueue.queue_order.asc()).all()
    
    @staticmethod
    def get_by_id(db: Session, queue_id: int) -> Optional[MusicQueue]:
        """Get a music queue item by ID."""
        return db.query(MusicQueue).filter(
            MusicQueue.id == queue_id,
            MusicQueue.is_deleted == False
        ).first()
    
    @staticmethod
    def create(
        db: Session,
        track_title: str,
        track_artist: str,
        yandex_music_url: Optional[str] = None,
        other_source_url: Optional[str] = None,
    ) -> MusicQueue:
        """Create a new music queue item (adds to end of queue)."""
        max_order = MusicQueueRepository.get_max_order(db)
        music_queue = MusicQueue(
            track_title=track_title,
            track_artist=track_artist,
            yandex_music_url=yandex_music_url,
            other_source_url=other_source_url,
            queue_order=max_order,
        )
        db.add(music_queue)
        db.commit()
        db.refresh(music_queue)
        return music_queue
    
    @staticmethod
    def get_max_order(db: Session) -> int:
        """Get maximum queue_order value for new items."""
        result = db.query(MusicQueue).filter(
            MusicQueue.is_deleted == False
        ).order_by(MusicQueue.queue_order.desc()).first()
        if result:
            return result.queue_order + 1
        return 0
    
    @staticmethod
    def reorder(db: Session, queue_orders: List[Dict[str, int]]) -> bool:
        """Update queue_order for multiple items.
        
        Args:
            queue_orders: List of dicts with 'id' and 'queue_order' keys
                          Example: [{"id": 1, "queue_order": 0}, {"id": 2, "queue_order": 1}]
        """
        try:
            for queue_order in queue_orders:
                queue_id = queue_order.get('id')
                order = queue_order.get('queue_order')
                if queue_id is None or order is None:
                    continue
                
                music_queue = db.query(MusicQueue).filter(MusicQueue.id == queue_id).first()
                if music_queue:
                    music_queue.queue_order = order
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def soft_delete(db: Session, queue_id: int) -> bool:
        """Soft delete a music queue item."""
        music_queue = MusicQueueRepository.get_by_id(db, queue_id)
        if not music_queue or music_queue.is_deleted:
            return False
        music_queue.is_deleted = True
        music_queue.deleted_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, queue_id: int, hard: bool = False) -> bool:
        """Delete a music queue item."""
        if not hard:
            return MusicQueueRepository.soft_delete(db, queue_id)
        
        music_queue = db.query(MusicQueue).filter(MusicQueue.id == queue_id).first()
        if not music_queue:
            return False
        db.delete(music_queue)
        db.commit()
        return True
    
    @staticmethod
    def delete_batch(db: Session, queue_ids: List[int], hard: bool = False) -> int:
        """Delete multiple music queue items."""
        count = 0
        for queue_id in queue_ids:
            if MusicQueueRepository.delete(db, queue_id, hard=hard):
                count += 1
        return count

