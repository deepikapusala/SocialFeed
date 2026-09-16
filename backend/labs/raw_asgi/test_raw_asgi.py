"""
Tests for Raw ASGI Lab (A1)

Directly exercises the raw ASGI callable (scope, receive, send) to verify:
1. HTTP GET /health/live
2. HTTP GET /feed
3. HTTP 404 for unknown routes
4. HTTP response start and body message formats & headers
5. Lifespan startup and shutdown event handling
"""

import asyncio
import json
from typing import Dict, Any, List, Tuple

# Support both direct script execution and pytest invocation
try:
    from labs.raw_asgi.app import app
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from labs.raw_asgi.app import app


async def call_asgi_http(method: str, path: str, headers: List[Tuple[bytes, bytes]] = None) -> Tuple[int, Dict[bytes, bytes], bytes]:
    """
    Simulates an ASGI HTTP request cycle against the raw ASGI app.
    Returns (status_code, headers_dict, body_bytes).
    """
    if headers is None:
        headers = []

    scope: Dict[str, Any] = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method.upper(),
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers,
    }

    async def mock_receive() -> Dict[str, Any]:
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    sent_messages: List[Dict[str, Any]] = []

    async def mock_send(message: Dict[str, Any]) -> None:
        sent_messages.append(message)

    await app(scope, mock_receive, mock_send)

    assert len(sent_messages) == 2, f"Expected 2 ASGI messages, got {len(sent_messages)}"
    start_msg, body_msg = sent_messages[0], sent_messages[1]

    assert start_msg["type"] == "http.response.start"
    assert body_msg["type"] == "http.response.body"

    status_code = start_msg["status"]
    headers_dict = dict(start_msg.get("headers", []))
    body = body_msg["body"]

    return status_code, headers_dict, body


# ---------------------------------------------------------------------------
# Test 1: GET /health/live
# ---------------------------------------------------------------------------
def test_health_live():
    status, headers, body = asyncio.run(call_asgi_http("GET", "/health/live"))
    assert status == 200
    assert b"content-type" in headers
    assert b"application/json" in headers[b"content-type"]

    data = json.loads(body.decode("utf-8"))
    assert data == {"status": "ok"}


# ---------------------------------------------------------------------------
# Test 2: GET /feed
# ---------------------------------------------------------------------------
def test_feed():
    status, headers, body = asyncio.run(call_asgi_http("GET", "/feed"))
    assert status == 200
    assert b"content-type" in headers

    data = json.loads(body.decode("utf-8"))
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "toy-post-1"


# ---------------------------------------------------------------------------
# Test 3: Unknown route returns 404
# ---------------------------------------------------------------------------
def test_not_found():
    status, headers, body = asyncio.run(call_asgi_http("GET", "/unknown/route"))
    assert status == 404
    assert b"content-type" in headers

    data = json.loads(body.decode("utf-8"))
    assert data.get("error") == "Not Found"
    assert data.get("path") == "/unknown/route"


# ---------------------------------------------------------------------------
# Test 4: Unsupported method on valid route returns 404
# ---------------------------------------------------------------------------
def test_unsupported_method():
    status, headers, body = asyncio.run(call_asgi_http("POST", "/health/live"))
    assert status == 404
    data = json.loads(body.decode("utf-8"))
    assert data.get("error") == "Not Found"


# ---------------------------------------------------------------------------
# Test 5: Lifespan startup and shutdown handshake
# ---------------------------------------------------------------------------
def test_lifespan_lifecycle():
    scope: Dict[str, Any] = {
        "type": "lifespan",
        "asgi": {"version": "3.0", "spec_version": "2.0"},
    }

    incoming_queue = asyncio.Queue()
    outgoing_messages = []

    async def mock_receive():
        return await incoming_queue.get()

    async def mock_send(message):
        outgoing_messages.append(message)

    async def run_lifespan_test():
        # Start app task
        task = asyncio.create_task(app(scope, mock_receive, mock_send))

        # 1. Send startup event
        await incoming_queue.put({"type": "lifespan.startup"})
        await asyncio.sleep(0.01)

        assert len(outgoing_messages) == 1
        assert outgoing_messages[0]["type"] == "lifespan.startup.complete"

        # 2. Send shutdown event
        await incoming_queue.put({"type": "lifespan.shutdown"})
        await asyncio.wait_for(task, timeout=1.0)

        assert len(outgoing_messages) == 2
        assert outgoing_messages[1]["type"] == "lifespan.shutdown.complete"

    asyncio.run(run_lifespan_test())


# ---------------------------------------------------------------------------
# Test 6: Message formatting verification
# ---------------------------------------------------------------------------
def test_asgi_message_sequence():
    status, headers, body = asyncio.run(call_asgi_http("GET", "/health/live"))
    assert status == 200
    assert headers[b"content-length"] == str(len(body)).encode("ascii")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Raw ASGI Lab Tests...")
    print("=" * 60)
    test_health_live()
    print("  [PASS] test_health_live")
    test_feed()
    print("  [PASS] test_feed")
    test_not_found()
    print("  [PASS] test_not_found")
    test_unsupported_method()
    print("  [PASS] test_unsupported_method")
    test_lifespan_lifecycle()
    print("  [PASS] test_lifespan_lifecycle")
    test_asgi_message_sequence()
    print("  [PASS] test_asgi_message_sequence")
    print("=" * 60)
    print("ALL RAW ASGI LAB TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
