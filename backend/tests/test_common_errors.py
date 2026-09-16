"""
Tests for Standard Error Models and Exception Foundation (Stage A).
"""

from app.common.errors import (
    AppException,
    ValidationError,
    NotFoundError,
    ConflictError,
    ServiceUnavailableError,
    InternalServerError,
    format_error_envelope,
    CODE_VALIDATION_ERROR,
    CODE_NOT_FOUND,
    CODE_CONFLICT,
    CODE_SERVICE_UNAVAILABLE,
    CODE_INTERNAL_ERROR,
)


def test_format_error_envelope_structure():
    """Verify the error envelope matches the shared PRD schema exactly."""
    envelope = format_error_envelope(
        code=CODE_VALIDATION_ERROR,
        message="limit must be an integer from 1 to 50",
        details=[{"field": "limit", "reason": "out_of_range"}],
        request_id="test-req-123",
    )

    assert "error" in envelope
    assert "requestId" in envelope
    assert envelope["requestId"] == "test-req-123"

    error_obj = envelope["error"]
    assert error_obj["code"] == "VALIDATION_ERROR"
    assert error_obj["message"] == "limit must be an integer from 1 to 50"
    assert error_obj["details"] == [{"field": "limit", "reason": "out_of_range"}]


def test_format_error_envelope_default_details():
    """Verify that omitting details returns an empty list, not null or missing key."""
    envelope = format_error_envelope(
        code=CODE_NOT_FOUND,
        message="Post not found",
        request_id="req-456",
    )
    assert envelope["error"]["details"] == []


def test_validation_error_defaults():
    """Verify ValidationError default status code and code string."""
    err = ValidationError("Invalid query parameter")
    assert err.code == CODE_VALIDATION_ERROR
    assert err.status_code == 400
    assert err.message == "Invalid query parameter"
    assert err.details == []


def test_validation_error_domain_status():
    """Verify ValidationError allows status_code=422 for domain/body errors."""
    err = ValidationError("Invalid body", status_code=422)
    assert err.status_code == 422


def test_not_found_error():
    """Verify NotFoundError defaults to 404."""
    err = NotFoundError("User not found")
    assert err.code == CODE_NOT_FOUND
    assert err.status_code == 404
    assert err.message == "User not found"


def test_conflict_error():
    """Verify ConflictError defaults to 409."""
    err = ConflictError("Duplicate repost")
    assert err.code == CODE_CONFLICT
    assert err.status_code == 409
    assert err.message == "Duplicate repost"


def test_service_unavailable_error():
    """Verify ServiceUnavailableError defaults to 503."""
    err = ServiceUnavailableError("Database unreachable")
    assert err.code == CODE_SERVICE_UNAVAILABLE
    assert err.status_code == 503
    assert err.message == "Database unreachable"


def test_internal_server_error():
    """Verify InternalServerError defaults to 500."""
    err = InternalServerError("Unexpected failure")
    assert err.code == CODE_INTERNAL_ERROR
    assert err.status_code == 500
    assert err.message == "Unexpected failure"
