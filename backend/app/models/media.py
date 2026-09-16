"""
SQLAlchemy ORM model for post_media table.
Target Engine: PostgreSQL 16+
Reference: db/schema.sql
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.post import Post


class PostMedia(Base):
    """Ordered carousel media attachments belonging to original posts (0..4)."""
    __tablename__ = "post_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    alt_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    small_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    large_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("post_id", "position", name="post_media_post_position_unique"),
        CheckConstraint("position >= 0 AND position <= 3", name="post_media_position_check"),
        CheckConstraint("width > 0 AND height > 0", name="post_media_dimensions_check"),
        CheckConstraint("length(trim(alt_text)) >= 1", name="post_media_alt_text_check"),
        CheckConstraint("length(trim(small_url)) >= 1", name="post_media_small_url_check"),
        CheckConstraint("length(trim(large_url)) >= 1", name="post_media_large_url_check"),
    )

    # Relationships
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="media",
    )
