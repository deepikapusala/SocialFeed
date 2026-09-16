"""
SQLAlchemy ORM model for posts table.
Target Engine: PostgreSQL 16+
Reference: db/schema.sql
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.media import PostMedia
    from app.models.like import PostLike


class Post(Base):
    """
    Unified table representing original posts, direct replies, and reposts.
    Content reuse: reposts store no new text or media, only repost_of_id.
    """
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    text: Mapped[Optional[str]] = mapped_column(
        String(280),
        nullable=True,
    )
    reply_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    repost_of_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("author_id", "repost_of_id", name="posts_author_repost_unique"),
        CheckConstraint("kind IN ('original', 'reply', 'repost')", name="posts_kind_check"),
        CheckConstraint("text IS NULL OR length(trim(text)) BETWEEN 1 AND 280", name="posts_text_length_check"),
        CheckConstraint(
            "(kind = 'original' AND text IS NOT NULL AND reply_to_id IS NULL AND repost_of_id IS NULL) OR "
            "(kind = 'reply'    AND text IS NOT NULL AND reply_to_id IS NOT NULL AND repost_of_id IS NULL) OR "
            "(kind = 'repost'   AND text IS NULL     AND reply_to_id IS NULL AND repost_of_id IS NOT NULL)",
            name="posts_kind_attributes_check",
        ),
    )

    # Relationships
    author: Mapped["User"] = relationship(
        "User",
        back_populates="posts",
    )
    reply_to: Mapped[Optional["Post"]] = relationship(
        "Post",
        remote_side=[id],
        foreign_keys=[reply_to_id],
        back_populates="replies",
    )
    replies: Mapped[List["Post"]] = relationship(
        "Post",
        foreign_keys=[reply_to_id],
        back_populates="reply_to",
    )
    repost_of: Mapped[Optional["Post"]] = relationship(
        "Post",
        remote_side=[id],
        foreign_keys=[repost_of_id],
        back_populates="reposts",
    )
    reposts: Mapped[List["Post"]] = relationship(
        "Post",
        foreign_keys=[repost_of_id],
        back_populates="repost_of",
    )
    media: Mapped[List["PostMedia"]] = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="PostMedia.position",
    )
    likes: Mapped[List["PostLike"]] = relationship(
        "PostLike",
        back_populates="post",
        cascade="all, delete-orphan",
    )
