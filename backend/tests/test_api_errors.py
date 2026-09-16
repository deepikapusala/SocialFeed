"""
Tests for global API error handling and envelope formatting (Stage A).
"""

from fastapi.testclient import TestClient
from app.common.dependencies import get_repository


def test_error_envelope_structure_on_404(client: TestClient):
    res = client.get("/posts/aaaaaaaa-aaaa-4aaa-8aaa-999999999999")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert "requestId" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert isinstance(data["error"]["message"], str)
    assert isinstance(data["error"]["details"], list)
    assert res.headers["X-Request-Id"] == data["requestId"]


def test_error_envelope_preserves_supplied_request_id(client: TestClient):
    custom_id = "custom-test-request-id-12345"
    res = client.get(
        "/posts/not-a-valid-uuid",
        headers={"X-Request-Id": custom_id},
    )
    assert res.status_code == 400
    data = res.json()
    assert data["requestId"] == custom_id
    assert res.headers["X-Request-Id"] == custom_id
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_unknown_path_returns_404_in_standard_envelope(client: TestClient):
    res = client.get("/non-existent-route")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert "requestId" in data
    assert "X-Request-Id" in res.headers


def test_unexpected_exception_mapped_to_500_internal_error(app):
    # Simulate an unexpected bug in repository by overriding it with a broken provider
    class BrokenRepo:
        async def list_original_feed(self, *args, **kwargs):
            raise RuntimeError("Secret database connection string in stack trace: postgres://root:secret@localhost:5432")

    app.dependency_overrides[get_repository] = lambda: BrokenRepo()

    # Disable raise_server_exceptions so TestClient returns the 500 response rather than raising in-test
    no_raise_client = TestClient(app, raise_server_exceptions=False)
    res = no_raise_client.get("/feed")
    assert res.status_code == 500
    data = res.json()
    assert data["error"]["code"] == "INTERNAL_ERROR"
    assert data["error"]["message"] == "An internal server error occurred"
    # Ensure sensitive runtime info/stack trace is not leaked
    assert "Secret database connection string" not in str(data)
    assert "requestId" in data
    assert "X-Request-Id" in res.headers
