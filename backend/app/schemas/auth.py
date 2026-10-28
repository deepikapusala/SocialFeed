"""
Authentication schemas for Stage 1 (PY-P0-01).

Implements bounded inputs, strict normalization, and extra="forbid".
"""

from datetime import datetime
import re
from typing import Optional
from pydantic import ConfigDict, Field, field_validator
from app.schemas.common import CamelModel
from app.schemas.user import UserProfile

HANDLE_REGEX = re.compile(r"^[a-z0-9_]+$")


class RegisterRequest(CamelModel):
    """Registration payload with bounded fields and normalization."""
    model_config = ConfigDict(extra="forbid")

    handle: str = Field(..., min_length=1, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    bio: Optional[str] = Field(None, max_length=500)

    @field_validator("handle")
    @classmethod
    def normalize_and_validate_handle(cls, v: str) -> str:
        clean = v.strip().lower()
        if not clean:
            raise ValueError("Handle cannot be empty or whitespace only")
        if not HANDLE_REGEX.match(clean):
            raise ValueError("Handle must contain only lowercase alphanumeric characters and underscores")
        return clean

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Display name cannot be empty or whitespace only")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_not_blank(cls, v: str) -> str:
        if not v or len(v.strip()) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class LoginRequest(CamelModel):
    """Login credentials payload."""
    model_config = ConfigDict(extra="forbid")

    handle: str = Field(..., min_length=1, max_length=30)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("handle")
    @classmethod
    def normalize_handle(cls, v: str) -> str:
        return v.strip().lower()


class AuthTokenResponse(CamelModel):
    """Successful authentication response containing Bearer token and user info."""
    access_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    user: UserProfile
    reactivated: bool = False
    was_reactivated: bool = False


class CurrentUserResponse(CamelModel):
    """Response envelope for GET /auth/me."""
    item: UserProfile
