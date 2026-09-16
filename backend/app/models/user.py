"""
SQLAlchemy ORM model for users table.
Target Engine: PostgreSQL 16+
Reference: db/schema.sql
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import CheckConstraint, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.like import PostLike
    from app.models.follow import Follow


class User(Base):
    """Represents registered social accounts and authors."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    handle: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    avatar_small_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    avatar_large_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "handle = lower(handle) AND length(trim(handle)) >= 1 AND handle ~ '^[a-z0-9_]+$'",
            name="users_handle_format_check",
        ),
        CheckConstraint(
            "length(trim(display_name)) >= 1",
            name="users_display_name_check",
        ),
        CheckConstraint(
            "avatar_small_url IS NULL OR length(trim(avatar_small_url)) > 0",
            name="users_avatar_small_url_check",
        ),
        CheckConstraint(
            "avatar_large_url IS NULL OR length(trim(avatar_large_url)) > 0",
            name="users_avatar_large_url_check",
        ),
    )

    # Relationships
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        back_populates="author",
    )
    likes: Mapped[List["PostLike"]] = relationship(
        "PostLike",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    following: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    followers: Mapped[List["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
    )
