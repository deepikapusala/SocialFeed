"""
Tests for OpenAPI Documentation and Schema Contracts (Stage A).

Verifies:
- OpenAPI JSON endpoint (/openapi.json) is accessible and valid.
- Swagger docs UI (/docs) is accessible.
- All four Stage A routes are registered in the OpenAPI specification.
- Response models conform to Stage A contracts.
"""

from fastapi.testclient import TestClient


def test_openapi_schema_endpoint(client: TestClient):
    """Verify /openapi.json returns valid OpenAPI 3.x document."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert schema["info"]["title"] == "Instagram Clone API"

    paths = schema["paths"]
    # All 4 Stage A endpoints must be documented
    assert "/health/live" in paths
    assert "/feed" in paths
    assert "/posts/{id}" in paths
    assert "/users/{id}" in paths


def test_docs_ui_endpoint(client: TestClient):
    """Verify Swagger UI /docs endpoint is reachable."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


def test_openapi_feed_response_model(client: TestClient):
    """Verify /feed response model is documented with correct schemas."""
    response = client.get("/openapi.json")
    schema = response.json()
    feed_path = schema["paths"]["/feed"]["get"]
    assert "200" in feed_path["responses"]
    responses_200 = feed_path["responses"]["200"]
    assert "content" in responses_200
    assert "application/json" in responses_200["content"]
