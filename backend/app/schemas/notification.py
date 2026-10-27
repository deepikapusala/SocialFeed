"""
Notification Schemas (Stage 6 PY-P0-06).
"""

from datetime import datetime
from typing import List, Literal, Optional
from app.schemas.common import CamelModel
from app.schemas.user import UserAuthor

NotificationEventType = Literal["follow", "follow_accepted", "like", "reply", "repost"]


class NotificationTargetPost(CamelModel):
    id: str
    kind: Optional[str] = None
    text: Optional[str] = None
    is_deleted: bool = False
    reply_to_id: Optional[str] = None


class NotificationItem(CamelModel):
    id: str
    event_type: NotificationEventType
    created_at: datetime
    read_at: Optional[datetime] = None
    is_read: bool = False
    actor: UserAuthor
    target_post: Optional[NotificationTargetPost] = None


class NotificationListResponse(CamelModel):
    items: List[NotificationItem]
    unread_count: int
    next_cursor: Optional[str] = None
    has_more: bool = False


class MarkReadResponse(CamelModel):
    marked_count: int
    unread_count: int

