"""
Posts Router (Stage A & C).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.common.dependencies import get_current_actor_id, get_repository
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.common import PaginatedResponse
from app.schemas.post import (
    CreatePostRequest,
    LikeResponse,
    PostDetailResponse,
    PostItem,
    RepostResponse,
)
from app.services.social_service import SocialService

router = APIRouter(tags=["posts"])


@router.get("/posts/{id}", response_model=PostDetailResponse)
async def get_post_detail(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    viewer_id: str = Depends(get_current_actor_id),
) -> PostDetailResponse:
    """
    Retrieve single post detail by UUID.
    """
    service = SocialService(repo)
    return await service.get_post_detail(post_id=id, viewer_id=viewer_id)


@router.get("/posts/{id}/replies", response_model=PaginatedResponse[PostItem])
async def list_direct_replies(
    id: str,
    cursor: Optional[str] = Query(None, description="Opaque pagination cursor token"),
    limit: int = Query(10, description="Page size (1-50)"),
    repo: SocialRepositoryProtocol = Depends(get_repository),
    viewer_id: str = Depends(get_current_actor_id),
) -> PaginatedResponse[PostItem]:
    """
    Retrieve paginated direct replies for an original post.
    """
    service = SocialService(repo)
    return await service.list_direct_replies(
        post_id=id,
        cursor_str=cursor,
        limit=limit,
        viewer_id=viewer_id,
    )


@router.post("/posts", response_model=PostDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_current_actor_id),
) -> PostDetailResponse:
    """
    Creates a new post (original, reply, or repost) authored by the demo actor.
    """
    service = SocialService(repo)
    return await service.create_post(
        author_id=actor_id,
        kind=request.kind,
        text=request.text,
        reply_to_id=request.reply_to_id,
        repost_of_id=request.repost_of_id,
        media=request.media,
    )


@router.put("/posts/{id}/like", response_model=LikeResponse)
@router.post("/posts/{id}/like", response_model=LikeResponse)
async def set_post_like(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_current_actor_id),
) -> LikeResponse:
    """
    Sets desired liked state for the current viewer.
    """
    service = SocialService(repo)
    return await service.set_like(user_id=actor_id, post_id=id)


@router.delete("/posts/{id}/like", response_model=LikeResponse)
async def remove_post_like(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_current_actor_id),
) -> LikeResponse:
    """
    Removes like from post for the current viewer.
    """
    service = SocialService(repo)
    return await service.remove_like(user_id=actor_id, post_id=id)


@router.post("/posts/{id}/repost", response_model=RepostResponse)
@router.put("/posts/{id}/repost", response_model=RepostResponse)
async def create_post_repost(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_current_actor_id),
) -> RepostResponse:
    """
    Creates a repost for the current viewer on target original post.
    """
    service = SocialService(repo)
    return await service.create_repost(user_id=actor_id, post_id=id)


@router.delete("/posts/{id}/repost", response_model=RepostResponse)
async def remove_post_repost(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_current_actor_id),
) -> RepostResponse:
    """
    Removes repost for the current viewer on target original post.
    """
    service = SocialService(repo)
    return await service.remove_repost(user_id=actor_id, post_id=id)
