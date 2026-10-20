"""Public API Schemas Package."""

from app.schemas.common import CamelModel, PaginatedResponse
from app.schemas.health import HealthResponse
from app.schemas.user import AvatarVariants, UserAuthor, UserProfile, UserProfileResponse, ProfileUpdateRequest
from app.schemas.media import MediaItem
from app.schemas.post import PostKind, PostItem, PostDetailResponse, FeedResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthTokenResponse,
    CurrentUserResponse,
)

__all__ = [
    "CamelModel",
    "PaginatedResponse",
    "HealthResponse",
    "AvatarVariants",
    "UserAuthor",
    "UserProfile",
    "UserProfileResponse",
    "ProfileUpdateRequest",
    "MediaItem",
    "PostKind",
    "PostItem",
    "PostDetailResponse",
    "FeedResponse",
    "RegisterRequest",
    "LoginRequest",
    "AuthTokenResponse",
    "CurrentUserResponse",
]
