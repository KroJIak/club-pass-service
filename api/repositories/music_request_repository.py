"""Repository for music requests."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from api.models.music_request import MusicRequest


class MusicRequestRepository:
    """Repository for music request operations."""
    
    @staticmethod
    def get_all(db: Session, event_id: Optional[int] = None) -> List[MusicRequest]:
        """Get all music requests, sorted by request_count DESC."""
        query = db.query(MusicRequest).filter(
            MusicRequest.is_deleted == False
        )
        if event_id:
            query = query.filter(MusicRequest.event_id == event_id)
        return query.order_by(MusicRequest.request_count.desc()).all()
    
    @staticmethod
    def get_by_id(db: Session, request_id: int) -> Optional[MusicRequest]:
        """Get a music request by ID."""
        return db.query(MusicRequest).filter(
            MusicRequest.id == request_id,
            MusicRequest.is_deleted == False
        ).first()
    
    @staticmethod
    def get_by_title_artist(
        db: Session,
        event_id: int,
        track_title: str,
        track_artist: str
    ) -> Optional[MusicRequest]:
        """Get a music request by title and artist for a specific event."""
        return db.query(MusicRequest).filter(
            MusicRequest.event_id == event_id,
            MusicRequest.track_title == track_title,
            MusicRequest.track_artist == track_artist,
            MusicRequest.is_deleted == False
        ).first()
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        event_id: int,
        track_title: str,
        track_artist: str,
        yandex_music_url: Optional[str] = None,
        other_source_url: Optional[str] = None,
    ) -> MusicRequest:
        """Create a new music request."""
        music_request = MusicRequest(
            user_id=user_id,
            event_id=event_id,
            track_title=track_title,
            track_artist=track_artist,
            yandex_music_url=yandex_music_url,
            other_source_url=other_source_url,
            request_count=1,
        )
        db.add(music_request)
        db.commit()
        db.refresh(music_request)
        return music_request
    
    @staticmethod
    def increment_request_count(db: Session, request_id: int) -> Optional[MusicRequest]:
        """Increment request_count for a music request."""
        music_request = MusicRequestRepository.get_by_id(db, request_id)
        if not music_request:
            return None
        music_request.request_count += 1
        db.commit()
        db.refresh(music_request)
        return music_request
    
    @staticmethod
    def soft_delete(db: Session, request_id: int) -> bool:
        """Soft delete a music request."""
        music_request = MusicRequestRepository.get_by_id(db, request_id)
        if not music_request or music_request.is_deleted:
            return False
        music_request.is_deleted = True
        music_request.deleted_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, request_id: int, hard: bool = False) -> bool:
        """Delete a music request."""
        if not hard:
            return MusicRequestRepository.soft_delete(db, request_id)
        
        music_request = db.query(MusicRequest).filter(MusicRequest.id == request_id).first()
        if not music_request:
            return False
        db.delete(music_request)
        db.commit()
        return True
    
    @staticmethod
    def delete_batch(db: Session, request_ids: List[int], hard: bool = False) -> int:
        """Delete multiple music requests."""
        count = 0
        for request_id in request_ids:
            if MusicRequestRepository.delete(db, request_id, hard=hard):
                count += 1
        return count

