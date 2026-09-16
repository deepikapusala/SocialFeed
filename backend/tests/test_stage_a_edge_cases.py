"""
Comprehensive Stage A Edge Cases and Validation Tests.

Covers:
- Oversized cursor in /feed query param (> 1024 chars) -> 400
- Request ID > 128 chars replaced with newly generated valid UUID
- Request ID with invalid chars sanitized/replaced
- Exact error envelope contract on all error paths
- Exact camelCase wire format on /posts/{id} and /users/{id}
"""

import uuid
from fastapi.testclient import TestClient
from app.common.middleware import REQUEST_ID_HEADER, sanitize_or_generate_request_id


def test_feed_oversized_cursor_in_query_param(client: TestClient):
    """Verify that a cursor parameter exceeding 1024 characters returns HTTP 400."""
    oversized = "a" * 1025
    response = client.get(f"/feed?cursor={oversized}")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "requestId" in data


def test_request_id_too_long_sanitized():
    """Verify that a client-supplied request ID exceeding 128 chars is replaced with a generated UUID."""
    too_long = "a" * 129
    sanitized = sanitize_or_generate_request_id(too_long)
    assert sanitized != too_long
    assert len(sanitized) <= 64
    uuid.UUID(sanitized)  # Must be valid UUID format


def test_request_id_invalid_characters_sanitized():
    """Verify that a client-supplied request ID with invalid header chars is replaced with a generated UUID."""
    invalid_chars = "bad\nid\r\nwith;characters"
    sanitized = sanitize_or_generate_request_id(invalid_chars)
    assert sanitized != invalid_chars
    uuid.UUID(sanitized)


def test_request_id_in_error_envelope_matches_header(client: TestClient):
    """Verify X-Request-Id header and error body requestId always match identically."""
    custom_id = "trace-err-test-456"
    response = client.get("/posts/not-a-uuid", headers={REQUEST_ID_HEADER: custom_id})
    assert response.status_code == 400
    assert response.headers[REQUEST_ID_HEADER] == custom_id
    body = response.json()
    assert body["requestId"] == custom_id


def test_post_detail_exact_camelcase_contract(client: TestClient):
    """Verify GET /posts/{id} returns exact camelCase item envelope."""
    post_id = "11111111-1111-4111-8111-111111111101"
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert "item" in data
    item = data["item"]
    assert item["id"] == post_id
    assert "kind" in item
    assert "text" in item
    assert "createdAt" in item
    assert "author" in item
    assert "media" in item
    assert "likeCount" in item
    assert "replyCount" in item
    assert "likedByViewer" in item
    assert "replyToId" in item
    assert "repostOfId" in item

    # Author shape
    author = item["author"]
    assert "id" in author
    assert "handle" in author
    assert "displayName" in author
    assert "avatar" in author

    # Media shape
    if item["media"]:
        m = item["media"][0]
        assert "id" in m
        assert "altText" in m
        assert "width" in m
        assert "height" in m
        assert "position" in m
        assert "smallUrl" in m
        assert "largeUrl" in m


def test_user_profile_exact_camelcase_contract(client: TestClient):
    """Verify GET /users/{id} returns exact camelCase item envelope with stats."""
    user_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "item" in data
    item = data["item"]
    assert item["id"] == user_id
    assert item["handle"] == "asha"
    assert "displayName" in item
    assert "bio" in item
    assert "avatar" in item
    assert "postCount" in item
    assert "followerCount" in item
    assert "followingCount" in item
