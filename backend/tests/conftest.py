"""
Pytest configuration and shared fixtures for FastAPI application tests (Stage A & C).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.common.dependencies import get_repository, get_fixture_repository


@pytest.fixture
def app():
    """Returns a fresh FastAPI application instance configured for tests."""
    application = create_app()
    # Default repository for Stage A unit tests is the deterministic FixtureRepository
    application.dependency_overrides[get_repository] = get_fixture_repository
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Provides a TestClient for synchronous API testing."""
    with TestClient(app) as test_client:
        yield test_client
