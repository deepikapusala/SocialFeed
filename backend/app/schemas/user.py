"""
User and Author Schemas (Stage A).
"""

from typing import Optional
from pydantic import ConfigDict, Field, field_validator
from app.schemas.common import CamelModel


class ProfileUpdateRequest(CamelModel):
    """
    Allowlist for updating own profile.
    """
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    handle: Optional[str] = Field(None, min_length=1, max_length=30)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_small_url: Optional[str] = Field(None, max_length=1000)
    avatar_large_url: Optional[str] = Field(None, max_length=1000)
    is_private: Optional[bool] = Field(None)

    @field_validator("handle")
    @classmethod
    def validate_handle(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip().lower()
            if not clean:
                raise ValueError("Handle cannot be empty")
            import re
            if not re.match(r"^[a-z0-9_]+$", clean):
                raise ValueError("Handle must contain only lowercase alphanumeric characters and underscores")
            return clean
        return None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if not clean:
                raise ValueError("Display name cannot be empty or whitespace only")
            return clean
        return None

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return None

    @field_validator("avatar_small_url", "avatar_large_url")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if clean and not (clean.startswith("http://") or clean.startswith("https://") or clean.startswith("/")):
                raise ValueError("Avatar URL must be a valid http/https or relative URL")
            return clean if clean else None
        return None


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
    followed_by_viewer: bool = False


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
    followed_by_viewer: bool = False
    is_private: bool = False
    relationship_status: str = "none"  # 'none', 'pending', 'accepted'


class UserProfileResponse(CamelModel):
    """
    Response envelope for GET /users/{id}:
    { "item": { ... } }
    """
    item: UserProfile


class FollowResponse(CamelModel):
    """
    Response body for PUT /users/{id}/follow and DELETE /users/{id}/follow.
    """
    user_id: str
    followed_by_viewer: bool
    follower_count: int
    relationship_status: str = "accepted"  # 'none', 'pending', 'accepted'


class RelationshipUserItem(CamelModel):
    """
    User representation in bounded followers and following relationship lists.
    """
    id: str
    handle: str
    display_name: str
    avatar: Optional[AvatarVariants] = None
    followed_by_viewer: bool = False
    created_at: Optional[str] = None


class FollowRequestAcceptResponse(CamelModel):
    """
    Response schema for POST /users/requests/{requester_id}/accept.
    """
    requester_id: str
    accepted: bool = True
    follower_count: int


