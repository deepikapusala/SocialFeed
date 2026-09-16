"""
Raw ASGI Application Lab (A1)

A minimal ASGI 3.0 compliant application callable:
  async def app(scope, receive, send)

This demonstrates the low-level ASGI request lifecycle without any web framework.
"""

import json
from typing import Callable, Dict, Any, List, Tuple


async def handle_lifespan(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    """
    Handles the ASGI lifespan protocol to allow clean server startup and shutdown.
    """
    while True:
        message = await receive()
        message_type = message.get("type")

        if message_type == "lifespan.startup":
            # Initialization logic if any (no heavy work or database connections in toy lab)
            await send({"type": "lifespan.startup.complete"})

        elif message_type == "lifespan.shutdown":
            # Cleanup logic if any
            await send({"type": "lifespan.shutdown.complete"})
            return


async def handle_http(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    """
    Handles incoming HTTP requests based on the ASGI HTTP connection scope.
    """
    method: str = scope.get("method", "GET").upper()
    path: str = scope.get("path", "")

    # Drain any incoming request body (if present)
    more_body = True
    while more_body:
        message = await receive()
        more_body = message.get("more_body", False)

    # Route matching
    if method == "GET" and path == "/health/live":
        status_code = 200
        payload = {"status": "ok"}

    elif method == "GET" and path == "/feed":
        status_code = 200
        payload = {
            "items": [
                {
                    "id": "toy-post-1",
                    "text": "Raw ASGI demo post 1",
                    "kind": "original",
                },
                {
                    "id": "toy-post-2",
                    "text": "Raw ASGI demo post 2",
                    "kind": "original",
                },
            ],
            "message": "Raw ASGI toy feed demonstration (Stage A1)",
        }

    else:
        status_code = 404
        payload = {
            "error": "Not Found",
            "path": path,
        }

    # Encode JSON payload
    body_bytes = json.dumps(payload, indent=2).encode("utf-8")

    # Construct response headers
    headers: List[Tuple[bytes, bytes]] = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"content-length", str(len(body_bytes)).encode("ascii")),
    ]

    # Step 1: Send HTTP response start message
    await send({
        "type": "http.response.start",
        "status": status_code,
        "headers": headers,
    })

    # Step 2: Send HTTP response body message
    await send({
        "type": "http.response.body",
        "body": body_bytes,
        "more_body": False,
    })


async def app(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    """
    Main ASGI 3.0 entry point.
    """
    scope_type = scope.get("type")

    if scope_type == "lifespan":
        await handle_lifespan(scope, receive, send)

    elif scope_type == "http":
        await handle_http(scope, receive, send)

    else:
        # Unsupported scope type (e.g. websocket in this minimal lab)
        pass
