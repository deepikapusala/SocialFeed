"""Add follow privacy (Stage 3 PY-P0-03)

Revision ID: 0003_add_follow_privacy
Revises: 0002_add_auth_and_sessions
Create Date: 2026-10-20 18:40:00.000000

Adds is_private to users, and status ('pending', 'accepted') with check constraint to follows.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic (must be <= 32 chars).
revision: str = "0003_add_follow_privacy"
down_revision: Union[str, None] = "0002_add_auth_and_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_private column to users
    op.add_column(
        "users",
        sa.Column("is_private", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
    )

    # 2. Add status column to follows
    op.add_column(
        "follows",
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'accepted'"),
            nullable=False,
        ),
    )

    # 3. Add check constraint for legal follow statuses
    op.create_check_constraint(
        "follows_status_check",
        "follows",
        "status IN ('pending', 'accepted')",
    )

    # 4. Create composite index for efficient active relationship lookups
    op.create_index(
        "idx_follows_following_status",
        "follows",
        ["following_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("idx_follows_following_status", table_name="follows")
    op.drop_constraint("follows_status_check", "follows", type_="check")
    op.drop_column("follows", "status")
    op.drop_column("users", "is_private")
