"""
Health Check Router (Stage A & C).
"""

from fastapi import APIRouter, Response, status
from app.database import check_database_connectivity
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=HealthResponse)
async def get_health_live() -> HealthResponse:
    """
    Liveness probe returning HTTP 200 and {"status": "ok"}.
    Does not depend on any database.
    """
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
async def get_health_ready(response: Response) -> HealthResponse:
    """
    Readiness probe performing bounded database connectivity check against instagram_modeling.
    Returns HTTP 200 {"status": "ready"} if reachable, 503 {"status": "unavailable"} if unreachable.
    """
    is_ready = await check_database_connectivity()
    if is_ready:
        return HealthResponse(status="ready")
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status="unavailable")
