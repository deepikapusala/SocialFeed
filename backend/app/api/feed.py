"""
Feed Router (Stage A).
"""

from typing import Optional
from urllib.parse import parse_qsl
from fastapi import APIRouter, Depends, Query, Request
from app.common.dependencies import get_current_actor_id, get_repository
from app.common.errors import ValidationError
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.post import FeedResponse
from app.services.feed_service import FeedService

router = APIRouter(tags=["feed"])

ALLOWED_FEED_PARAMS = {"cursor", "limit"}


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    request: Request,
    cursor: Optional[str] = Query(None, description="Opaque pagination cursor token"),
    limit: int = Query(10, description="Page size (1-50)"),
    repo: SocialRepositoryProtocol = Depends(get_repository),
    viewer_id: str = Depends(get_current_actor_id),
) -> FeedResponse:
    """
    Retrieve paginated original-post chronological feed.
    """
    raw_query = request.scope.get("query_string", b"").decode("latin-1")
    if raw_query:
        pairs = parse_qsl(raw_query, keep_blank_values=True)
        seen_keys = set()
        for key, _ in pairs:
            if key == "page":
                raise ValidationError(
                    "Legacy parameter 'page' is not supported. Use cursor pagination.",
                    details=[{"field": "page", "reason": "unsupported_parameter"}],
                    status_code=400,
                )
            if key not in ALLOWED_FEED_PARAMS:
                raise ValidationError(
                    f"Unknown query parameter '{key}'.",
                    details=[{"field": key, "reason": "unknown_parameter"}],
                    status_code=400,
                )
            if key in seen_keys:
                raise ValidationError(
                    f"Duplicate query parameter '{key}'.",
                    details=[{"field": key, "reason": "duplicate_parameter"}],
                    status_code=400,
                )
            seen_keys.add(key)

    service = FeedService(repo)
    return await service.get_feed(
        cursor_str=cursor,
        limit=limit,
        viewer_id=viewer_id,
    )
