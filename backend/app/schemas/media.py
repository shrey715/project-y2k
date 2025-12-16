from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class MediaItem(BaseModel):
    """Schema for media item (image or audio)."""
    id: int
    filename: str


class MediaListResponse(BaseModel):
    """Schema for media list response."""
    items: List[MediaItem]


class VideoImageItem(BaseModel):
    """Schema for video image item."""
    image_id: int
    duration: int
    transition: Dict[str, Any]


class VideoRenderRequest(BaseModel):
    """Schema for video render request."""
    info: Dict[str, Any]
    video: Dict[str, Any]
    audios: Optional[List[Dict[str, Any]]] = None
