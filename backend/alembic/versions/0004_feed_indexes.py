"""Add feed composite indexes (Stage 4 PY-P0-04)

Revision ID: 0004_feed_indexes
Revises: 0003_add_follow_privacy
Create Date: 2026-10-21 09:30:00.000000

Adds composite indexes to posts and follows to optimize personalized feed queries
and keyset cursor pagination without sequential table scans.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic (must be <= 32 chars).
revision: str = "0004_feed_indexes"
down_revision: Union[str, None] = "0003_add_follow_privacy"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Composite index on posts for author filtering and keyset ordering
    op.create_index(
        "idx_posts_author_created_id",
        "posts",
        ["author_id", "created_at", "id"],
    )

    # 2. Composite index on posts for kind filtering and keyset ordering
    op.create_index(
        "idx_posts_kind_created_id",
        "posts",
        ["kind", "created_at", "id"],
    )

    # 3. Composite covering index on follows for follower's accepted followees
    op.create_index(
        "idx_follows_follower_status",
        "follows",
        ["follower_id", "status", "following_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_follows_follower_status", table_name="follows")
    op.drop_index("idx_posts_kind_created_id", table_name="posts")
    op.drop_index("idx_posts_author_created_id", table_name="posts")
