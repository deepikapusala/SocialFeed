"""
Tests for Non-Blocking Async Behavior and Concurrency (Stage A).

Verifies:
- Configured SIMULATED_IO_MS does not block unrelated concurrent requests.
- Multiple async requests execute concurrently with overlapping timelines.
- Uses pure asyncio and ASGI transport without blocking thread pools.
"""

import time
import asyncio
import pytest
import httpx

from app.main import create_app
from app.common.dependencies import get_repository
from app.repositories.fixture_repository import FixtureRepository


@pytest.mark.asyncio
async def test_concurrent_requests_non_blocking_overlap():
    """
    Verify that multiple concurrent requests to the API overlap rather than execute sequentially.
    With simulated I/O delay of 80ms per request:
    - 4 sequential requests would take >= 320ms.
    - 4 concurrent async requests overlap and complete in ~80-180ms.
    """
    delay_ms = 80
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: FixtureRepository(simulated_io_ms=delay_ms)

    request_timings = []

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as async_client:

        async def fetch_feed(idx: int):
            t_start = time.perf_counter()
            resp = await async_client.get(f"/feed?limit=5")
            t_end = time.perf_counter()
            assert resp.status_code == 200
            duration = t_end - t_start
            request_timings.append((idx, t_start, t_end, duration))
            return resp.json()

        wall_start = time.perf_counter()
        results = await asyncio.gather(
            fetch_feed(1),
            fetch_feed(2),
            fetch_feed(3),
            fetch_feed(4),
        )
        wall_end = time.perf_counter()
        total_wall_time = wall_end - wall_start

    # Check that all 4 requests succeeded
    assert len(results) == 4
    for res in results:
        assert len(res["items"]) == 5

    # If sequential, 4 * 80ms = 320ms. Concurrency ensures total wall time is significantly less.
    sequential_minimum = (4 * delay_ms) / 1000.0  # 0.32s
    assert total_wall_time < sequential_minimum * 0.85, (
        f"Expected concurrent execution under {sequential_minimum * 0.85:.3f}s, "
        f"got wall time {total_wall_time:.3f}s"
    )

    # Verify that requests overlapped: at least one request started before another finished
    starts = [t[1] for t in request_timings]
    ends = [t[2] for t in request_timings]
    min_end = min(ends)
    max_start = max(starts)
    # The last request started before the first request ended (showing complete overlap)
    assert max_start < min_end + 0.05, "Requests should have overlapping execution windows"


@pytest.mark.asyncio
async def test_repository_simulated_io_non_blocking():
    """Verify repository list_original_feed non-blocking sleep concurrency."""
    repo = FixtureRepository(simulated_io_ms=50)

    t0 = time.perf_counter()
    results = await asyncio.gather(
        repo.list_original_feed(None, 5, "viewer1"),
        repo.list_original_feed(None, 5, "viewer2"),
        repo.list_original_feed(None, 5, "viewer3"),
    )
    total_time = time.perf_counter() - t0

    assert len(results) == 3
    # 3 * 50ms = 150ms sequential. Concurrent should finish in < 120ms.
    assert total_time < 0.13, f"Concurrent repository calls took {total_time:.3f}s, expected < 0.13s"
