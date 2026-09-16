"""
Search Router (Stage A & C).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.common.dependencies import get_current_actor_id, get_repository
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.post import FeedResponse
from app.services.social_service import SocialService

router = APIRouter(tags=["search"])


@router.get("/search/posts", response_model=FeedResponse)
@router.get("/search", response_model=FeedResponse)
async def search_posts(
    q: str = Query(..., min_length=2, max_length=80, description="Literal substring query"),
    cursor: Optional[str] = Query(None, description="Opaque pagination cursor token"),
    limit: int = Query(10, description="Page size (1-50)"),
    repo: SocialRepositoryProtocol = Depends(get_repository),
    viewer_id: str = Depends(get_current_actor_id),
) -> FeedResponse:
    """
    Search original posts by literal substring match with cursor pagination.
    """
    service = SocialService(repo)
    return await service.search_originals(
        query=q,
        cursor_str=cursor,
        limit=limit,
        viewer_id=viewer_id,
    )
