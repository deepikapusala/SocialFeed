"""Add notifications table (Stage 6 PY-P0-06)

Revision ID: 0006_add_notifications
Revises: 0005_add_post_lifecycle
Create Date: 2026-10-21 11:45:00.000000

Adds notifications table with unique deduplication constraints, recipient isolation,
and read status tracking.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006_add_notifications"
down_revision: Union[str, None] = "0005_add_post_lifecycle"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("target_post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("recipient_id <> actor_id", name="notifications_no_self_notification_check"),
        sa.CheckConstraint("event_type IN ('follow', 'follow_accepted', 'like', 'reply', 'repost')", name="notifications_event_type_check"),
        sa.UniqueConstraint("recipient_id", "actor_id", "event_type", "target_post_id", name="notifications_dedup_unique"),
    )

    op.create_index(
        "idx_notifications_recipient_created_id",
        "notifications",
        ["recipient_id", "created_at", "id"],
    )
    op.create_index(
        "idx_notifications_unread",
        "notifications",
        ["recipient_id", "read_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_notifications_unread", table_name="notifications")
    op.drop_index("idx_notifications_recipient_created_id", table_name="notifications")
    op.drop_table("notifications")

