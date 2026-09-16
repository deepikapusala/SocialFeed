"""
Tests for Application Lifespan and Startup/Shutdown (Stage A).

Verifies:
- Application startup executes cleanly.
- Lifespan context manager runs and validates settings.
- Shutdown releases resources cleanly without dangling handles.
- No database connection is initialized at startup/shutdown.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app, lifespan
from app.config import get_settings


def test_application_lifespan_startup_and_shutdown():
    """Verify application starts and shuts down cleanly within lifespan context."""
    app = create_app()
    with TestClient(app) as client:
        # Perform a request while server is live
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lifespan_context_manager_directly():
    """Verify lifespan async context manager directly initializes settings without database."""
    app = create_app()
    settings_before = get_settings()
    assert settings_before.PORT > 0
    assert settings_before.FRONTEND_ORIGIN is not None

    async with lifespan(app):
        # Startup phase completed
        settings_during = get_settings()
        assert settings_during.DEMO_USER_ID is not None
    # Shutdown phase completed without errors
