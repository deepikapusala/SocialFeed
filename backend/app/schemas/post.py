"""
Post and Feed Schemas (Stage A & C).
"""

from typing import Any, Dict, List, Literal, Optional
from datetime import datetime
from pydantic import Field
from app.schemas.common import CamelModel
from app.schemas.user import UserAuthor
from app.schemas.media import MediaItem


PostKind = Literal["original", "reply", "repost"]


class PostItem(CamelModel):
    """
    Representation of a Post across Feed, Detail, Replies, and Search.
    """
    id: str
    kind: PostKind
    text: Optional[str] = None
    created_at: datetime
    author: UserAuthor
    media: List[MediaItem] = []
    like_count: int = 0
    reply_count: int = 0
    repost_count: int = 0
    liked_by_viewer: bool = False
    reposted_by_viewer: bool = False
    reply_to_id: Optional[str] = None
    repost_of_id: Optional[str] = None
    updated_at: Optional[datetime] = None
    version: Optional[int] = 1
    liker_handles: List[str] = []


class PostDetailResponse(CamelModel):
    """
    Response envelope for GET /posts/{id} and POST /posts:
    { "item": { ... } }
    """
    item: PostItem


class FeedResponse(CamelModel):
    """
    Response envelope for GET /feed and GET /search/posts:
    {
      "items": [...],
      "nextCursor": null | string,
      "hasMore": bool
    }
    """
    items: List[PostItem]
    next_cursor: Optional[str] = None
    has_more: bool = False


class CreatePostRequest(CamelModel):
    """
    Request body for POST /posts.
    """
    kind: PostKind
    text: Optional[str] = Field(default=None, max_length=280)
    reply_to_id: Optional[str] = None
    repost_of_id: Optional[str] = None
    media: Optional[List[Dict[str, Any]]] = None


class UpdatePostRequest(CamelModel):
    """
    Request body for PATCH /posts/{id}.
    Strictly forbids immutable fields (kind, authorId, id, counts, etc.).
    """
    model_config = {"extra": "forbid"}

    text: str = Field(..., min_length=1, max_length=280)
    version: Optional[int] = Field(default=None, description="Expected post version for optimistic concurrency")


class LikeResponse(CamelModel):
    """
    Response body for PUT /posts/{id}/like and DELETE /posts/{id}/like.
    """
    post_id: str
    liked_by_viewer: bool
    like_count: int


class RepostResponse(CamelModel):
    """
    Response body for POST /posts/{id}/repost and DELETE /posts/{id}/repost.
    """
    post_id: str
    reposted_by_viewer: bool
    repost_count: int


