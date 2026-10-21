"""Add post lifecycle, soft delete, and versioning (Stage 5 PY-P0-05)

Revision ID: 0005_add_post_lifecycle
Revises: 0004_feed_indexes
Create Date: 2026-10-21 10:20:00.000000

Adds deleted_at, updated_at, and version columns to posts table for
owned-content lifecycle management and optimistic concurrency control.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic (must be <= 32 chars).
revision: str = "0005_add_post_lifecycle"
down_revision: Union[str, None] = "0004_feed_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add deleted_at column for soft deletion
    op.add_column(
        "posts",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Add updated_at column for tracking edit timestamps
    op.add_column(
        "posts",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 3. Add version column for optimistic concurrency control (defaults to 1)
    op.add_column(
        "posts",
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
    )

    # 4. Create partial index on active posts
    op.create_index(
        "idx_posts_deleted_at",
        "posts",
        ["deleted_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_posts_deleted_at", table_name="posts")
    op.drop_column("posts", "version")
    op.drop_column("posts", "updated_at")
    op.drop_column("posts", "deleted_at")
