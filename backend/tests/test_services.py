"""
Tests for FeedService and SocialService (Stage A).
"""

import pytest

from app.common.errors import NotFoundError, ValidationError
from app.fixtures.manifest import DEMO_USER_ID
from app.repositories.fixture_repository import FixtureRepository
from app.services.feed_service import FeedService
from app.services.social_service import SocialService


@pytest.fixture
def services():
    repo = FixtureRepository(simulated_io_ms=0)
    return FeedService(repo), SocialService(repo)


# ---------------------------------------------------------------------------
# FeedService Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_feed_service_pagination_flow(services):
    feed_svc, _ = services

    # Page 1 (limit=10)
    page1 = await feed_svc.get_feed(cursor_str=None, limit=10, viewer_id=DEMO_USER_ID)
    assert len(page1.items) == 10
    assert page1.has_more is True
    assert page1.next_cursor is not None

    # Page 2 (limit=10)
    page2 = await feed_svc.get_feed(cursor_str=page1.next_cursor, limit=10, viewer_id=DEMO_USER_ID)
    assert len(page2.items) == 10
    assert page2.has_more is True
    assert page2.next_cursor is not None

    # Verify no duplicates across page 1 and page 2
    page1_ids = {p.id for p in page1.items}
    page2_ids = {p.id for p in page2.items}
    assert len(page1_ids.intersection(page2_ids)) == 0

    # Page 3 (final page, limit=10)
    page3 = await feed_svc.get_feed(cursor_str=page2.next_cursor, limit=10, viewer_id=DEMO_USER_ID)
    assert len(page3.items) == 10
    assert page3.has_more is False
    assert page3.next_cursor is None


@pytest.mark.asyncio
async def test_feed_service_invalid_limit(services):
    feed_svc, _ = services

    with pytest.raises(ValidationError) as exc:
        await feed_svc.get_feed(cursor_str=None, limit=0, viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 400

    with pytest.raises(ValidationError) as exc:
        await feed_svc.get_feed(cursor_str=None, limit=51, viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_feed_service_invalid_cursor(services):
    feed_svc, _ = services

    with pytest.raises(ValidationError) as exc:
        await feed_svc.get_feed(cursor_str="invalid-cursor-token", limit=10, viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 400
    assert exc.value.details[0]["field"] == "cursor"


# ---------------------------------------------------------------------------
# SocialService Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_social_service_post_detail(services):
    _, social_svc = services

    res = await social_svc.get_post_detail("11111111-1111-4111-8111-111111111101", viewer_id=DEMO_USER_ID)
    assert res.item.id == "11111111-1111-4111-8111-111111111101"
    assert res.item.author.handle == "asha"
    assert res.item.liked_by_viewer is True
    assert len(res.item.media) == 2


@pytest.mark.asyncio
async def test_social_service_post_detail_not_found(services):
    _, social_svc = services

    with pytest.raises(NotFoundError) as exc:
        await social_svc.get_post_detail("99999999-9999-9999-9999-999999999999", viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_social_service_invalid_uuid(services):
    _, social_svc = services

    with pytest.raises(ValidationError) as exc:
        await social_svc.get_post_detail("not-a-uuid", viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 400
    assert exc.value.details[0]["field"] == "id"


@pytest.mark.asyncio
async def test_social_service_user_profile(services):
    _, social_svc = services

    profile_res = await social_svc.get_user_profile(DEMO_USER_ID)
    assert profile_res.item.id == DEMO_USER_ID
    assert profile_res.item.handle == "asha"
    assert profile_res.item.post_count == 6


@pytest.mark.asyncio
async def test_social_service_user_profile_not_found(services):
    _, social_svc = services

    with pytest.raises(NotFoundError) as exc:
        await social_svc.get_user_profile("99999999-9999-9999-9999-999999999999")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_social_service_replies_on_non_original_rejected(services):
    _, social_svc = services

    # Reply 1 ID: 22222222-2222-4222-8222-222222222201 (kind='reply')
    reply_id = "22222222-2222-4222-8222-222222222201"
    with pytest.raises(ValidationError) as exc:
        await social_svc.list_direct_replies(post_id=reply_id, cursor_str=None, limit=10, viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_social_service_search_query_validation(services):
    _, social_svc = services

    # Query too short (< 2 chars)
    with pytest.raises(ValidationError) as exc:
        await social_svc.search_originals(query="a", cursor_str=None, limit=10, viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 400

    # Query too long (> 80 chars)
    with pytest.raises(ValidationError) as exc:
        await social_svc.search_originals(query="a" * 81, cursor_str=None, limit=10, viewer_id=DEMO_USER_ID)
    assert exc.value.status_code == 400

    # Valid search
    res = await social_svc.search_originals(query="photo", cursor_str=None, limit=10, viewer_id=DEMO_USER_ID)
    assert len(res.items) > 0
