"""
User and Author Schemas (Stage A).
"""

from typing import Optional
from app.schemas.common import CamelModel


class AvatarVariants(CamelModel):
    """
    Image variants for a user avatar.
    """
    small_url: str
    large_url: str


class UserAuthor(CamelModel):
    """
    Embedded author representation within a Post.
    """
    id: str
    handle: str
    display_name: str
    avatar: Optional[AvatarVariants] = None


class UserProfile(CamelModel):
    """
    Detailed profile information for GET /users/{id}.
    """
    id: str
    handle: str
    display_name: str
    bio: Optional[str] = None
    avatar: Optional[AvatarVariants] = None
    post_count: int = 0
    follower_count: int = 0
    following_count: int = 0


class UserProfileResponse(CamelModel):
    """
    Response envelope for GET /users/{id}:
    { "item": { ... } }
    """
    item: UserProfile
