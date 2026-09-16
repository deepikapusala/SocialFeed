"""
Request ID Middleware and Context Tracking (Stage A).

Ensures every incoming HTTP request is assigned a unique X-Request-Id:
- Preserves client-supplied X-Request-Id header if valid.
- Generates a new UUID v4 if absent.
- Stores request ID in contextvars for downstream access (e.g. error handlers, logs).
- Attaches X-Request-Id to response headers.
"""

import uuid
from contextvars import ContextVar
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


REQUEST_ID_HEADER = "X-Request-Id"
MAX_REQUEST_ID_LENGTH = 128

# Task-local context variable for request ID tracking
_request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


def get_current_request_id() -> str:
    """
    Returns the active request ID for the current async task context,
    or generates a fallback UUID if accessed outside a request.
    """
    req_id = _request_id_ctx_var.get()
    return req_id if req_id else str(uuid.uuid4())


def set_current_request_id(req_id: str) -> None:
    """
    Sets the active request ID for the current async task context.
    """
    _request_id_ctx_var.set(req_id)


import re

REQUEST_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.:]{1,128}$")


def sanitize_or_generate_request_id(incoming_header: str | None) -> str:
    """
    Validates an incoming X-Request-Id header (safe ASCII token 1-128 chars)
    or generates a fresh UUID4.
    """
    if incoming_header:
        cleaned = incoming_header.strip()
        if REQUEST_ID_PATTERN.match(cleaned):
            return cleaned
    return str(uuid.uuid4())


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Starlette/FastAPI Middleware for X-Request-Id handling.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        raw_header = request.headers.get(REQUEST_ID_HEADER)
        request_id = sanitize_or_generate_request_id(raw_header)

        # 1. Set contextvar for task-level access
        token = _request_id_ctx_var.set(request_id)

        # 2. Attach to request.state
        request.state.request_id = request_id

        try:
            # 3. Process downstream request
            response = await call_next(request)
        finally:
            # Reset contextvar token
            _request_id_ctx_var.reset(token)

        # 4. Attach X-Request-Id to outgoing response
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
