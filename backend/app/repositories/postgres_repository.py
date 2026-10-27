"""
PostgreSQL Repository Implementation (Stage C).

Implements SocialRepositoryProtocol and Stage C persistence requirements using
SQLAlchemy 2.x async ORM and Core against PostgreSQL (instagram_modeling).
Reference: docs/05_Python_Database_Integration_PRD.md
"""

import inspect
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import (
    and_,
    delete,
    exists,
    func,
    or_,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.common.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models import Follow, Notification, Post, PostLike, PostMedia, Session, User


class PostgresRepository:
    """
    Asynchronous PostgreSQL repository satisfying SocialRepositoryProtocol and Stage C persistence.
    Operates on a request-scoped AsyncSession without leaking ORM models across the boundary.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    # -----------------------------------------------------------------------
    # Helper Serialization & Mapping
    # -----------------------------------------------------------------------
    @staticmethod
    def _format_author_dict(user: User, followed_by_viewer: bool = False) -> Dict[str, Any]:
        avatar = None
        if user.avatar_small_url or user.avatar_large_url:
            avatar = {
                "smallUrl": user.avatar_small_url,
                "largeUrl": user.avatar_large_url,
            }
        return {
            "id": str(user.id),
            "handle": user.handle,
            "displayName": user.display_name,
            "avatar": avatar,
            "followedByViewer": followed_by_viewer,
        }

    @staticmethod
    def _format_media_dict(media: PostMedia) -> Dict[str, Any]:
        return {
            "id": str(media.id),
            "postId": str(media.post_id),
            "altText": media.alt_text,
            "width": media.width,
            "height": media.height,
            "position": media.position,
            "smallUrl": media.small_url,
            "largeUrl": media.large_url,
            "createdAt": media.created_at.isoformat().replace("+00:00", "Z"),
        }

    def _assemble_post_dict(
        self,
        post: Post,
        like_count: int,
        reply_count: int,
        liked_by_viewer: bool,
        followed_by_viewer: bool = False,
        repost_count: int = 0,
        reposted_by_viewer: bool = False,
        referenced_author_handle: Optional[str] = None,
        referenced_text: Optional[str] = None,
        liker_handles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        media_list = []
        if post.kind == "original" and post.media:
            sorted_media = sorted(post.media, key=lambda m: m.position)
            media_list = [
                {
                    "id": str(m.id),
                    "altText": m.alt_text,
                    "width": m.width,
                    "height": m.height,
                    "position": m.position,
                    "smallUrl": m.small_url,
                    "largeUrl": m.large_url,
                }
                for m in sorted_media
            ]

        data: Dict[str, Any] = {
            "id": str(post.id),
            "kind": post.kind,
            "text": post.text,
            "createdAt": post.created_at.isoformat().replace("+00:00", "Z") if hasattr(post.created_at, "isoformat") else str(post.created_at),
            "author": self._format_author_dict(post.author, followed_by_viewer=followed_by_viewer),
            "media": media_list,
            "likeCount": like_count,
            "replyCount": reply_count,
            "repostCount": repost_count,
            "likedByViewer": liked_by_viewer,
            "repostedByViewer": reposted_by_viewer,
            "replyToId": str(post.reply_to_id) if post.reply_to_id else None,
            "repostOfId": str(post.repost_of_id) if post.repost_of_id else None,
            "updatedAt": post.updated_at.isoformat().replace("+00:00", "Z") if getattr(post, "updated_at", None) else None,
            "version": getattr(post, "version", 1),
            "likerHandles": liker_handles or [],
        }

        if post.kind == "repost" and referenced_author_handle is not None:
            data["referencedPost"] = {
                "id": str(post.repost_of_id),
                "text": referenced_text,
                "author": {"handle": referenced_author_handle},
            }

        return data

    @staticmethod
    def _apply_cursor_predicate(
        query,
        cursor_tuple: Optional[Tuple[datetime, str]],
    ):
        """Applies the strict keyset cursor predicate (created_at DESC, id DESC)."""
        if cursor_tuple is None:
            return query
        cursor_time, cursor_id_str = cursor_tuple
        cursor_uuid = uuid.UUID(cursor_id_str)
        return query.where(
            or_(
                Post.created_at < cursor_time,
                and_(
                    Post.created_at == cursor_time,
                    Post.id < cursor_uuid,
                ),
            )
        )

    # -----------------------------------------------------------------------
    # Protocol Read Methods
    # -----------------------------------------------------------------------
    async def list_original_feed(
        self,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
        scope: str = "home",
    ) -> List[Dict[str, Any]]:
        viewer_uuid = uuid.UUID(viewer_id)

        # Correlated scalar subqueries for count safety (no row multiplying)
        reply_post = aliased(Post)
        like_count_sq = (
            select(func.count(PostLike.user_id))
            .where(PostLike.post_id == Post.id)
            .correlate(Post)
            .scalar_subquery()
        )
        reply_count_sq = (
            select(func.count(reply_post.id))
            .where(reply_post.reply_to_id == Post.id)
            .correlate(Post)
            .scalar_subquery()
        )
        liked_by_viewer_sq = (
            select(
                exists(
                    select(1)
                    .where(
                        and_(
                            PostLike.post_id == Post.id,
                            PostLike.user_id == viewer_uuid,
                        )
                    )
                    .correlate(Post)
                )
            ).scalar_subquery()
        )
        followed_by_viewer_sq = (
            select(
                exists(
                    select(1)
                    .where(
                        and_(
                            Follow.follower_id == viewer_uuid,
                            Follow.following_id == Post.author_id,
                            Follow.status == "accepted",
                        )
                    )
                    .correlate(Post)
                )
            ).scalar_subquery()
        )

        repost_post = aliased(Post)
        repost_count_sq = (
            select(func.count(repost_post.id))
            .where(and_(repost_post.kind == "repost", repost_post.repost_of_id == Post.id))
            .correlate(Post)
            .scalar_subquery()
        )
        reposted_by_viewer_sq = (
            select(
                exists(
                    select(1)
                    .where(
                        and_(
                            repost_post.kind == "repost",
                            repost_post.author_id == viewer_uuid,
                            repost_post.repost_of_id == Post.id,
                        )
                    )
                    .correlate(Post)
                )
            ).scalar_subquery()
        )

        stmt = (
            select(
                Post,
                like_count_sq.label("like_count"),
                reply_count_sq.label("reply_count"),
                liked_by_viewer_sq.label("liked_by_viewer"),
                followed_by_viewer_sq.label("followed_by_viewer"),
                repost_count_sq.label("repost_count"),
                reposted_by_viewer_sq.label("reposted_by_viewer"),
            )
            .join(Post.author)
            .options(
                selectinload(Post.author),
                selectinload(Post.media),
            )
            .where(
                and_(
                    Post.kind == "original",
                    Post.deleted_at.is_(None),
                    User.is_active.is_(True),
                )
            )
        )

        if scope == "home":
            # Personalized feed: only viewer's own posts and accepted followed authors
            eligible_authors = or_(
                Post.author_id == viewer_uuid,
                Post.author_id.in_(
                    select(Follow.following_id).where(
                        and_(
                            Follow.follower_id == viewer_uuid,
                            Follow.status == "accepted",
                        )
                    )
                ),
            )
            stmt = stmt.where(eligible_authors)

        stmt = (
            stmt.order_by(Post.created_at.desc(), Post.id.desc())
            .limit(limit + 1)
        )

        stmt = self._apply_cursor_predicate(stmt, cursor_tuple)
        result = await self._session.execute(stmt)
        rows = result.all()

        post_ids = [row[0].id for row in rows]
        liker_map = defaultdict(list)
        if post_ids:
            likers_stmt = (
                select(PostLike.post_id, User.handle)
                .join(User, PostLike.user_id == User.id)
                .where(PostLike.post_id.in_(post_ids))
                .order_by(PostLike.created_at.desc())
            )
            likers_res = await self._session.execute(likers_stmt)
            for pid, handle in likers_res.all():
                if len(liker_map[pid]) < 3:
                    liker_map[pid].append(handle)

        return [
            self._assemble_post_dict(
                post=row[0],
                like_count=row[1] or 0,
                reply_count=row[2] or 0,
                liked_by_viewer=bool(row[3]),
                followed_by_viewer=bool(row[4]),
                repost_count=row[5] or 0,
                reposted_by_viewer=bool(row[6]),
                liker_handles=liker_map.get(row[0].id, []),
            )
            for row in rows
        ]

    async def get_post_detail(
        self,
        post_id: str,
        viewer_id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            post_uuid = uuid.UUID(post_id)
            viewer_uuid = uuid.UUID(viewer_id)
        except ValueError:
            return None

        reply_post = aliased(Post)
        like_count_sq = (
            select(func.count(PostLike.user_id))
            .where(PostLike.post_id == post_uuid)
            .scalar_subquery()
        )
        reply_count_sq = (
            select(func.count(reply_post.id))
            .where(reply_post.reply_to_id == post_uuid)
            .scalar_subquery()
        )
        liked_by_viewer_sq = (
            select(
                exists(
                    select(1).where(
                        and_(
                            PostLike.post_id == post_uuid,
                            PostLike.user_id == viewer_uuid,
                        )
                    )
                )
            ).scalar_subquery()
        )
        followed_by_viewer_sq = (
            select(
                exists(
                    select(1)
                    .where(
                        and_(
                            Follow.follower_id == viewer_uuid,
                            Follow.following_id == Post.author_id,
                        )
                    )
                    .correlate(Post)
                )
            ).scalar_subquery()
        )
        repost_post = aliased(Post)
        repost_count_sq = (
            select(func.count(repost_post.id))
            .where(and_(repost_post.kind == "repost", repost_post.repost_of_id == post_uuid))
            .scalar_subquery()
        )
        reposted_by_viewer_sq = (
            select(
                exists(
                    select(1).where(
                        and_(
                            repost_post.kind == "repost",
                            repost_post.author_id == viewer_uuid,
                            repost_post.repost_of_id == post_uuid,
                        )
                    )
                )
            ).scalar_subquery()
        )

        stmt = (
            select(
                Post,
                like_count_sq.label("like_count"),
                reply_count_sq.label("reply_count"),
                liked_by_viewer_sq.label("liked_by_viewer"),
                followed_by_viewer_sq.label("followed_by_viewer"),
                repost_count_sq.label("repost_count"),
                reposted_by_viewer_sq.label("reposted_by_viewer"),
            )
            .options(
                selectinload(Post.author),
                selectinload(Post.media),
            )
            .where(and_(Post.id == post_uuid, Post.deleted_at.is_(None)))
        )

        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None

        post, like_cnt, reply_cnt, liked, followed, repost_cnt, reposted = (
            row[0], row[1] or 0, row[2] or 0, bool(row[3]), bool(row[4]), row[5] or 0, bool(row[6])
        )
        ref_handle, ref_text = None, None

        if post.kind == "repost" and post.repost_of_id:
            ref_stmt = (
                select(Post, User.handle)
                .join(User, User.id == Post.author_id)
                .where(Post.id == post.repost_of_id)
            )
            ref_res = await self._session.execute(ref_stmt)
            ref_row = ref_res.first()
            if ref_row:
                ref_text = ref_row[0].text
                ref_handle = ref_row[1]

        # Fetch top liker handles for this post
        likers_stmt = (
            select(User.handle)
            .join(PostLike, PostLike.user_id == User.id)
            .where(PostLike.post_id == post_uuid)
            .order_by(PostLike.created_at.desc())
            .limit(3)
        )
        likers_res = await self._session.execute(likers_stmt)
        liker_handles = [row[0] for row in likers_res.all()]

        return self._assemble_post_dict(
            post=post,
            like_count=like_cnt,
            reply_count=reply_cnt,
            liked_by_viewer=liked,
            followed_by_viewer=followed,
            repost_count=repost_cnt,
            reposted_by_viewer=reposted,
            referenced_author_handle=ref_handle,
            referenced_text=ref_text,
            liker_handles=liker_handles,
        )

    async def get_user_profile(
        self,
        user_id: str,
        viewer_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None

        viewer_uuid = None
        if viewer_id:
            try:
                viewer_uuid = uuid.UUID(viewer_id)
            except ValueError:
                pass

        # Scalar subqueries for profile counts
        post_count_sq = (
            select(func.count(Post.id))
            .where(
                and_(
                    Post.author_id == user_uuid,
                    Post.kind == "original",
                    Post.deleted_at.is_(None),
                )
            )
            .scalar_subquery()
        )
        follower_count_sq = (
            select(func.count(Follow.follower_id))
            .where(and_(Follow.following_id == user_uuid, Follow.status == "accepted"))
            .scalar_subquery()
        )
        following_count_sq = (
            select(func.count(Follow.following_id))
            .where(and_(Follow.follower_id == user_uuid, Follow.status == "accepted"))
            .scalar_subquery()
        )
        followed_by_viewer_sq = (
            select(
                exists(
                    select(1).where(
                        and_(
                            Follow.follower_id == viewer_uuid,
                            Follow.following_id == user_uuid,
                            Follow.status == "accepted",
                        )
                    )
                )
            ).scalar_subquery() if viewer_uuid else select(False).scalar_subquery()
        )
        relationship_status_sq = (
            select(Follow.status)
            .where(
                and_(
                    Follow.follower_id == viewer_uuid,
                    Follow.following_id == user_uuid,
                )
            )
            .limit(1)
            .scalar_subquery() if viewer_uuid else select(None).scalar_subquery()
        )

        stmt = select(
            User,
            post_count_sq.label("post_count"),
            follower_count_sq.label("follower_count"),
            following_count_sq.label("following_count"),
            followed_by_viewer_sq.label("followed_by_viewer"),
            relationship_status_sq.label("relationship_status"),
        ).where(and_(User.id == user_uuid, User.is_active.is_(True)))

        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None

        user, post_cnt, follower_cnt, following_cnt, followed_by_viewer, rel_status = (
            row[0], row[1] or 0, row[2] or 0, row[3] or 0, bool(row[4]), row[5] or "none"
        )
        avatar = None
        if user.avatar_small_url or user.avatar_large_url:
            avatar = {
                "smallUrl": user.avatar_small_url,
                "largeUrl": user.avatar_large_url,
            }

        return {
            "id": str(user.id),
            "handle": user.handle,
            "displayName": user.display_name,
            "bio": user.bio,
            "avatar": avatar,
            "postCount": post_cnt,
            "followerCount": follower_cnt,
            "followingCount": following_cnt,
            "followedByViewer": followed_by_viewer,
            "isPrivate": user.is_private,
            "relationshipStatus": rel_status,
        }

    async def list_direct_replies(
        self,
        post_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        parent_uuid = uuid.UUID(post_id)
        viewer_uuid = uuid.UUID(viewer_id)

        like_count_sq = (
            select(func.count(PostLike.user_id))
            .where(PostLike.post_id == Post.id)
            .correlate(Post)
            .scalar_subquery()
        )
        liked_by_viewer_sq = (
            select(
                exists(
                    select(1)
                    .where(
                        and_(
                            PostLike.post_id == Post.id,
                            PostLike.user_id == viewer_uuid,
                        )
                    )
                    .correlate(Post)
                )
            ).scalar_subquery()
        )

        stmt = (
            select(
                Post,
                like_count_sq.label("like_count"),
                liked_by_viewer_sq.label("liked_by_viewer"),
            )
            .options(selectinload(Post.author))
            .where(
                and_(
                    Post.kind == "reply",
                    Post.reply_to_id == parent_uuid,
                    Post.deleted_at.is_(None),
                )
            )
            .order_by(Post.created_at.desc(), Post.id.desc())
            .limit(limit + 1)
        )

        stmt = self._apply_cursor_predicate(stmt, cursor_tuple)
        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            self._assemble_post_dict(
                post=row[0],
                like_count=row[1] or 0,
                reply_count=0,
                liked_by_viewer=bool(row[2]),
            )
            for row in rows
        ]

    async def list_profile_media(
        self,
        user_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        user_uuid = uuid.UUID(user_id)

        stmt = (
            select(PostMedia)
            .join(Post, Post.id == PostMedia.post_id)
            .where(
                and_(
                    Post.author_id == user_uuid,
                    Post.kind == "original",
                    Post.deleted_at.is_(None),
                )
            )
            .order_by(PostMedia.created_at.desc(), PostMedia.id.desc())
            .limit(limit + 1)
        )

        if cursor_tuple is not None:
            cursor_time, cursor_id_str = cursor_tuple
            cursor_uuid = uuid.UUID(cursor_id_str)
            stmt = stmt.where(
                or_(
                    PostMedia.created_at < cursor_time,
                    and_(
                        PostMedia.created_at == cursor_time,
                        PostMedia.id < cursor_uuid,
                    ),
                )
            )

        result = await self._session.execute(stmt)
        media_rows = result.scalars().all()
        return [self._format_media_dict(m) for m in media_rows]

    async def search_originals(
        self,
        query: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        viewer_uuid = uuid.UUID(viewer_id)
        clean_query = query.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

        reply_post = aliased(Post)
        like_count_sq = (
            select(func.count(PostLike.user_id))
            .where(PostLike.post_id == Post.id)
            .correlate(Post)
            .scalar_subquery()
        )
        reply_count_sq = (
            select(func.count(reply_post.id))
            .where(reply_post.reply_to_id == Post.id)
            .correlate(Post)
            .scalar_subquery()
        )
        liked_by_viewer_sq = (
            select(
                exists(
                    select(1)
                    .where(
                        and_(
                            PostLike.post_id == Post.id,
                            PostLike.user_id == viewer_uuid,
                        )
                    )
                    .correlate(Post)
                )
            ).scalar_subquery()
        )

        stmt = (
            select(
                Post,
                like_count_sq.label("like_count"),
                reply_count_sq.label("reply_count"),
                liked_by_viewer_sq.label("liked_by_viewer"),
            )
            .options(
                selectinload(Post.author),
                selectinload(Post.media),
            )
            .where(
                and_(
                    Post.kind == "original",
                    Post.deleted_at.is_(None),
                    Post.text.ilike(f"%{clean_query}%"),
                )
            )
            .order_by(Post.created_at.desc(), Post.id.desc())
            .limit(limit + 1)
        )

        stmt = self._apply_cursor_predicate(stmt, cursor_tuple)
        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            self._assemble_post_dict(
                post=row[0],
                like_count=row[1] or 0,
                reply_count=row[2] or 0,
                liked_by_viewer=bool(row[3]),
            )
            for row in rows
        ]

    async def user_exists(self, user_id: str) -> bool:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return False
        stmt = select(exists(select(1).where(User.id == user_uuid)))
        result = await self._session.execute(stmt)
        return bool(result.scalar())

    async def get_post_kind(self, post_id: str, include_deleted: bool = False) -> Optional[str]:
        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            return None
        stmt = select(Post.kind).where(Post.id == post_uuid)
        if not include_deleted:
            stmt = stmt.where(Post.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # -----------------------------------------------------------------------
    # Stage C Persistence Writes
    # -----------------------------------------------------------------------
    async def create_post(
        self,
        author_id: str,
        kind: str,
        text: Optional[str] = None,
        reply_to_id: Optional[str] = None,
        repost_of_id: Optional[str] = None,
        media: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Persists a new post (original, reply, or repost) atomically with domain validation.
        """
        author_uuid = uuid.UUID(author_id)
        if not await self.user_exists(author_id):
            raise NotFoundError("Author user not found", [{"field": "authorId", "reason": "not_found"}])

        post_uuid = uuid.uuid4()
        now = datetime.now()

        if kind == "original":
            if not text or not (1 <= len(text.strip()) <= 280):
                raise ValidationError("Original post requires 1 to 280 characters of text", [{"field": "text", "reason": "length"}], status_code=422)
            if media and len(media) > 4:
                raise ValidationError("Original post can contain at most 4 media attachments", [{"field": "media", "reason": "max_length"}], status_code=422)

            post = Post(
                id=post_uuid,
                author_id=author_uuid,
                kind="original",
                text=text.strip(),
                reply_to_id=None,
                repost_of_id=None,
                created_at=now,
            )
            self._session.add(post)

            if media:
                for idx, m in enumerate(media):
                    media_row = PostMedia(
                        id=uuid.uuid4(),
                        post_id=post_uuid,
                        position=idx,
                        alt_text=m.get("altText", ""),
                        width=m.get("width", 1200),
                        height=m.get("height", 800),
                        small_url=m.get("smallUrl", ""),
                        large_url=m.get("largeUrl", ""),
                        created_at=now,
                    )
                    self._session.add(media_row)

            await self._session.flush()
            return await self.get_post_detail(str(post_uuid), viewer_id=author_id)  # type: ignore

        elif kind == "reply":
            if not reply_to_id:
                raise ValidationError("replyToId is required for reply", [{"field": "replyToId", "reason": "missing"}], status_code=422)
            if not text or not (1 <= len(text.strip()) <= 280):
                raise ValidationError("Reply post requires 1 to 280 characters of text", [{"field": "text", "reason": "length"}], status_code=422)
            if media:
                raise ValidationError("Replies cannot contain media attachments", [{"field": "media", "reason": "unsupported"}], status_code=422)

            parent_kind = await self.get_post_kind(reply_to_id)
            if parent_kind is None:
                raise NotFoundError("Target post not found", [{"field": "replyToId", "reason": "not_found"}])
            if parent_kind != "original":
                raise ValidationError("Replies are only permitted on original posts", [{"field": "replyToId", "reason": "invalid_kind"}], status_code=422)

            post = Post(
                id=post_uuid,
                author_id=author_uuid,
                kind="reply",
                text=text.strip(),
                reply_to_id=uuid.UUID(reply_to_id),
                repost_of_id=None,
                created_at=now,
            )
            self._session.add(post)
            await self._session.flush()

            # Trigger notification for reply
            parent_post = None
            if hasattr(self._session, "get"):
                res = self._session.get(Post, uuid.UUID(reply_to_id))
                if inspect.isawaitable(res):
                    parent_post = await res
            if parent_post:
                await self._create_notification(
                    recipient_id=parent_post.author_id,
                    actor_id=author_uuid,
                    event_type="reply",
                    target_post_id=post_uuid,
                )

            await self._session.flush()
            return await self.get_post_detail(str(post_uuid), viewer_id=author_id)  # type: ignore

        elif kind == "repost":
            if not repost_of_id:
                raise ValidationError("repostOfId is required for repost", [{"field": "repostOfId", "reason": "missing"}], status_code=422)
            if text is not None:
                raise ValidationError("Reposts cannot contain new text", [{"field": "text", "reason": "unsupported"}], status_code=422)
            if media:
                raise ValidationError("Reposts cannot contain media attachments", [{"field": "media", "reason": "unsupported"}], status_code=422)

            target_kind = await self.get_post_kind(repost_of_id)
            if target_kind is None:
                raise NotFoundError("Target post not found", [{"field": "repostOfId", "reason": "not_found"}])
            if target_kind != "original":
                raise ValidationError("Reposts are only permitted on original posts", [{"field": "repostOfId", "reason": "invalid_kind"}], status_code=422)

            target_uuid = uuid.UUID(repost_of_id)
            # Check duplicate repost invariant
            existing_repost = await self.get_repost_lookup(author_id, repost_of_id)
            if existing_repost is not None:
                raise ConflictError("User has already reposted this original post", [{"field": "repostOfId", "reason": "duplicate_repost"}])

            post = Post(
                id=post_uuid,
                author_id=author_uuid,
                kind="repost",
                text=None,
                reply_to_id=None,
                repost_of_id=target_uuid,
                created_at=now,
            )
            self._session.add(post)

            # Trigger notification for repost
            target_post = None
            if hasattr(self._session, "get"):
                res = self._session.get(Post, target_uuid)
                if inspect.isawaitable(res):
                    target_post = await res
            if target_post:
                await self._create_notification(
                    recipient_id=target_post.author_id,
                    actor_id=author_uuid,
                    event_type="repost",
                    target_post_id=target_uuid,
                )

            try:
                await self._session.flush()
            except IntegrityError as exc:
                raise ConflictError("User has already reposted this original post", [{"field": "repostOfId", "reason": "duplicate_repost"}]) from exc

            return await self.get_post_detail(str(post_uuid), viewer_id=author_id)  # type: ignore

        else:
            raise ValidationError(f"Invalid post kind '{kind}'", [{"field": "kind", "reason": "invalid_kind"}], status_code=422)

    async def set_like(self, user_id: str, post_id: str) -> Dict[str, Any]:
        """
        Sets desired liked state (idempotent write). Handles concurrency races gracefully.
        """
        user_uuid = uuid.UUID(user_id)
        post_uuid = uuid.UUID(post_id)

        post_kind = await self.get_post_kind(post_id)
        if post_kind is None:
            raise NotFoundError("Post not found", [{"field": "postId", "reason": "not_found"}])
        if post_kind == "repost":
            raise ValidationError("Liking a repost is rejected; like the referenced original instead", [{"field": "postId", "reason": "invalid_kind"}], status_code=422)

        # Upsert or savepoint insert to handle concurrent likes
        async with self._session.begin_nested():
            stmt = pg_insert(PostLike).values(
                user_id=user_uuid,
                post_id=post_uuid,
                created_at=datetime.now(),
            ).on_conflict_do_nothing(index_elements=["user_id", "post_id"])
            await self._session.execute(stmt)

        # Trigger notification for like
        target_post = None
        if hasattr(self._session, "get"):
            res = self._session.get(Post, post_uuid)
            if inspect.isawaitable(res):
                target_post = await res
        if target_post:
            await self._create_notification(
                recipient_id=target_post.author_id,
                actor_id=user_uuid,
                event_type="like",
                target_post_id=post_uuid,
            )

        await self._session.flush()
        like_count = await self.get_like_count(post_id)
        return {
            "postId": post_id,
            "likedByViewer": True,
            "likeCount": like_count,
        }

    async def remove_like(self, user_id: str, post_id: str) -> Dict[str, Any]:
        """
        Removes like from post (desired unliked state). Idempotent.
        """
        user_uuid = uuid.UUID(user_id)
        post_uuid = uuid.UUID(post_id)

        post_kind = await self.get_post_kind(post_id)
        if post_kind is None:
            raise NotFoundError("Post not found", [{"field": "postId", "reason": "not_found"}])
        if post_kind == "repost":
            raise ValidationError("Liking a repost is rejected", [{"field": "postId", "reason": "invalid_kind"}], status_code=422)

        stmt = delete(PostLike).where(
            and_(PostLike.user_id == user_uuid, PostLike.post_id == post_uuid)
        )
        await self._session.execute(stmt)
        await self._session.flush()

        like_count = await self.get_like_count(post_id)
        return {
            "postId": post_id,
            "likedByViewer": False,
            "likeCount": like_count,
        }

    async def get_like_count(self, post_id: str) -> int:
        post_uuid = uuid.UUID(post_id)
        stmt = select(func.count(PostLike.user_id)).where(PostLike.post_id == post_uuid)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_repost_lookup(self, author_id: str, original_post_id: str) -> Optional[Dict[str, Any]]:
        author_uuid = uuid.UUID(author_id)
        original_uuid = uuid.UUID(original_post_id)
    
        stmt = (
            select(Post)
            .where(
                and_(
                    Post.kind == "repost",
                    Post.author_id == author_uuid,
                    Post.repost_of_id == original_uuid,
                )
            )
        )
        result = await self._session.execute(stmt)
        post = result.scalar_one_or_none()
        if not post:
            return None
        return {
            "repostId": str(post.id),
            "authorId": str(post.author_id),
            "repostOfId": str(post.repost_of_id),
            "createdAt": post.created_at.isoformat().replace("+00:00", "Z") if hasattr(post.created_at, "isoformat") else str(post.created_at),
        }

    async def is_following(self, follower_id: str, following_id: str) -> bool:
        try:
            follower_uuid = uuid.UUID(follower_id)
            following_uuid = uuid.UUID(following_id)
        except ValueError:
            return False

        stmt = select(
            exists(
                select(1).where(
                    and_(
                        Follow.follower_id == follower_uuid,
                        Follow.following_id == following_uuid,
                        Follow.status == "accepted",
                    )
                )
            )
        )
        result = await self._session.execute(stmt)
        return bool(result.scalar())

    async def follow_user(self, follower_id: str, following_id: str) -> Tuple[str, bool, int]:
        try:
            follower_uuid = uuid.UUID(follower_id)
            following_uuid = uuid.UUID(following_id)
        except ValueError as e:
            raise ValidationError("Invalid UUID format.", details=[{"reason": "invalid_uuid"}]) from e

        if follower_uuid == following_uuid:
            raise ValidationError("Self-follow is prohibited.", details=[{"reason": "self_follow_prohibited"}], status_code=400)

        target_user = await self._session.get(User, following_uuid)
        if not target_user or not target_user.is_active:
            raise NotFoundError("Target user not found.", details=[{"field": "followingId", "reason": "not_found"}])

        desired_status = "pending" if target_user.is_private else "accepted"

        try:
            stmt = (
                pg_insert(Follow)
                .values(
                    follower_id=follower_uuid,
                    following_id=following_uuid,
                    status=desired_status,
                )
                .on_conflict_do_nothing(index_elements=["follower_id", "following_id"])
            )
            await self._session.execute(stmt)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError("Follow relation conflict.", details=[{"reason": "duplicate_follow"}]) from exc

        # Read actual row status (whether newly inserted or already existing)
        status_stmt = select(Follow.status).where(
            and_(
                Follow.follower_id == follower_uuid,
                Follow.following_id == following_uuid,
            )
        )
        res_status = await self._session.execute(status_stmt)
        actual_status = res_status.scalar() or desired_status

        if actual_status == "accepted":
            await self._create_notification(
                recipient_id=following_uuid,
                actor_id=follower_uuid,
                event_type="follow",
                target_post_id=None,
            )
            await self._session.commit()

        count_stmt = select(func.count(Follow.follower_id)).where(
            and_(
                Follow.following_id == following_uuid,
                Follow.status == "accepted",
            )
        )
        res = await self._session.execute(count_stmt)
        follower_count = res.scalar() or 0
        followed_by_viewer = (actual_status == "accepted")
        return actual_status, followed_by_viewer, follower_count

    async def unfollow_user(self, follower_id: str, following_id: str) -> Tuple[str, bool, int]:
        try:
            follower_uuid = uuid.UUID(follower_id)
            following_uuid = uuid.UUID(following_id)
        except ValueError as e:
            raise ValidationError("Invalid UUID format.", details=[{"reason": "invalid_uuid"}]) from e

        target_exists = await self.user_exists(following_id)
        if not target_exists:
            raise NotFoundError("Target user not found.", details=[{"field": "followingId", "reason": "not_found"}])

        stmt = delete(Follow).where(
            and_(
                Follow.follower_id == follower_uuid,
                Follow.following_id == following_uuid,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

        count_stmt = select(func.count(Follow.follower_id)).where(
            and_(
                Follow.following_id == following_uuid,
                Follow.status == "accepted",
            )
        )
        res = await self._session.execute(count_stmt)
        follower_count = res.scalar() or 0
        return "none", False, follower_count

    async def accept_follow_request(
        self,
        target_id: str,
        requester_id: str,
    ) -> Tuple[bool, int]:
        try:
            target_uuid = uuid.UUID(target_id)
            requester_uuid = uuid.UUID(requester_id)
        except ValueError as e:
            raise ValidationError("Invalid UUID format.", details=[{"reason": "invalid_uuid"}]) from e

        stmt = (
            update(Follow)
            .where(
                and_(
                    Follow.follower_id == requester_uuid,
                    Follow.following_id == target_uuid,
                    Follow.status == "pending",
                )
            )
            .values(status="accepted")
        )
        res = await self._session.execute(stmt)
        is_accepted = bool(res.rowcount > 0)

        if is_accepted:
            # Recipient of follow_accepted is the original requester
            await self._create_notification(
                recipient_id=requester_uuid,
                actor_id=target_uuid,
                event_type="follow_accepted",
                target_post_id=None,
            )

        await self._session.commit()

        count_stmt = select(func.count(Follow.follower_id)).where(
            and_(
                Follow.following_id == target_uuid,
                Follow.status == "accepted",
            )
        )
        count_res = await self._session.execute(count_stmt)
        follower_count = count_res.scalar() or 0
        return is_accepted, follower_count

    async def reject_follow_request(
        self,
        target_id: str,
        requester_id: str,
    ) -> bool:
        try:
            target_uuid = uuid.UUID(target_id)
            requester_uuid = uuid.UUID(requester_id)
        except ValueError as e:
            raise ValidationError("Invalid UUID format.", details=[{"reason": "invalid_uuid"}]) from e

        stmt = (
            delete(Follow)
            .where(
                and_(
                    Follow.follower_id == requester_uuid,
                    Follow.following_id == target_uuid,
                    Follow.status == "pending",
                )
            )
        )
        res = await self._session.execute(stmt)
        await self._session.commit()
        return bool(res.rowcount > 0)

    async def list_followers(
        self,
        user_id: str,
        viewer_id: Optional[str] = None,
        cursor_tuple: Optional[Tuple[datetime, str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        user_uuid = uuid.UUID(user_id)
        viewer_uuid = uuid.UUID(viewer_id) if viewer_id else None

        followed_by_viewer_sq = (
            select(
                exists(
                    select(1).where(
                        and_(
                            Follow.follower_id == viewer_uuid,
                            Follow.following_id == User.id,
                            Follow.status == "accepted",
                        )
                    )
                )
            ).scalar_subquery() if viewer_uuid else select(False).scalar_subquery()
        )

        stmt = (
            select(
                User,
                Follow.created_at.label("rel_created_at"),
                followed_by_viewer_sq.label("followed_by_viewer"),
            )
            .join(Follow, Follow.follower_id == User.id)
            .where(
                and_(
                    Follow.following_id == user_uuid,
                    Follow.status == "accepted",
                    User.is_active.is_(True),
                )
            )
            .order_by(Follow.created_at.desc(), User.id.desc())
            .limit(limit + 1)
        )

        if cursor_tuple:
            c_time, c_id = cursor_tuple
            c_uuid = uuid.UUID(c_id)
            stmt = stmt.where(
                or_(
                    Follow.created_at < c_time,
                    and_(
                        Follow.created_at == c_time,
                        User.id < c_uuid,
                    ),
                )
            )

        res = await self._session.execute(stmt)
        rows = res.all()
        items = []
        for row in rows:
            u, rel_created_at, followed = row[0], row[1], bool(row[2])
            avatar = None
            if u.avatar_small_url or u.avatar_large_url:
                avatar = {
                    "smallUrl": u.avatar_small_url,
                    "largeUrl": u.avatar_large_url,
                }
            items.append({
                "id": str(u.id),
                "handle": u.handle,
                "displayName": u.display_name,
                "avatar": avatar,
                "followedByViewer": followed,
                "createdAt": rel_created_at.isoformat().replace("+00:00", "Z") if hasattr(rel_created_at, "isoformat") else str(rel_created_at),
            })
        return items

    async def list_following(
        self,
        user_id: str,
        viewer_id: Optional[str] = None,
        cursor_tuple: Optional[Tuple[datetime, str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        user_uuid = uuid.UUID(user_id)
        viewer_uuid = uuid.UUID(viewer_id) if viewer_id else None

        followed_by_viewer_sq = (
            select(
                exists(
                    select(1).where(
                        and_(
                            Follow.follower_id == viewer_uuid,
                            Follow.following_id == User.id,
                            Follow.status == "accepted",
                        )
                    )
                )
            ).scalar_subquery() if viewer_uuid else select(False).scalar_subquery()
        )

        stmt = (
            select(
                User,
                Follow.created_at.label("rel_created_at"),
                followed_by_viewer_sq.label("followed_by_viewer"),
            )
            .join(Follow, Follow.following_id == User.id)
            .where(
                and_(
                    Follow.follower_id == user_uuid,
                    Follow.status == "accepted",
                    User.is_active.is_(True),
                )
            )
            .order_by(Follow.created_at.desc(), User.id.desc())
            .limit(limit + 1)
        )

        if cursor_tuple:
            c_time, c_id = cursor_tuple
            c_uuid = uuid.UUID(c_id)
            stmt = stmt.where(
                or_(
                    Follow.created_at < c_time,
                    and_(
                        Follow.created_at == c_time,
                        User.id < c_uuid,
                    ),
                )
            )

        res = await self._session.execute(stmt)
        rows = res.all()
        items = []
        for row in rows:
            u, rel_created_at, followed = row[0], row[1], bool(row[2])
            avatar = None
            if u.avatar_small_url or u.avatar_large_url:
                avatar = {
                    "smallUrl": u.avatar_small_url,
                    "largeUrl": u.avatar_large_url,
                }
            items.append({
                "id": str(u.id),
                "handle": u.handle,
                "displayName": u.display_name,
                "avatar": avatar,
                "followedByViewer": followed,
                "createdAt": rel_created_at.isoformat().replace("+00:00", "Z") if hasattr(rel_created_at, "isoformat") else str(rel_created_at),
            })
        return items

    async def get_repost_count(self, post_id: str) -> int:
        post_uuid = uuid.UUID(post_id)
        stmt = select(func.count(Post.id)).where(
            and_(Post.kind == "repost", Post.repost_of_id == post_uuid)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create_repost(self, user_id: str, post_id: str) -> Dict[str, Any]:
        user_uuid = uuid.UUID(user_id)
        post_uuid = uuid.UUID(post_id)

        post_kind = await self.get_post_kind(post_id)
        if post_kind is None:
            raise NotFoundError("Post not found", [{"field": "postId", "reason": "not_found"}])
        if post_kind == "repost":
            raise ValidationError("Reposting a repost is rejected", [{"field": "postId", "reason": "invalid_kind"}], status_code=422)

        existing_lookup = await self.get_repost_lookup(user_id, post_id)
        if not existing_lookup:
            repost_id = uuid.uuid4()
            stmt = pg_insert(Post).values(
                id=repost_id,
                author_id=user_uuid,
                kind="repost",
                repost_of_id=post_uuid,
                created_at=datetime.now(),
            )
            await self._session.execute(stmt)

            target_post = None
            if hasattr(self._session, "get"):
                res = self._session.get(Post, post_uuid)
                if inspect.isawaitable(res):
                    target_post = await res
            if target_post:
                await self._create_notification(
                    recipient_id=target_post.author_id,
                    actor_id=user_uuid,
                    event_type="repost",
                    target_post_id=post_uuid,
                )

            await self._session.commit()

        repost_count = await self.get_repost_count(post_id)
        return {
            "postId": post_id,
            "repostedByViewer": True,
            "repostCount": repost_count,
        }

    async def remove_repost(self, user_id: str, post_id: str) -> Dict[str, Any]:
        user_uuid = uuid.UUID(user_id)
        post_uuid = uuid.UUID(post_id)

        stmt = delete(Post).where(
            and_(
                Post.kind == "repost",
                Post.author_id == user_uuid,
                Post.repost_of_id == post_uuid,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

        repost_count = await self.get_repost_count(post_id)
        return {
            "postId": post_id,
            "repostedByViewer": False,
            "repostCount": repost_count,
        }

    async def update_user_profile(
        self,
        user_id: str,
        fields: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Updates allowed fields on a user profile.
        Returns the updated user profile dict or None if user not found.
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None

        user = await self._session.get(User, user_uuid)
        if not user or not user.is_active:
            return None

        if "display_name" in fields and fields["display_name"] is not None:
            user.display_name = fields["display_name"]
        if "bio" in fields:
            user.bio = fields["bio"]
        if "avatar_small_url" in fields:
            user.avatar_small_url = fields["avatar_small_url"]
        if "avatar_large_url" in fields:
            user.avatar_large_url = fields["avatar_large_url"]
        if "is_private" in fields and fields["is_private"] is not None:
            user.is_private = fields["is_private"]

        await self._session.commit()
        return await self.get_user_profile(user_id, viewer_id=user_id)

    async def deactivate_user(
        self,
        user_id: str,
    ) -> bool:
        """
        Deactivates a user account (is_active = False) and revokes active sessions.
        Returns True if deactivated, False if user not found.
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return False

        user = await self._session.get(User, user_uuid)
        if not user or not user.is_active:
            return False

        user.is_active = False

        now = datetime.now()
        stmt = (
            update(Session)
            .where(and_(Session.user_id == user_uuid, Session.revoked_at.is_(None)))
            .values(revoked_at=now)
        )
        await self._session.execute(stmt)
        await self._session.commit()
        return True

    async def update_post(
        self,
        post_id: str,
        author_id: str,
        text: str,
        expected_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Updates an existing original or reply post's text.
        Enforces:
        - Post existence and not deleted (404)
        - Author ownership (403 if not owner)
        - Kind is original or reply (422 if repost)
        - Valid text length (1 to 280 chars) (422)
        - Optimistic concurrency control (409 if version mismatch)
        Returns updated post detail.
        """
        post_uuid = uuid.UUID(post_id)
        author_uuid = uuid.UUID(author_id)
        clean_text = text.strip()
        if not (1 <= len(clean_text) <= 280):
            raise ValidationError(
                "Post text must be between 1 and 280 characters",
                details=[{"field": "text", "reason": "length"}],
                status_code=422,
            )

        post = await self._session.get(Post, post_uuid)
        if not post or post.deleted_at is not None:
            raise NotFoundError(
                "Post not found",
                details=[{"field": "postId", "reason": "not_found"}],
            )

        if post.author_id != author_uuid:
            raise ForbiddenError(
                "You are not authorized to edit another author's post",
                details=[{"field": "authorId", "reason": "forbidden_cross_user_mutation"}],
            )

        if post.kind not in ("original", "reply"):
            raise ValidationError(
                "Only original and reply posts can be edited",
                details=[{"field": "kind", "reason": "invalid_kind"}],
                status_code=422,
            )

        if expected_version is not None and post.version != expected_version:
            raise ConflictError(
                f"Post was modified by another request. Current version is {post.version}, expected {expected_version}",
                details=[{"field": "version", "reason": "stale_version_conflict"}],
            )

        post.text = clean_text
        post.version = post.version + 1
        post.updated_at = datetime.now()

        await self._session.commit()
        return await self.get_post_detail(post_id=post_id, viewer_id=author_id)  # type: ignore

    async def delete_post(
        self,
        post_id: str,
        author_id: str,
    ) -> bool:
        """
        Soft-deletes a post owned by author_id.
        Sets deleted_at = CURRENT_TIMESTAMP.
        Idempotent:
        - If post does not exist -> 404
        - If post author != author_id -> 403
        - If post already deleted -> returns True (204 No Content)
        - If post active -> sets deleted_at, commits, returns True
        """
        post_uuid = uuid.UUID(post_id)
        author_uuid = uuid.UUID(author_id)

        post = await self._session.get(Post, post_uuid)
        if not post:
            raise NotFoundError(
                "Post not found",
                details=[{"field": "postId", "reason": "not_found"}],
            )

        if post.author_id != author_uuid:
            raise ForbiddenError(
                "You are not authorized to delete another author's post",
                details=[{"field": "authorId", "reason": "forbidden_cross_user_mutation"}],
            )

        if post.deleted_at is not None:
            # Idempotent: already deleted by owner
            return True

        post.deleted_at = datetime.now()
        await self._session.commit()
        return True

    # -----------------------------------------------------------------------
    # Stage 6 Notification Inbox Implementation
    # -----------------------------------------------------------------------
    async def _create_notification(
        self,
        recipient_id: uuid.UUID,
        actor_id: uuid.UUID,
        event_type: str,
        target_post_id: Optional[uuid.UUID] = None,
    ) -> None:
        """
        Creates an event notification within the current transaction.
        Enforces self-notification suppression and idempotent deduplication.
        """
        if recipient_id == actor_id:
            return

        # Explicit idempotency check across all event types (handles NULL target_post_id)
        filter_post = (Notification.target_post_id == target_post_id) if target_post_id is not None else Notification.target_post_id.is_(None)
        existing = await self._session.execute(
            select(Notification.id).where(
                Notification.recipient_id == recipient_id,
                Notification.actor_id == actor_id,
                Notification.event_type == event_type,
                filter_post,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return

        stmt = (
            pg_insert(Notification)
            .values(
                id=uuid.uuid4(),
                recipient_id=recipient_id,
                actor_id=actor_id,
                event_type=event_type,
                target_post_id=target_post_id,
                created_at=datetime.now(),
            )
            .on_conflict_do_nothing(index_elements=["recipient_id", "actor_id", "event_type", "target_post_id"])
        )
        await self._session.execute(stmt)

    async def list_notifications(
        self,
        recipient_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves cursor-paginated notifications for recipient_id ordered by (created_at DESC, id DESC).
        Includes actor information and target post information (with tombstone display if deleted).
        """
        recipient_uuid = uuid.UUID(recipient_id)

        stmt = (
            select(Notification)
            .options(
                selectinload(Notification.actor),
                selectinload(Notification.target_post),
            )
            .where(Notification.recipient_id == recipient_uuid)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit + 1)
        )

        if cursor_tuple is not None:
            c_time, c_id = cursor_tuple
            c_uuid = uuid.UUID(c_id)
            stmt = stmt.where(
                or_(
                    Notification.created_at < c_time,
                    and_(
                        Notification.created_at == c_time,
                        Notification.id < c_uuid,
                    ),
                )
            )

        res = await self._session.execute(stmt)
        rows = res.scalars().all()

        results = []
        for n in rows:
            target_post_data = None
            if n.target_post_id is not None:
                if n.target_post:
                    is_del = n.target_post.deleted_at is not None
                    target_post_data = {
                        "id": str(n.target_post.id),
                        "kind": n.target_post.kind if not is_del else None,
                        "text": n.target_post.text if not is_del else "[Deleted]",
                        "isDeleted": is_del,
                        "replyToId": str(n.target_post.reply_to_id) if n.target_post.reply_to_id else None,
                    }
                else:
                    target_post_data = {
                        "id": str(n.target_post_id),
                        "kind": None,
                        "text": "[Deleted]",
                        "isDeleted": True,
                        "replyToId": None,
                    }

            results.append({
                "id": str(n.id),
                "eventType": n.event_type,
                "createdAt": n.created_at.isoformat().replace("+00:00", "Z") if hasattr(n.created_at, "isoformat") else str(n.created_at),
                "readAt": n.read_at.isoformat().replace("+00:00", "Z") if (n.read_at and hasattr(n.read_at, "isoformat")) else (str(n.read_at) if n.read_at else None),
                "isRead": n.read_at is not None,
                "actor": self._format_author_dict(n.actor),
                "targetPost": target_post_data,
            })
        return results

    async def get_unread_notification_count(
        self,
        recipient_id: str,
    ) -> int:
        """
        Returns authoritative count of unread notifications for recipient_id.
        """
        recipient_uuid = uuid.UUID(recipient_id)
        stmt = (
            select(func.count(Notification.id))
            .where(
                and_(
                    Notification.recipient_id == recipient_uuid,
                    Notification.read_at.is_(None),
                )
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar() or 0

    async def mark_notifications_read(
        self,
        recipient_id: str,
        notification_id: Optional[str] = None,
    ) -> Tuple[int, int]:
        """
        Marks single notification or all unread notifications for recipient as read.
        Returns (marked_count, remaining_unread_count).
        """
        recipient_uuid = uuid.UUID(recipient_id)
        now = datetime.now()

        if notification_id is not None:
            notif_uuid = uuid.UUID(notification_id)
            notif = await self._session.get(Notification, notif_uuid)
            if not notif:
                raise NotFoundError("Notification not found", details=[{"field": "notificationId", "reason": "not_found"}])
            if notif.recipient_id != recipient_uuid:
                raise ForbiddenError("Forbidden access to notification", details=[{"field": "notificationId", "reason": "wrong_recipient"}])

            marked_count = 0
            if notif.read_at is None:
                notif.read_at = now
                marked_count = 1
                await self._session.commit()

            unread = await self.get_unread_notification_count(recipient_id)
            return marked_count, unread
        else:
            stmt = (
                update(Notification)
                .where(
                    and_(
                        Notification.recipient_id == recipient_uuid,
                        Notification.read_at.is_(None),
                    )
                )
                .values(read_at=now)
            )
            res = await self._session.execute(stmt)
            marked_count = res.rowcount or 0
            await self._session.commit()

            unread = await self.get_unread_notification_count(recipient_id)
            return marked_count, unread



