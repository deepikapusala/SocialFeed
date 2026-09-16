"""
Tests for Task Cancellation and Async Cleanup (Stage A).

Verifies:
- Cancellation propagates correctly through repository and service async operations.
- asyncio.CancelledError is not swallowed incorrectly.
- When an async operation is cancelled mid-flight, no dangling work or corrupted state is left.
- Subsequent requests on the same repository instance succeed immediately without errors.
"""

import asyncio
import pytest
from app.repositories.fixture_repository import FixtureRepository
from app.services.feed_service import FeedService
from app.services.social_service import SocialService


@pytest.mark.asyncio
async def test_repository_simulated_io_cancellation():
    """Verify cancellation during repository I/O propagates CancelledError and preserves state."""
    repo = FixtureRepository(simulated_io_ms=500)

    # Launch task that simulates 500ms I/O
    task = asyncio.create_task(
        repo.list_original_feed(cursor_tuple=None, limit=10, viewer_id="test-viewer")
    )

    # Let it enter the simulated I/O wait
    await asyncio.sleep(0.05)

    # Cancel the task
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    # Confirm the repository is fully operational for subsequent requests
    repo.simulated_io_ms = 0
    res = await repo.list_original_feed(cursor_tuple=None, limit=5, viewer_id="test-viewer")
    assert len(res) == 6  # limit + 1


@pytest.mark.asyncio
async def test_service_feed_cancellation():
    """Verify FeedService gracefully handles task cancellation."""
    repo = FixtureRepository(simulated_io_ms=400)
    service = FeedService(repo)

    task = asyncio.create_task(
        service.get_feed(cursor_str=None, limit=10, viewer_id="test-viewer")
    )

    await asyncio.sleep(0.05)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    # Next call on service succeeds cleanly
    repo.simulated_io_ms = 0
    response = await service.get_feed(cursor_str=None, limit=10, viewer_id="test-viewer")
    assert len(response.items) == 10
    assert response.has_more is True


@pytest.mark.asyncio
async def test_social_service_cancellation():
    """Verify SocialService post detail and profile retrieval cancellation."""
    repo = FixtureRepository(simulated_io_ms=400)
    service = SocialService(repo)

    post_id = "11111111-1111-4111-8111-111111111101"
    task = asyncio.create_task(
        service.get_post_detail(post_id=post_id, viewer_id="test-viewer")
    )

    await asyncio.sleep(0.05)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    # Next call succeeds
    repo.simulated_io_ms = 0
    post_res = await service.get_post_detail(post_id=post_id, viewer_id="test-viewer")
    assert post_res.item.id == post_id
