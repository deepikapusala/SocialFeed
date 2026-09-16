"""
Tests for GET /health/live endpoint.
"""

from fastapi.testclient import TestClient


def test_health_live_success(client: TestClient):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-Id" in response.headers


def test_health_live_does_not_require_db(client: TestClient):
    # Liveness is purely in-memory and returns immediately
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
