"""
SQLAlchemy ORM model for follows table.
Target Engine: PostgreSQL 16+
Reference: db/schema.sql
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Follow(Base):
    """
    Directional follow graph association table.
    Self-follows prohibited by CHECK constraint.
    """
    __tablename__ = "follows"

    follower_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    following_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("follower_id <> following_id", name="follows_no_self_follow_check"),
    )

    # Relationships
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following",
    )
    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )
