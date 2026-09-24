"""
Social Service (Stage A & C).

Orchestrates post detail, user profiles, direct replies, profile media,
text search across original posts, and post/like write operations.
"""

import uuid
from typing import Any, Dict, List, Optional
from app.common.cursor import decode_cursor, encode_cursor, InvalidCursorError
from app.common.errors import NotFoundError, ValidationError
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.common import PaginatedResponse
from app.schemas.media import MediaItem
from app.schemas.post import PostItem, PostDetailResponse, FeedResponse, LikeResponse, RepostResponse
from app.schemas.user import UserProfile, UserProfileResponse


class SocialService:
    """
    Application service managing posts, profiles, replies, media, search, and writes.
    """

    def __init__(self, repository: SocialRepositoryProtocol):
        self._repository = repository

    @staticmethod
    def _validate_uuid(val: str, field_name: str = "id") -> str:
        """Validates that a string is a valid UUID format."""
        try:
            return str(uuid.UUID(str(val))).lower()
        except (ValueError, AttributeError):
            raise ValidationError(
                f"Invalid UUID for '{field_name}': '{val}'",
                details=[{"field": field_name, "reason": "invalid_uuid"}],
            )

    @staticmethod
    def _validate_limit(limit: int) -> int:
        """Validates limit is an integer between 1 and 50."""
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            raise ValidationError(
                "limit must be an integer from 1 to 50",
                details=[{"field": "limit", "reason": "out_of_range"}],
            )
        return limit

    async def get_post_detail(self, post_id: str, viewer_id: str) -> PostDetailResponse:
        """
        Retrieves detail for a single post by UUID.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        raw_post = await self._repository.get_post_detail(clean_post_id, viewer_id)

        if not raw_post:
            raise NotFoundError(f"Post with id '{clean_post_id}' not found.")

        return PostDetailResponse(item=PostItem(**raw_post))

    async def get_user_profile(self, user_id: str, viewer_id: Optional[str] = None) -> UserProfileResponse:
        """
        Retrieves user profile and statistics by UUID.
        """
        clean_user_id = self._validate_uuid(user_id, "id")
        raw_user = await self._repository.get_user_profile(clean_user_id, viewer_id=viewer_id)

        if not raw_user:
            raise NotFoundError(f"User with id '{clean_user_id}' not found.")

        return UserProfileResponse(item=UserProfile(**raw_user))

    async def follow_user(self, follower_id: str, target_user_id: str) -> Dict[str, Any]:
        """
        Follows target user for the current viewer actor.
        """
        clean_target_id = self._validate_uuid(target_user_id, "id")
        is_following, follower_count = await self._repository.follow_user(follower_id, clean_target_id)
        return {
            "user_id": clean_target_id,
            "followed_by_viewer": is_following,
            "follower_count": follower_count,
        }

    async def unfollow_user(self, follower_id: str, target_user_id: str) -> Dict[str, Any]:
        """
        Unfollows target user for the current viewer actor.
        """
        clean_target_id = self._validate_uuid(target_user_id, "id")
        is_following, follower_count = await self._repository.unfollow_user(follower_id, clean_target_id)
        return {
            "user_id": clean_target_id,
            "followed_by_viewer": is_following,
            "follower_count": follower_count,
        }

    async def list_direct_replies(
        self,
        post_id: str,
        cursor_str: Optional[str],
        limit: int,
        viewer_id: str,
    ) -> PaginatedResponse[PostItem]:
        """
        Retrieves direct replies for an original post.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        clean_limit = self._validate_limit(limit)

        # Confirm post exists and is an original
        kind = await self._repository.get_post_kind(clean_post_id)
        if kind is None:
            raise NotFoundError(f"Post with id '{clean_post_id}' not found.")
        if kind != "original":
            raise ValidationError(
                f"Replies can only be listed for original posts, target is '{kind}'.",
                status_code=422,
            )

        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(f"Invalid cursor: {e}", details=[{"field": "cursor", "reason": "invalid_cursor"}])

        raw_replies = await self._repository.list_direct_replies(
            post_id=clean_post_id,
            cursor_tuple=cursor_tuple,
            limit=clean_limit,
            viewer_id=viewer_id,
        )

        if len(raw_replies) > clean_limit:
            page_records = raw_replies[:clean_limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_replies
            has_more = False
            next_cursor = None

        return PaginatedResponse[PostItem](
            items=[PostItem(**r) for r in page_records],
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def list_profile_media(
        self,
        user_id: str,
        cursor_str: Optional[str],
        limit: int,
    ) -> PaginatedResponse[MediaItem]:
        """
        Retrieves paginated media rows from a user's original posts.
        """
        clean_user_id = self._validate_uuid(user_id, "id")
        clean_limit = self._validate_limit(limit)

        exists = await self._repository.user_exists(clean_user_id)
        if not exists:
            raise NotFoundError(f"User with id '{clean_user_id}' not found.")

        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(f"Invalid cursor: {e}", details=[{"field": "cursor", "reason": "invalid_cursor"}])

        raw_media = await self._repository.list_profile_media(
            user_id=clean_user_id,
            cursor_tuple=cursor_tuple,
            limit=clean_limit,
        )

        if len(raw_media) > clean_limit:
            page_records = raw_media[:clean_limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_media
            has_more = False
            next_cursor = None

        return PaginatedResponse[MediaItem](
            items=[MediaItem(**m) for m in page_records],
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def search_originals(
        self,
        query: str,
        cursor_str: Optional[str],
        limit: int,
        viewer_id: str,
    ) -> FeedResponse:
        """
        Performs a case-insensitive literal substring search across original posts.
        """
        clean_limit = self._validate_limit(limit)

        # Validate search query length (2–80 code points after trim)
        trimmed = query.strip() if query else ""
        if len(trimmed) < 2 or len(trimmed) > 80:
            raise ValidationError(
                "Search query 'q' must be between 2 and 80 characters.",
                details=[{"field": "q", "reason": "length_out_of_range"}],
            )

        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(f"Invalid cursor: {e}", details=[{"field": "cursor", "reason": "invalid_cursor"}])

        raw_results = await self._repository.search_originals(
            query=trimmed,
            cursor_tuple=cursor_tuple,
            limit=clean_limit,
            viewer_id=viewer_id,
        )

        if len(raw_results) > clean_limit:
            page_records = raw_results[:clean_limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_results
            has_more = False
            next_cursor = None

        return FeedResponse(
            items=[PostItem(**item) for item in page_records],
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def create_post(
        self,
        author_id: str,
        kind: str,
        text: Optional[str] = None,
        reply_to_id: Optional[str] = None,
        repost_of_id: Optional[str] = None,
        media: Optional[List[Dict[str, Any]]] = None,
    ) -> PostDetailResponse:
        """
        Creates a new post (original, reply, or repost) and returns the post detail.
        """
        if hasattr(self._repository, "create_post"):
            raw_post = await self._repository.create_post(
                author_id=author_id,
                kind=kind,
                text=text,
                reply_to_id=reply_to_id,
                repost_of_id=repost_of_id,
                media=media,
            )
            return PostDetailResponse(item=PostItem(**raw_post))
        raise ValidationError("Repository does not support post creation", status_code=500)

    async def set_like(self, user_id: str, post_id: str) -> LikeResponse:
        """
        Sets authoritative liked state for viewer.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        if hasattr(self._repository, "set_like"):
            res = await self._repository.set_like(user_id=user_id, post_id=clean_post_id)
            return LikeResponse(**res)
        raise ValidationError("Repository does not support like persistence", status_code=500)

    async def remove_like(self, user_id: str, post_id: str) -> LikeResponse:
        """
        Removes like from post for viewer.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        if hasattr(self._repository, "remove_like"):
            res = await self._repository.remove_like(user_id=user_id, post_id=clean_post_id)
            return LikeResponse(**res)
        raise ValidationError("Repository does not support like removal", status_code=500)

    async def create_repost(self, user_id: str, post_id: str) -> RepostResponse:
        """
        Creates a repost of an original post for viewer.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        if hasattr(self._repository, "create_repost"):
            res = await self._repository.create_repost(user_id=user_id, post_id=clean_post_id)
            return RepostResponse(**res)
        # Fallback to create_post
        raw_post = await self.create_post(author_id=user_id, kind="repost", repost_of_id=clean_post_id)
        return RepostResponse(post_id=clean_post_id, reposted_by_viewer=True, repost_count=1)

    async def remove_repost(self, user_id: str, post_id: str) -> RepostResponse:
        """
        Removes a repost of an original post for viewer.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        if hasattr(self._repository, "remove_repost"):
            res = await self._repository.remove_repost(user_id=user_id, post_id=clean_post_id)
            return RepostResponse(**res)
        raise ValidationError("Repository does not support repost removal", status_code=500)
