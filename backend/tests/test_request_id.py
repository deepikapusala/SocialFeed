"""
Tests for Request ID Generation, Propagation, and Middleware (Stage A).
"""

import uuid
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.common.middleware import (
    RequestIdMiddleware,
    REQUEST_ID_HEADER,
    get_current_request_id,
    set_current_request_id,
    sanitize_or_generate_request_id,
)


def test_sanitize_or_generate_request_id():
    """Verify UUID generation when header is absent or empty, and preservation when present."""
    # When None or empty
    id1 = sanitize_or_generate_request_id(None)
    assert len(id1) > 0
    uuid.UUID(id1)  # Asserts valid UUID format

    id2 = sanitize_or_generate_request_id("   ")
    assert len(id2) > 0
    uuid.UUID(id2)

    # When valid client header supplied
    client_id = "custom-client-trace-12345"
    id3 = sanitize_or_generate_request_id(client_id)
    assert id3 == client_id


def test_contextvar_request_id():
    """Verify contextvar get/set behavior."""
    test_id = "task-local-uuid-999"
    set_current_request_id(test_id)
    assert get_current_request_id() == test_id


def test_middleware_generates_request_id_when_absent():
    """Verify middleware generates an X-Request-Id header when client does not send one."""
    async def sample_endpoint(request):
        req_id = getattr(request.state, "request_id", None)
        return JSONResponse({"captured_id": req_id})

    app = Starlette(routes=[Route("/test", sample_endpoint)])
    app.add_middleware(RequestIdMiddleware)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers

    header_id = response.headers[REQUEST_ID_HEADER]
    assert len(header_id) > 0
    uuid.UUID(header_id)  # Validate generated format

    # Confirm the endpoint handler saw the same request ID
    body = response.json()
    assert body["captured_id"] == header_id


def test_middleware_preserves_incoming_request_id():
    """Verify middleware preserves a client-supplied X-Request-Id header."""
    async def sample_endpoint(request):
        req_id = getattr(request.state, "request_id", None)
        return JSONResponse({"captured_id": req_id})

    app = Starlette(routes=[Route("/test", sample_endpoint)])
    app.add_middleware(RequestIdMiddleware)

    client = TestClient(app)
    client_supplied_id = "client-trace-abc-123"
    response = client.get("/test", headers={REQUEST_ID_HEADER: client_supplied_id})

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == client_supplied_id
    assert response.json()["captured_id"] == client_supplied_id
