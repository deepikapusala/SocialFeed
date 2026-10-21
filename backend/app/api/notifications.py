"""
Notifications Router (Stage 6 PY-P0-06).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.common.dependencies import get_required_actor_id, get_repository
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.notification import MarkReadResponse, NotificationListResponse
from app.services.social_service import SocialService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    cursor: Optional[str] = Query(None, description="Opaque pagination cursor token"),
    limit: int = Query(10, description="Page size (1-50)"),
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_required_actor_id),
) -> NotificationListResponse:
    """
    Retrieves newest-first cursor-paginated notification inbox for current authenticated member.
    """
    service = SocialService(repo)
    return await service.list_notifications(
        recipient_id=actor_id,
        cursor_str=cursor,
        limit=limit,
    )


@router.post("/read", response_model=MarkReadResponse)
async def mark_all_read(
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_required_actor_id),
) -> MarkReadResponse:
    """
    Marks all eligible unread notifications for current authenticated member as read.
    """
    service = SocialService(repo)
    return await service.mark_notifications_read(recipient_id=actor_id)


@router.post("/{id}/read", response_model=MarkReadResponse)
async def mark_single_read(
    id: str,
    repo: SocialRepositoryProtocol = Depends(get_repository),
    actor_id: str = Depends(get_required_actor_id),
) -> MarkReadResponse:
    """
    Marks single notification as read. Rejects cross-user access with 403 Forbidden.
    """
    service = SocialService(repo)
    return await service.mark_notifications_read(
        recipient_id=actor_id,
        notification_id=id,
    )

