"""
Tests for Public API Pydantic Schemas and CamelCase Serialization (Stage A).
"""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.schemas.common import CamelModel, PaginatedResponse
from app.schemas.health import HealthResponse
from app.schemas.user import AvatarVariants, UserAuthor, UserProfile, UserProfileResponse
from app.schemas.media import MediaItem
from app.schemas.post import PostItem, PostDetailResponse, FeedResponse


def test_health_schema():
    """Verify health response defaults to status='ok'."""
    h = HealthResponse()
    assert h.status == "ok"
    assert h.model_dump(by_alias=True) == {"status": "ok"}


def test_user_author_camelcase_serialization():
    """Verify user author serializes fields to camelCase (displayName, smallUrl, largeUrl)."""
    author = UserAuthor(
        id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        handle="asha",
        display_name="Asha Patel",
        avatar=AvatarVariants(
            small_url="/fixtures/asha-48.jpg",
            large_url="/fixtures/asha-96.jpg",
        ),
    )

    data = author.model_dump(by_alias=True)
    assert data["id"] == "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    assert data["handle"] == "asha"
    assert data["displayName"] == "Asha Patel"
    assert "display_name" not in data
    assert data["avatar"]["smallUrl"] == "/fixtures/asha-48.jpg"
    assert data["avatar"]["largeUrl"] == "/fixtures/asha-96.jpg"


def test_user_profile_response_shape():
    """Verify user profile envelope matches GET /users/{id} response format."""
    profile = UserProfile(
        id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        handle="asha",
        display_name="Asha Patel",
        bio="Software engineer & photographer",
        post_count=10,
        follower_count=250,
        following_count=180,
    )
    res = UserProfileResponse(item=profile)
    data = res.model_dump(by_alias=True)

    assert "item" in data
    item = data["item"]
    assert item["postCount"] == 10
    assert item["followerCount"] == 250
    assert item["followingCount"] == 180


def test_post_item_camelcase_serialization():
    """Verify post item serializes createdAt, likeCount, replyCount, likedByViewer to camelCase."""
    dt = datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
    post = PostItem(
        id="11111111-1111-4111-8111-111111111101",
        kind="original",
        text="Hello world photo post",
        created_at=dt,
        author=UserAuthor(
            id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            handle="asha",
            display_name="Asha",
        ),
        media=[
            MediaItem(
                id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01",
                alt_text="A desk with laptop",
                width=1200,
                height=800,
                position=0,
                small_url="/desk-sm.jpg",
                large_url="/desk-lg.jpg",
            )
        ],
        like_count=5,
        reply_count=2,
        liked_by_viewer=True,
    )

    data = post.model_dump(by_alias=True)
    assert data["id"] == "11111111-1111-4111-8111-111111111101"
    assert data["kind"] == "original"
    assert data["likeCount"] == 5
    assert data["replyCount"] == 2
    assert data["likedByViewer"] is True
    assert data["replyToId"] is None
    assert data["repostOfId"] is None
    assert data["media"][0]["altText"] == "A desk with laptop"
    assert data["media"][0]["smallUrl"] == "/desk-sm.jpg"
    assert data["media"][0]["largeUrl"] == "/desk-lg.jpg"


def test_post_item_rejects_invalid_kind():
    """Verify that unsupported kind strings raise ValidationError."""
    with pytest.raises(ValidationError):
        PostItem(
            id="11111111-1111-4111-8111-111111111101",
            kind="tweet",  # Invalid kind (must be original, reply, or repost)
            text="Invalid kind post",
            created_at=datetime.now(timezone.utc),
            author=UserAuthor(
                id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                handle="asha",
                display_name="Asha",
            ),
        )


def test_feed_response_shape():
    """Verify FeedResponse contains items, nextCursor, and hasMore in camelCase."""
    feed = FeedResponse(
        items=[],
        next_cursor="dummy-cursor-token",
        has_more=True,
    )
    data = feed.model_dump(by_alias=True)
    assert "items" in data
    assert "nextCursor" in data
    assert "hasMore" in data
    assert data["nextCursor"] == "dummy-cursor-token"
    assert data["hasMore"] is True
