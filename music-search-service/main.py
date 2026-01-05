"""FastAPI service for music search."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from services.music_searcher import MusicSearcher

app = FastAPI(title="Music Search Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize music searcher
yandex_token = os.getenv("YANDEX_MUSIC_TOKEN", "")
music_api_base = os.getenv("MUSIC_API_BASE_URL", "https://bhindi1.ddns.net/music/api")

if not yandex_token:
    raise ValueError("YANDEX_MUSIC_TOKEN environment variable is required")

searcher = MusicSearcher(yandex_token, music_api_base)


class MusicSearchRequest(BaseModel):
    """Request model for music search."""
    song_title: str
    artist: Optional[str] = None


class TrackLink(BaseModel):
    """Track link model."""
    platform: str
    url: Optional[str] = None


class TrackResponse(BaseModel):
    """Track response model."""
    title: str
    artist: str
    source: str
    links: Dict[str, Optional[str]]
    album: Optional[str] = None
    release_date: Optional[str] = None
    track_id: Optional[str] = None


class MusicSearchResponse(BaseModel):
    """Response model for music search."""
    tracks: List[TrackResponse]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/search", response_model=MusicSearchResponse)
async def search_music(request: MusicSearchRequest):
    """
    Search for music tracks.
    
    Args:
        request: Search request with song_title and optional artist
    
    Returns:
        List of found tracks with links to various platforms
    """
    try:
        # Use advanced search to get unique tracks
        tracks = searcher.search_advanced(
            song_title=request.song_title,
            artist=request.artist,
            min_similarity=0.3
        )
        
        # Convert Track objects to TrackResponse
        track_responses = []
        for track in tracks:
            track_responses.append(TrackResponse(
                title=track.title,
                artist=track.artist,
                source=track.source,
                links=track.links,
                album=track.album,
                release_date=track.release_date,
                track_id=track.track_id
            ))
        
        return MusicSearchResponse(tracks=track_responses)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching music: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

