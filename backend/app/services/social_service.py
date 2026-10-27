"""
Social Service (Stage A & C).

Orchestrates post detail, user profiles, direct replies, profile media,
text search across original posts, and post/like write operations.
"""

import uuid
from typing import Any, Dict, List, Optional
from app.common.cursor import decode_cursor, encode_cursor, InvalidCursorError
from app.common.errors import ForbiddenError, NotFoundError, ValidationError
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.common import PaginatedResponse
from app.schemas.media import MediaItem
from app.schemas.post import PostItem, PostDetailResponse, FeedResponse, LikeResponse, RepostResponse
from app.schemas.user import ProfileUpdateRequest, UserProfile, UserProfileResponse, RelationshipUserItem


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

    async def update_profile(
        self,
        actor_id: str,
        target_user_id: str,
        req: ProfileUpdateRequest,
    ) -> UserProfileResponse:
        """
        Updates allowed profile fields (display_name, bio, avatars, is_private).
        Enforces strict authorization: only the account owner may update.
        """
        clean_actor_id = self._validate_uuid(actor_id, "actor_id")
        clean_target_id = self._validate_uuid(target_user_id, "id")

        if clean_actor_id != clean_target_id:
            raise ForbiddenError(
                "You are not authorized to update another member's profile",
                details=[{"field": "id", "reason": "forbidden_cross_user_mutation"}],
            )

        fields: Dict[str, Any] = {}
        if req.display_name is not None:
            fields["display_name"] = req.display_name
        if req.handle is not None:
            fields["handle"] = req.handle
        if req.bio is not None:
            fields["bio"] = req.bio
        if req.avatar_url is not None:
            clean_url = req.avatar_url.strip() if req.avatar_url else None
            fields["avatar_small_url"] = clean_url
            fields["avatar_large_url"] = clean_url
        else:
            if req.avatar_small_url is not None:
                fields["avatar_small_url"] = req.avatar_small_url.strip() if req.avatar_small_url else None
            if req.avatar_large_url is not None:
                fields["avatar_large_url"] = req.avatar_large_url.strip() if req.avatar_large_url else None
        if req.is_private is not None:
            fields["is_private"] = req.is_private

        raw_user = await self._repository.update_user_profile(clean_target_id, fields)
        if not raw_user:
            raise NotFoundError(f"User with id '{clean_target_id}' not found.")

        return UserProfileResponse(item=UserProfile(**raw_user))

    async def deactivate_account(
        self,
        actor_id: str,
        target_user_id: str,
    ) -> None:
        """
        Deactivates account and revokes all active sessions.
        Enforces strict authorization: only the account owner may deactivate.
        """
        clean_actor_id = self._validate_uuid(actor_id, "actor_id")
        clean_target_id = self._validate_uuid(target_user_id, "id")

        if clean_actor_id != clean_target_id:
            raise ForbiddenError(
                "You are not authorized to deactivate another member's account",
                details=[{"field": "id", "reason": "forbidden_cross_user_mutation"}],
            )

        success = await self._repository.deactivate_user(clean_target_id)
        if not success:
            raise NotFoundError(f"User with id '{clean_target_id}' not found.")

    async def follow_user(self, follower_id: str, target_user_id: str) -> Dict[str, Any]:
        """
        Follows target user for the current viewer actor.
        """
        clean_target_id = self._validate_uuid(target_user_id, "id")
        clean_follower_id = self._validate_uuid(follower_id, "actor_id")
        if clean_follower_id == clean_target_id:
            raise ValidationError("Self-follow is prohibited.", details=[{"reason": "self_follow_prohibited"}], status_code=400)

        rel_status, is_following, follower_count = await self._repository.follow_user(clean_follower_id, clean_target_id)
        return {
            "user_id": clean_target_id,
            "followed_by_viewer": is_following,
            "follower_count": follower_count,
            "relationship_status": rel_status,
        }

    async def unfollow_user(self, follower_id: str, target_user_id: str) -> Dict[str, Any]:
        """
        Unfollows target user or cancels pending follow request.
        """
        clean_target_id = self._validate_uuid(target_user_id, "id")
        clean_follower_id = self._validate_uuid(follower_id, "actor_id")
        rel_status, is_following, follower_count = await self._repository.unfollow_user(clean_follower_id, clean_target_id)
        return {
            "user_id": clean_target_id,
            "followed_by_viewer": is_following,
            "follower_count": follower_count,
            "relationship_status": rel_status,
        }

    async def accept_follow_request(self, actor_id: str, requester_id: str) -> Dict[str, Any]:
        """
        Target user accepts a pending follow request from requester.
        """
        clean_actor_id = self._validate_uuid(actor_id, "actor_id")
        clean_requester_id = self._validate_uuid(requester_id, "requester_id")

        is_accepted, follower_count = await self._repository.accept_follow_request(
            target_id=clean_actor_id,
            requester_id=clean_requester_id,
        )
        if not is_accepted:
            raise NotFoundError(
                "Pending follow request not found.",
                details=[{"field": "requesterId", "reason": "not_found"}],
            )

        return {
            "requester_id": clean_requester_id,
            "accepted": True,
            "follower_count": follower_count,
        }

    async def reject_follow_request(self, actor_id: str, requester_id: str) -> None:
        """
        Target user rejects a pending follow request from requester.
        """
        clean_actor_id = self._validate_uuid(actor_id, "actor_id")
        clean_requester_id = self._validate_uuid(requester_id, "requester_id")

        is_rejected = await self._repository.reject_follow_request(
            target_id=clean_actor_id,
            requester_id=clean_requester_id,
        )
        if not is_rejected:
            raise NotFoundError(
                "Pending follow request not found.",
                details=[{"field": "requesterId", "reason": "not_found"}],
            )

    async def _check_profile_visibility(self, target_user_id: str, viewer_id: Optional[str]) -> None:
        """
        Verifies if viewer is authorized to view a potentially private profile's protected data
        (followers, following, media).
        """
        profile = await self._repository.get_user_profile(target_user_id, viewer_id=viewer_id)
        if not profile:
            raise NotFoundError(f"User with id '{target_user_id}' not found.")

        if profile.get("isPrivate"):
            # If viewer is the user themselves, allow
            if viewer_id and str(viewer_id) == str(target_user_id):
                return
            # If viewer is an accepted follower, allow
            if profile.get("followedByViewer"):
                return
            # Otherwise forbidden
            raise ForbiddenError(
                "This account is private. Follow this user to see their content.",
                details=[{"field": "id", "reason": "private_account"}],
            )

    async def list_followers(
        self,
        user_id: str,
        viewer_id: Optional[str],
        cursor_str: Optional[str],
        limit: int,
    ) -> PaginatedResponse[RelationshipUserItem]:
        """
        Returns bounded, cursor-paginated active followers of user_id.
        Enforces privacy visibility.
        """
        clean_user_id = self._validate_uuid(user_id, "id")
        clean_limit = self._validate_limit(limit)
        await self._check_profile_visibility(clean_user_id, viewer_id)

        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(f"Invalid cursor: {e}", details=[{"field": "cursor", "reason": "invalid_cursor"}])

        raw_followers = await self._repository.list_followers(
            user_id=clean_user_id,
            viewer_id=viewer_id,
            cursor_tuple=cursor_tuple,
            limit=clean_limit,
        )

        if len(raw_followers) > clean_limit:
            page_records = raw_followers[:clean_limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_followers
            has_more = False
            next_cursor = None

        return PaginatedResponse[RelationshipUserItem](
            items=[RelationshipUserItem(**r) for r in page_records],
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def list_following(
        self,
        user_id: str,
        viewer_id: Optional[str],
        cursor_str: Optional[str],
        limit: int,
    ) -> PaginatedResponse[RelationshipUserItem]:
        """
        Returns bounded, cursor-paginated active followees of user_id.
        Enforces privacy visibility.
        """
        clean_user_id = self._validate_uuid(user_id, "id")
        clean_limit = self._validate_limit(limit)
        await self._check_profile_visibility(clean_user_id, viewer_id)

        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(f"Invalid cursor: {e}", details=[{"field": "cursor", "reason": "invalid_cursor"}])

        raw_following = await self._repository.list_following(
            user_id=clean_user_id,
            viewer_id=viewer_id,
            cursor_tuple=cursor_tuple,
            limit=clean_limit,
        )

        if len(raw_following) > clean_limit:
            page_records = raw_following[:clean_limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_following
            has_more = False
            next_cursor = None

        return PaginatedResponse[RelationshipUserItem](
            items=[RelationshipUserItem(**r) for r in page_records],
            next_cursor=next_cursor,
            has_more=has_more,
        )

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

        # Confirm post exists and is an original (allow replies on tombstoned/deleted parents)
        kind = await self._repository.get_post_kind(clean_post_id, include_deleted=True)
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
        viewer_id: Optional[str] = None,
    ) -> PaginatedResponse[MediaItem]:
        """
        Retrieves paginated media rows from a user's original posts.
        Enforces privacy visibility.
        """
        clean_user_id = self._validate_uuid(user_id, "id")
        clean_limit = self._validate_limit(limit)

        exists = await self._repository.user_exists(clean_user_id)
        if not exists:
            raise NotFoundError(f"User with id '{clean_user_id}' not found.")

        await self._check_profile_visibility(clean_user_id, viewer_id)

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

    async def update_post(
        self,
        post_id: str,
        author_id: str,
        text: str,
        expected_version: Optional[int] = None,
    ) -> PostDetailResponse:
        """
        Edits an eligible post's text.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        clean_author_id = self._validate_uuid(author_id, "author_id")

        if not hasattr(self._repository, "update_post"):
            raise ValidationError("Repository does not support post updates", status_code=500)

        raw_post = await self._repository.update_post(
            post_id=clean_post_id,
            author_id=clean_author_id,
            text=text,
            expected_version=expected_version,
        )
        return PostDetailResponse(item=PostItem(**raw_post))

    async def delete_post(
        self,
        post_id: str,
        author_id: str,
    ) -> None:
        """
        Soft-deletes an eligible post owned by author_id.
        """
        clean_post_id = self._validate_uuid(post_id, "id")
        clean_author_id = self._validate_uuid(author_id, "author_id")

        if not hasattr(self._repository, "delete_post"):
            raise ValidationError("Repository does not support post deletion", status_code=500)

        await self._repository.delete_post(
            post_id=clean_post_id,
            author_id=clean_author_id,
        )

    async def list_notifications(
        self,
        recipient_id: str,
        cursor_str: Optional[str] = None,
        limit: int = 10,
    ) -> Any:
        """
        Retrieves cursor-paginated notification inbox for authenticated recipient.
        """
        clean_recipient_id = self._validate_uuid(recipient_id, "recipient_id")
        clean_limit = self._validate_limit(limit)

        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(f"Invalid cursor: {e}", details=[{"field": "cursor", "reason": "invalid_cursor"}])

        raw_notifications = await self._repository.list_notifications(
            recipient_id=clean_recipient_id,
            cursor_tuple=cursor_tuple,
            limit=clean_limit,
        )
        unread_count = await self._repository.get_unread_notification_count(clean_recipient_id)

        if len(raw_notifications) > clean_limit:
            page_records = raw_notifications[:clean_limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_notifications
            has_more = False
            next_cursor = None

        from app.schemas.notification import NotificationItem, NotificationListResponse
        return NotificationListResponse(
            items=[NotificationItem(**n) for n in page_records],
            unread_count=unread_count,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def mark_notifications_read(
        self,
        recipient_id: str,
        notification_id: Optional[str] = None,
    ) -> Any:
        """
        Marks single or all unread notifications as read.
        """
        clean_recipient_id = self._validate_uuid(recipient_id, "recipient_id")
        clean_notif_id = self._validate_uuid(notification_id, "notification_id") if notification_id else None

        marked, unread = await self._repository.mark_notifications_read(
            recipient_id=clean_recipient_id,
            notification_id=clean_notif_id,
        )
        from app.schemas.notification import MarkReadResponse
        return MarkReadResponse(marked_count=marked, unread_count=unread)


