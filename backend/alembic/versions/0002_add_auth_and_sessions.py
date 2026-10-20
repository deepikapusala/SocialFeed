"""Add auth and sessions (Stage 1 PY-P0-01)

Revision ID: 0002_add_auth_and_sessions
Revises: 0001_initial_baseline
Create Date: 2026-10-16 12:55:00.000000

Adds password_hash and is_active to users, backfills V1 users with a known
seed password hash, and creates the sessions table for server-side token revocation.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_add_auth_and_sessions"
down_revision: Union[str, None] = "0001_initial_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Default seed hash for 'TestPassword123!'
DEFAULT_V1_SEED_HASH = "$argon2id$v=19$m=65536,t=3,p=4$fv5AaIEi8B3ufEWHKeQ3lA$bPo1F0VMpyKyKRB9Z9RgZ147t71+4Y7xgj8TRFOdHcI"


def upgrade() -> None:
    # 1. Add is_active column with default TRUE
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
    )

    # 2. Add password_hash column (initially nullable to allow backfill)
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )

    # 3. Backfill existing V1 users so no orphaned accounts exist
    op.execute(
        sa.text(f"UPDATE users SET password_hash = '{DEFAULT_V1_SEED_HASH}' WHERE password_hash IS NULL")
    )

    # 4. Enforce NOT NULL on password_hash now that existing rows are populated
    op.alter_column("users", "password_hash", nullable=False)

    # 5. Create sessions table for token authentication & revocation
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="sessions_pkey"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name="sessions_user_id_fkey"),
        sa.UniqueConstraint("token_hash", name="sessions_token_hash_unique"),
    )

    # 6. Index user_id for fast user session lookups
    op.create_index("idx_sessions_user_id", "sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "is_active")
