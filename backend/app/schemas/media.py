"""
Media Item Schemas (Stage A).
"""

from typing import Optional
from datetime import datetime
from app.schemas.common import CamelModel


class MediaItem(CamelModel):
    """
    Image media representation for post carousels and profile media.
    """
    id: str
    alt_text: str
    width: int
    height: int
    position: int
    small_url: str
    large_url: str
    post_id: Optional[str] = None
    created_at: Optional[datetime] = None
