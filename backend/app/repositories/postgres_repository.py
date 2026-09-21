"""
PostgreSQL Repository Implementation (Stage C).

Implements SocialRepositoryProtocol and Stage C persistence requirements using
SQLAlchemy 2.x async ORM and Core against PostgreSQL (instagram_modeling).
Reference: docs/05_Python_Database_Integration_PRD.md
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import (
    and_,
    delete,
    exists,
    func,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.common.errors import ConflictError, NotFoundError, ValidationError
from app.models import Follow, Post, PostLike, PostMedia, User


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
    def _format_author_dict(user: User) -> Dict[str, Any]:
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
        referenced_author_handle: Optional[str] = None,
        referenced_text: Optional[str] = None,
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
            "author": self._format_author_dict(post.author),
            "media": media_list,
            "likeCount": like_count,
            "replyCount": reply_count,
            "likedByViewer": liked_by_viewer,
            "replyToId": str(post.reply_to_id) if post.reply_to_id else None,
            "repostOfId": str(post.repost_of_id) if post.repost_of_id else None,
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

        stmt = (
            select(
                Post,
                like_count_sq.label("like_count"),
                reply_count_sq.label("reply_count"),
                liked_by_viewer_sq.label("liked_by_viewer"),
            )
            .join(Post.author)
            .options(
                selectinload(Post.author),
                selectinload(Post.media),
            )
            .where(Post.kind == "original")
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
            .where(Post.id == post_uuid)
        )

        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None

        post, like_cnt, reply_cnt, liked = row[0], row[1] or 0, row[2] or 0, bool(row[3])
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

        return self._assemble_post_dict(
            post=post,
            like_count=like_cnt,
            reply_count=reply_cnt,
            liked_by_viewer=liked,
            referenced_author_handle=ref_handle,
            referenced_text=ref_text,
        )

    async def get_user_profile(
        self,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None

        # Scalar subqueries for profile counts
        post_count_sq = (
            select(func.count(Post.id))
            .where(and_(Post.author_id == user_uuid, Post.kind == "original"))
            .scalar_subquery()
        )
        follower_count_sq = (
            select(func.count(Follow.follower_id))
            .where(Follow.following_id == user_uuid)
            .scalar_subquery()
        )
        following_count_sq = (
            select(func.count(Follow.following_id))
            .where(Follow.follower_id == user_uuid)
            .scalar_subquery()
        )

        stmt = select(
            User,
            post_count_sq.label("post_count"),
            follower_count_sq.label("follower_count"),
            following_count_sq.label("following_count"),
        ).where(User.id == user_uuid)

        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None

        user, post_cnt, follower_cnt, following_cnt = row[0], row[1] or 0, row[2] or 0, row[3] or 0
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
            .where(and_(Post.kind == "reply", Post.reply_to_id == parent_uuid))
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
            .where(and_(Post.author_id == user_uuid, Post.kind == "original"))
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

    async def get_post_kind(self, post_id: str) -> Optional[str]:
        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            return None
        stmt = select(Post.kind).where(Post.id == post_uuid)
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
