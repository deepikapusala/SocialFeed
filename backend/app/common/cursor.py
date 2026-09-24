"""
Opaque Cursor Utilities for Pagination (Stage A).

Implements base64url-encoded JSON tokens representing:
{
  "v": 1,
  "createdAt": "2026-09-01T10:00:00.000Z",
  "id": "11111111-1111-4111-8111-111111111111"
}
"""

import base64
import json
import uuid
from datetime import datetime, timezone
from typing import Tuple


MAX_CURSOR_LENGTH = 1024
SUPPORTED_CURSOR_VERSION = 1

  
class InvalidCursorError(ValueError):
    """Raised when a cursor string cannot be decoded or fails validation."""
    pass


def encode_cursor(created_at: datetime, item_id: str) -> str:
    """
    Encodes a (createdAt, id) tuple into a base64url opaque cursor string.
    
    Ensures timestamps are formatted in UTC with millisecond precision:
    YYYY-MM-DDTHH:MM:SS.sssZ
    """
    if isinstance(created_at, str):
        clean_str = created_at.replace("Z", "+00:00")
        created_at = datetime.fromisoformat(clean_str)

    # Ensure datetime is timezone-aware UTC
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    else:
        created_at = created_at.astimezone(timezone.utc)

    # Format timestamp to ISO 8601 UTC with milliseconds and trailing 'Z'
    # e.g., 2026-09-01T10:00:00.000Z
    iso_str = created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Validate item_id is a valid UUID
    try:
        valid_uuid = str(uuid.UUID(str(item_id))).lower()
    except (ValueError, AttributeError):
        raise InvalidCursorError(f"Invalid UUID for cursor: '{item_id}'")

    payload = {
        "v": SUPPORTED_CURSOR_VERSION,
        "createdAt": iso_str,
        "id": valid_uuid,
    }

    raw_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    raw_bytes = raw_json.encode("utf-8")

    # Base64url encode and strip trailing '=' padding for clean URL-safe token
    encoded_str = base64.urlsafe_b64encode(raw_bytes).decode("ascii").rstrip("=")

    if len(encoded_str) > MAX_CURSOR_LENGTH:
        raise InvalidCursorError(f"Generated cursor exceeds maximum length of {MAX_CURSOR_LENGTH} characters.")

    return encoded_str


def decode_cursor(cursor_str: str) -> Tuple[datetime, str]:
    """
    Decodes and validates an opaque cursor string into a (createdAt, id) tuple.
    
    Raises InvalidCursorError on:
    - Empty or non-string input
    - Length exceeding 1024 characters
    - Invalid base64url encoding
    - Invalid JSON payload
    - Missing required fields
    - Unsupported version (not 1)
    - Invalid ISO-8601 UTC timestamp
    - Invalid UUID string
    """
    if not isinstance(cursor_str, str) or not cursor_str.strip():
        raise InvalidCursorError("Cursor must be a non-empty string.")

    cursor_clean = cursor_str.strip()

    if len(cursor_clean) > MAX_CURSOR_LENGTH:
        raise InvalidCursorError(f"Cursor length exceeds maximum allowed limit of {MAX_CURSOR_LENGTH} characters.")

    # Restore base64 padding if stripped
    missing_padding = len(cursor_clean) % 4
    if missing_padding != 0:
        cursor_padded = cursor_clean + ("=" * (4 - missing_padding))
    else:
        cursor_padded = cursor_clean

    try: 
        raw_bytes = base64.urlsafe_b64decode(cursor_padded.encode("ascii"))
        raw_json = raw_bytes.decode("utf-8")
        payload = json.loads(raw_json)
    except Exception as e:
        raise InvalidCursorError(f"Malformed cursor encoding: {e}")

    if not isinstance(payload, dict):
        raise InvalidCursorError("Cursor payload must be a JSON object.")

    # Validate version
    version = payload.get("v")
    if version != SUPPORTED_CURSOR_VERSION:
        raise InvalidCursorError(f"Unsupported cursor version: {version}. Expected {SUPPORTED_CURSOR_VERSION}.")

    # Validate createdAt
    created_at_raw = payload.get("createdAt")
    if not created_at_raw or not isinstance(created_at_raw, str):
        raise InvalidCursorError("Cursor missing required 'createdAt' timestamp field.")

    try:
        # Standardize 'Z' to '+00:00' for datetime.fromisoformat
        iso_standard = created_at_raw.replace("Z", "+00:00") if created_at_raw.endswith("Z") else created_at_raw
        dt = datetime.fromisoformat(iso_standard)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
    except Exception as e:
        raise InvalidCursorError(f"Invalid timestamp format in cursor: '{created_at_raw}'. {e}")

    # Validate id
    id_raw = payload.get("id")
    if not id_raw or not isinstance(id_raw, str):
        raise InvalidCursorError("Cursor missing required 'id' UUID field.")

    try:
        uuid_obj = uuid.UUID(id_raw)
        valid_id = str(uuid_obj).lower()
    except Exception:
        raise InvalidCursorError(f"Invalid UUID in cursor: '{id_raw}'.")

    return dt, valid_id
