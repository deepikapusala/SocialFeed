"""
SQLAlchemy ORM model for notifications table.
Target Engine: PostgreSQL 16+
Reference: Stage 6 (PY-P0-06)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
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
    from app.models.post import Post


class Notification(Base):
    """
    Represents an event notification delivered to a recipient.
    """
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    target_post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=True,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("recipient_id <> actor_id", name="notifications_no_self_notification_check"),
        CheckConstraint("event_type IN ('follow', 'follow_accepted', 'like', 'reply', 'repost')", name="notifications_event_type_check"),
        UniqueConstraint("recipient_id", "actor_id", "event_type", "target_post_id", name="notifications_dedup_unique"),
    )

    # Relationships
    recipient: Mapped["User"] = relationship(
        "User",
        foreign_keys=[recipient_id],
    )
    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_id],
    )
    target_post: Mapped[Optional["Post"]] = relationship(
        "Post",
        foreign_keys=[target_post_id],
    )

