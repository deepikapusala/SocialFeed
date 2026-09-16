"""
Health Check Schema (Stage A).
"""

from app.schemas.common import CamelModel


class HealthResponse(CamelModel):
    """
    Response schema for GET /health/live.
    """
    status: str = "ok"
