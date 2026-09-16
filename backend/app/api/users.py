"""
Users Router (Stage A & C).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.common.dependencies import get_repository
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.common import PaginatedResponse
from app.schemas.media import MediaItem
from app.schemas.user import UserProfileResponse
from app.services.social_service import SocialService

router = APIRouter(tags=["users"])


@router.get("/users/{id}", response_model=UserProfileResponse)
async def get_user_profile(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
) -> UserProfileResponse:
    """
    Retrieve user profile by UUID.
    """
    service = SocialService(repo)
    return await service.get_user_profile(user_id=id)


@router.get("/users/{id}/media", response_model=PaginatedResponse[MediaItem])
async def list_profile_media(
    id: str,
    cursor: Optional[str] = Query(None, description="Opaque pagination cursor token"),
    limit: int = Query(10, description="Page size (1-50)"),
    repo: SocialRepositoryProtocol = Depends(get_repository),
) -> PaginatedResponse[MediaItem]:
    """
    Retrieve paginated media rows from a user's original posts.
    """
    service = SocialService(repo)
    return await service.list_profile_media(
        user_id=id,
        cursor_str=cursor,
        limit=limit,
    )
