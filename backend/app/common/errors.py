"""
Standard Error Model and Domain Exceptions (Stage A).

Defines the shared error envelope:
{
  "error": {
    "code": "...",
    "message": "...",
    "details": [...]
  },
  "requestId": "..."
}
"""

from typing import List, Dict, Any, Optional


# Standard Assignment Error Codes
CODE_VALIDATION_ERROR = "VALIDATION_ERROR"
CODE_NOT_FOUND = "NOT_FOUND"
CODE_CONFLICT = "CONFLICT"
CODE_SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
CODE_INTERNAL_ERROR = "INTERNAL_ERROR"


class AppException(Exception):
    """Base application exception supporting standard error envelope formatting."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


class ValidationError(AppException):
    """Raised for input validation failures (Query/Path: 400, Body/Domain: 422)."""

    def __init__(
        self,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None,
        status_code: int = 400,
    ):
        super().__init__(
            code=CODE_VALIDATION_ERROR,
            message=message,
            status_code=status_code,
            details=details,
        )


class NotFoundError(AppException):
    """Raised when a requested resource or parent does not exist (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            code=CODE_NOT_FOUND,
            message=message,
            status_code=404,
            details=details,
        )


class ConflictError(AppException):
    """Raised for unique constraint or state conflicts (409)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            code=CODE_CONFLICT,
            message=message,
            status_code=409,
            details=details,
        )


class ServiceUnavailableError(AppException):
    """Raised when a backing dependency/database is unreachable (503)."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            code=CODE_SERVICE_UNAVAILABLE,
            message=message,
            status_code=503,
            details=details,
        )


class InternalServerError(AppException):
    """Raised for unhandled internal exceptions (500)."""

    def __init__(
        self,
        message: str = "An internal server error occurred",
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            code=CODE_INTERNAL_ERROR,
            message=message,
            status_code=500,
            details=details,
        )


def format_error_envelope(
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
    request_id: str = "unknown",
) -> Dict[str, Any]:
    """
    Constructs the exact JSON dict conforming to the shared API contract error envelope.
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details if details is not None else [],
        },
        "requestId": request_id,
    }
