"""Initial schema baseline (Stage C Step 2)

Revision ID: 0001_initial_baseline
Revises: None
Create Date: 2026-09-14 18:00:00.000000

This baseline migration establishes the versioned schema for Social Feed,
matching the reviewed DDL in db/schema.sql and SQLAlchemy ORM models.

Usage:
  - Fresh Database: Run `alembic upgrade head` to construct all tables and constraints.
  - Existing Database (with schema.sql): Run `alembic stamp head` to baseline.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("handle", sa.String(length=30), nullable=False),
        sa.Column("display_name", sa.String(length=50), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_small_url", sa.Text(), nullable=True),
        sa.Column("avatar_large_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("handle", name="users_handle_unique"),
        sa.CheckConstraint(
            "handle = lower(handle) AND length(trim(handle)) >= 1 AND handle ~ '^[a-z0-9_]+$'",
            name="users_handle_format_check",
        ),
        sa.CheckConstraint("length(trim(display_name)) >= 1", name="users_display_name_check"),
        sa.CheckConstraint(
            "avatar_small_url IS NULL OR length(trim(avatar_small_url)) > 0",
            name="users_avatar_small_url_check",
        ),
        sa.CheckConstraint(
            "avatar_large_url IS NULL OR length(trim(avatar_large_url)) > 0",
            name="users_avatar_large_url_check",
        ),
    )

    # 2. posts table
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("text", sa.String(length=280), nullable=True),
        sa.Column("reply_to_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("repost_of_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="posts_pkey"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT", name="posts_author_id_fkey"),
        sa.ForeignKeyConstraint(["reply_to_id"], ["posts.id"], ondelete="RESTRICT", name="posts_reply_to_id_fkey"),
        sa.ForeignKeyConstraint(["repost_of_id"], ["posts.id"], ondelete="RESTRICT", name="posts_repost_of_id_fkey"),
        sa.UniqueConstraint("author_id", "repost_of_id", name="posts_author_repost_unique"),
        sa.CheckConstraint("kind IN ('original', 'reply', 'repost')", name="posts_kind_check"),
        sa.CheckConstraint(
            "text IS NULL OR length(trim(text)) BETWEEN 1 AND 280",
            name="posts_text_length_check",
        ),
        sa.CheckConstraint(
            "(kind = 'original' AND text IS NOT NULL AND reply_to_id IS NULL AND repost_of_id IS NULL) OR "
            "(kind = 'reply'    AND text IS NOT NULL AND reply_to_id IS NOT NULL AND repost_of_id IS NULL) OR "
            "(kind = 'repost'   AND text IS NULL     AND reply_to_id IS NULL AND repost_of_id IS NOT NULL)",
            name="posts_kind_attributes_check",
        ),
    )

    # 3. post_media table
    op.create_table(
        "post_media",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("alt_text", sa.Text(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("small_url", sa.Text(), nullable=False),
        sa.Column("large_url", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="post_media_pkey"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE", name="post_media_post_id_fkey"),
        sa.UniqueConstraint("post_id", "position", name="post_media_post_position_unique"),
        sa.CheckConstraint("position >= 0 AND position <= 3", name="post_media_position_check"),
        sa.CheckConstraint("width > 0 AND height > 0", name="post_media_dimensions_check"),
        sa.CheckConstraint("length(trim(alt_text)) >= 1", name="post_media_alt_text_check"),
        sa.CheckConstraint("length(trim(small_url)) >= 1", name="post_media_small_url_check"),
        sa.CheckConstraint("length(trim(large_url)) >= 1", name="post_media_large_url_check"),
    )

    # 4. post_likes table
    op.create_table(
        "post_likes",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "post_id", name="post_likes_pkey"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name="post_likes_user_id_fkey"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE", name="post_likes_post_id_fkey"),
    )

    # 5. follows table
    op.create_table(
        "follows",
        sa.Column("follower_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("following_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("follower_id", "following_id", name="follows_pkey"),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE", name="follows_follower_id_fkey"),
        sa.ForeignKeyConstraint(["following_id"], ["users.id"], ondelete="CASCADE", name="follows_following_id_fkey"),
        sa.CheckConstraint("follower_id <> following_id", name="follows_no_self_follow_check"),
    )


def downgrade() -> None:
    op.drop_table("follows")
    op.drop_table("post_likes")
    op.drop_table("post_media")
    op.drop_table("posts")
    op.drop_table("users")
