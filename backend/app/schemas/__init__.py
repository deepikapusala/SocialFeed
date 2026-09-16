"""Public API Schemas Package."""

from app.schemas.common import CamelModel, PaginatedResponse
from app.schemas.health import HealthResponse
from app.schemas.user import AvatarVariants, UserAuthor, UserProfile, UserProfileResponse
from app.schemas.media import MediaItem
from app.schemas.post import PostKind, PostItem, PostDetailResponse, FeedResponse

__all__ = [
    "CamelModel",
    "PaginatedResponse",
    "HealthResponse",
    "AvatarVariants",
    "UserAuthor",
    "UserProfile",
    "UserProfileResponse",
    "MediaItem",
    "PostKind",
    "PostItem",
    "PostDetailResponse",
    "FeedResponse",
]
