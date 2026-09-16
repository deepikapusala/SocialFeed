"""
Tests for In-Memory Fixture Repository (Stage A).
"""

import pytest
from datetime import datetime, timezone

from app.repositories.fixture_repository import FixtureRepository
from app.fixtures.manifest import (
    DEMO_USER_ID,
    TIED_POST_ID_A,
    TIED_POST_ID_B,
    TIED_TIMESTAMP,
)


@pytest.fixture
def repo():
    return FixtureRepository(simulated_io_ms=0)


@pytest.mark.asyncio
async def test_feed_returns_only_originals(repo):
    """Verify feed returns only posts with kind='original'."""
    posts = await repo.list_original_feed(cursor_tuple=None, limit=50, viewer_id=DEMO_USER_ID)
    assert len(posts) == 30
    for p in posts:
        assert p["kind"] == "original"


@pytest.mark.asyncio
async def test_feed_ordering_and_tie_breaking(repo):
    """Verify reverse chronological ordering and id tie-breaker for identical timestamps."""
    posts = await repo.list_original_feed(cursor_tuple=None, limit=30, viewer_id=DEMO_USER_ID)

    for i in range(len(posts) - 1):
        curr_p, next_p = posts[i], posts[i + 1]
        assert (curr_p["createdAt"] > next_p["createdAt"]) or (
            curr_p["createdAt"] == next_p["createdAt"] and curr_p["id"] > next_p["id"]
        )

    # Check the specific tied pair: Post 11 must appear before Post 10
    ids = [p["id"] for p in posts]
    idx_a = ids.index(TIED_POST_ID_A)  # ...1110
    idx_b = ids.index(TIED_POST_ID_B)  # ...1111
    assert idx_b < idx_a, f"Post B (ID: {TIED_POST_ID_B}) must come before Post A (ID: {TIED_POST_ID_A})"


@pytest.mark.asyncio
async def test_feed_limit_plus_one(repo):
    """Verify requesting limit=10 returns up to 11 records when more items exist."""
    posts = await repo.list_original_feed(cursor_tuple=None, limit=10, viewer_id=DEMO_USER_ID)
    assert len(posts) == 11


@pytest.mark.asyncio
async def test_feed_cursor_continuation(repo):
    """Verify cursor continuation returns the next batch strictly smaller than cursor."""
    # Page 1
    page1 = await repo.list_original_feed(cursor_tuple=None, limit=10, viewer_id=DEMO_USER_ID)
    assert len(page1) == 11
    last_p1 = page1[9]  # 10th item

    # Page 2 using last item of page 1 as cursor
    cursor_tuple = (last_p1["createdAt"], last_p1["id"])
    page2 = await repo.list_original_feed(cursor_tuple=cursor_tuple, limit=10, viewer_id=DEMO_USER_ID)

    assert len(page2) == 11
    # Page 2 first item must be the 11th item from initial fetch
    assert page2[0]["id"] == page1[10]["id"]


@pytest.mark.asyncio
async def test_viewer_liked_state(repo):
    """Verify likedByViewer is true for demo user on post 1 and false on unliked posts."""
    post1 = await repo.get_post_detail("11111111-1111-4111-8111-111111111101", viewer_id=DEMO_USER_ID)
    assert post1 is not None
    assert post1["likedByViewer"] is True

    # Check unliked post (Post 30)
    post30 = await repo.get_post_detail("11111111-1111-4111-8111-111111111130", viewer_id=DEMO_USER_ID)
    assert post30 is not None
    assert post30["likedByViewer"] is False


@pytest.mark.asyncio
async def test_get_post_detail_not_found(repo):
    """Verify get_post_detail returns None when ID does not exist."""
    missing = await repo.get_post_detail("99999999-9999-9999-9999-999999999999", viewer_id=DEMO_USER_ID)
    assert missing is None


@pytest.mark.asyncio
async def test_get_user_profile_statistics(repo):
    """Verify user profile statistics counts are accurate and not inflated."""
    profile = await repo.get_user_profile(DEMO_USER_ID)
    assert profile is not None
    assert profile["handle"] == "asha"
    assert profile["postCount"] == 6  # 30 originals distributed over 5 authors = 6 each
    assert profile["followerCount"] == 2  # user 2 and user 3 follow asha
    assert profile["followingCount"] == 3  # asha follows user 2, 3, 4


@pytest.mark.asyncio
async def test_get_user_profile_not_found(repo):
    """Verify get_user_profile returns None for unknown user ID."""
    missing = await repo.get_user_profile("99999999-9999-9999-9999-999999999999")
    assert missing is None


@pytest.mark.asyncio
async def test_list_direct_replies(repo):
    """Verify direct replies are fetched only for target post."""
    replies = await repo.list_direct_replies(
        post_id="11111111-1111-4111-8111-111111111101",
        cursor_tuple=None,
        limit=10,
        viewer_id=DEMO_USER_ID,
    )
    assert len(replies) > 0
    for r in replies:
        assert r["replyToId"] == "11111111-1111-4111-8111-111111111101"


@pytest.mark.asyncio
async def test_search_originals_literal(repo):
    """Verify case-insensitive literal substring search."""
    results = await repo.search_originals(
        query="exploration",
        cursor_tuple=None,
        limit=10,
        viewer_id=DEMO_USER_ID,
    )
    assert len(results) > 0
    for res in results:
        assert "exploration" in res["text"].lower()

    # Search with literal '#'
    hash_results = await repo.search_originals(
        query="#explore",
        cursor_tuple=None,
        limit=10,
        viewer_id=DEMO_USER_ID,
    )
    assert len(hash_results) > 0
