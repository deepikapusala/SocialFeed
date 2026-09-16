"""
Unit tests for Stage C Step 2 SQLAlchemy ORM models and metadata.
Verifies schema parity, constraint definitions, table registration, and relationship mappings.
"""

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base, User, Post, PostMedia, PostLike, Follow


def test_metadata_contains_all_five_tables():
    """Verify that exactly the 5 required domain tables are registered in Base.metadata."""
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {"users", "posts", "post_media", "post_likes", "follows"}
    assert table_names == expected_tables, f"Metadata tables mismatch. Got: {table_names}"


def test_user_model_mapping():
    """Verify User ORM model column definitions and constraints."""
    table = Base.metadata.tables["users"]
    assert table.c.id.primary_key is True
    assert isinstance(table.c.id.type, UUID)
    assert table.c.handle.unique is True or any(
        isinstance(c, UniqueConstraint) and "handle" in [col.name for col in c.columns]
        for c in table.constraints
    )
    assert table.c.display_name.nullable is False
    assert table.c.created_at.nullable is False

    # Check constraint names
    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "users_handle_format_check" in check_names
    assert "users_display_name_check" in check_names
    assert "users_avatar_small_url_check" in check_names
    assert "users_avatar_large_url_check" in check_names


def test_post_model_mapping():
    """Verify Post ORM model columns, foreign keys, and invariants."""
    table = Base.metadata.tables["posts"]
    assert table.c.id.primary_key is True
    assert table.c.author_id.nullable is False
    assert table.c.kind.nullable is False

    # Check foreign keys
    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "users.id" in fk_targets
    assert "posts.id" in fk_targets

    # Check unique constraint for author repost
    unique_names = {c.name for c in table.constraints if isinstance(c, UniqueConstraint)}
    assert "posts_author_repost_unique" in unique_names

    # Check constraints
    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "posts_kind_check" in check_names
    assert "posts_text_length_check" in check_names
    assert "posts_kind_attributes_check" in check_names


def test_post_media_model_mapping():
    """Verify PostMedia ORM model columns and constraints."""
    table = Base.metadata.tables["post_media"]
    assert table.c.id.primary_key is True
    assert table.c.post_id.nullable is False
    assert table.c.position.nullable is False

    # Check position unique constraint per post
    unique_names = {c.name for c in table.constraints if isinstance(c, UniqueConstraint)}
    assert "post_media_post_position_unique" in unique_names

    # Check constraints
    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "post_media_position_check" in check_names
    assert "post_media_dimensions_check" in check_names
    assert "post_media_alt_text_check" in check_names


def test_post_likes_composite_pk():
    """Verify PostLike composite primary key and foreign keys."""
    table = Base.metadata.tables["post_likes"]
    pk_cols = [c.name for c in table.primary_key.columns]
    assert pk_cols == ["user_id", "post_id"]

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "users.id" in fk_targets
    assert "posts.id" in fk_targets


def test_follows_composite_pk_and_check():
    """Verify Follow composite primary key, foreign keys, and no-self-follow check."""
    table = Base.metadata.tables["follows"]
    pk_cols = [c.name for c in table.primary_key.columns]
    assert pk_cols == ["follower_id", "following_id"]

    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "users.id" in fk_targets

    check_names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "follows_no_self_follow_check" in check_names


def test_orm_relationships_integrity():
    """Verify ORM relationships map without mapper initialization errors."""
    # Instantiating ORM instances validates mapper compilation
    user = User(handle="test_user", display_name="Test User")
    post = Post(author=user, kind="original", text="Hello world")
    media = PostMedia(post=post, position=0, alt_text="Alt", width=800, height=600, small_url="/s.jpg", large_url="/l.jpg")
    like = PostLike(user=user, post=post)
    follow = Follow(follower=user, following=user)

    assert post.author == user
    assert media.post == post
    assert like.user == user
    assert follow.follower == user
