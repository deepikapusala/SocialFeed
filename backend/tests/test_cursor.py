"""
Tests for Opaque Cursor Encoding and Decoding (Stage A).
"""

import uuid
from datetime import datetime, timezone
import pytest

from app.common.cursor import encode_cursor, decode_cursor, InvalidCursorError


def test_cursor_round_trip_success():
    """Verify that a valid (createdAt, id) tuple survives encode and decode intact."""
    dt = datetime(2026, 9, 1, 10, 30, 45, 123000, tzinfo=timezone.utc)
    item_id = "11111111-1111-4111-8111-111111111111"

    token = encode_cursor(dt, item_id)
    assert isinstance(token, str)
    assert len(token) > 0
    assert "=" not in token  # Stripped padding for clean URL safety

    decoded_dt, decoded_id = decode_cursor(token)
    assert decoded_dt == dt
    assert decoded_id == item_id


def test_cursor_version_one():
    """Verify that the cursor payload structure explicitly uses version 1."""
    import base64
    import json

    dt = datetime(2026, 9, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    item_id = str(uuid.uuid4())
    token = encode_cursor(dt, item_id)

    # Decode raw base64 JSON
    padding = "=" * ((4 - len(token) % 4) % 4)
    raw_json = base64.urlsafe_b64decode((token + padding).encode("ascii")).decode("utf-8")
    payload = json.loads(raw_json)

    assert payload["v"] == 1
    assert payload["id"] == item_id
    assert payload["createdAt"].endswith("Z")


def test_cursor_rejects_unsupported_version():
    """Verify that version != 1 is rejected with InvalidCursorError."""
    import base64
    import json

    bad_payload = {
        "v": 2,
        "createdAt": "2026-09-01T10:00:00.000Z",
        "id": "11111111-1111-4111-8111-111111111111",
    }
    raw_bytes = json.dumps(bad_payload).encode("utf-8")
    token = base64.urlsafe_b64encode(raw_bytes).decode("ascii")

    with pytest.raises(InvalidCursorError, match="Unsupported cursor version"):
        decode_cursor(token)


def test_cursor_rejects_malformed_base64():
    """Verify that invalid base64 encoding raises InvalidCursorError."""
    with pytest.raises(InvalidCursorError, match="Malformed cursor encoding"):
        decode_cursor("%%%not-valid-base64%%%")


def test_cursor_rejects_malformed_json():
    """Verify that base64 containing non-JSON bytes raises InvalidCursorError."""
    import base64
    token = base64.urlsafe_b64encode(b"not a json string").decode("ascii")

    with pytest.raises(InvalidCursorError, match="Malformed cursor encoding"):
        decode_cursor(token)


def test_cursor_rejects_missing_fields():
    """Verify missing createdAt or id fields are rejected."""
    import base64
    import json

    # Missing id
    payload1 = {"v": 1, "createdAt": "2026-09-01T10:00:00.000Z"}
    token1 = base64.urlsafe_b64encode(json.dumps(payload1).encode("utf-8")).decode("ascii")
    with pytest.raises(InvalidCursorError, match="missing required 'id'"):
        decode_cursor(token1)

    # Missing createdAt
    payload2 = {"v": 1, "id": "11111111-1111-4111-8111-111111111111"}
    token2 = base64.urlsafe_b64encode(json.dumps(payload2).encode("utf-8")).decode("ascii")
    with pytest.raises(InvalidCursorError, match="missing required 'createdAt'"):
        decode_cursor(token2)


def test_cursor_rejects_invalid_uuid():
    """Verify that a non-UUID id string is rejected."""
    import base64
    import json

    payload = {
        "v": 1,
        "createdAt": "2026-09-01T10:00:00.000Z",
        "id": "not-a-valid-uuid",
    }
    token = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    with pytest.raises(InvalidCursorError, match="Invalid UUID in cursor"):
        decode_cursor(token)


def test_cursor_rejects_invalid_timestamp():
    """Verify that a malformed timestamp string is rejected."""
    import base64
    import json

    payload = {
        "v": 1,
        "createdAt": "not-a-timestamp",
        "id": "11111111-1111-4111-8111-111111111111",
    }
    token = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    with pytest.raises(InvalidCursorError, match="Invalid timestamp format"):
        decode_cursor(token)


def test_cursor_rejects_oversized_string():
    """Verify that cursor string exceeding 1024 characters is rejected."""
    oversized = "a" * 1025
    with pytest.raises(InvalidCursorError, match="exceeds maximum allowed limit"):
        decode_cursor(oversized)


def test_cursor_rejects_empty_input():
    """Verify empty or whitespace strings are rejected."""
    with pytest.raises(InvalidCursorError, match="non-empty string"):
        decode_cursor("")

    with pytest.raises(InvalidCursorError, match="non-empty string"):
        decode_cursor("   ")
