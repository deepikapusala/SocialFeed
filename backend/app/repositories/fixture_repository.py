"""
In-Memory Fixture Repository Implementation (Stage A).

Implements SocialRepositoryProtocol using the deterministic fixture dataset.
Contains no SQL, no database sessions, and no network calls.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from app.fixtures.data import (
    FIXTURE_USERS,
    FIXTURE_ORIGINALS,
    FIXTURE_REPLIES,
    FIXTURE_REPOSTS,
    FIXTURE_MEDIA,
    FIXTURE_LIKES,
    FIXTURE_FOLLOWS,
    ALL_FIXTURE_POSTS,
)


class FixtureRepository:
    """
    In-memory implementation of SocialRepositoryProtocol backed by fixed fixtures.
    """

    def __init__(self, simulated_io_ms: int = 0):
        self.simulated_io_ms = max(0, min(1000, simulated_io_ms))
        self._users = FIXTURE_USERS
        self._originals = FIXTURE_ORIGINALS
        self._replies = FIXTURE_REPLIES
        self._reposts = FIXTURE_REPOSTS
        self._media = FIXTURE_MEDIA
        self._likes = FIXTURE_LIKES
        self._follows = FIXTURE_FOLLOWS
        self._all_posts = ALL_FIXTURE_POSTS

    async def _simulate_io(self) -> None:
        """Simulates non-blocking async I/O delay when configured."""
        if self.simulated_io_ms > 0:
            await asyncio.sleep(self.simulated_io_ms / 1000.0)

    # -----------------------------------------------------------------------
    # Helper Assemblers
    # -----------------------------------------------------------------------
    def _find_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        for u in self._users:
            if u["id"] == user_id:
                return u
        return None

    def _is_following(self, follower_id: Optional[str], following_id: str) -> bool:
        if not follower_id:
            return False
        return any(
            f["followerId"] == follower_id and f["followingId"] == following_id
            for f in self._follows
        )

    def _get_author_dict(self, user_id: str, viewer_id: Optional[str] = None) -> Dict[str, Any]:
        user = self._find_user(user_id)
        followed_by_viewer = self._is_following(viewer_id, user_id)
        if not user:
            return {
                "id": user_id,
                "handle": "unknown_user",
                "displayName": "Unknown User",
                "avatar": None,
                "followedByViewer": followed_by_viewer,
            }
        return {
            "id": user["id"],
            "handle": user["handle"],
            "displayName": user["displayName"],
            "avatar": user.get("avatar"),
            "followedByViewer": followed_by_viewer,
        }

    def _get_media_for_post(self, post_id: str) -> List[Dict[str, Any]]:
        post_media = [m for m in self._media if m["postId"] == post_id]
        post_media.sort(key=lambda m: m["position"])
        return [
            {
                "id": m["id"],
                "altText": m["altText"],
                "width": m["width"],
                "height": m["height"],
                "position": m["position"],
                "smallUrl": m["smallUrl"],
                "largeUrl": m["largeUrl"],
            }
            for m in post_media
        ]

    def _count_likes(self, post_id: str) -> int:
        return sum(1 for lk in self._likes if lk["postId"] == post_id)

    def _count_replies(self, post_id: str) -> int:
        return sum(1 for r in self._replies if r["replyToId"] == post_id)

    def _count_reposts(self, post_id: str) -> int:
        return sum(1 for p in self._reposts if p.get("repostOfId") == post_id)

    def _is_liked_by_viewer(self, post_id: str, viewer_id: str) -> bool:
        return any(lk["userId"] == viewer_id and lk["postId"] == post_id for lk in self._likes)

    def _is_reposted_by_viewer(self, post_id: str, viewer_id: str) -> bool:
        return any(p.get("repostOfId") == post_id and p.get("authorId") == viewer_id for p in self._reposts)

    def _assemble_post(self, post_raw: Dict[str, Any], viewer_id: str) -> Dict[str, Any]:
        post_id = post_raw["id"]
        return {
            "id": post_id,
            "kind": post_raw["kind"],
            "text": post_raw.get("text"),
            "createdAt": post_raw["createdAt"],
            "author": self._get_author_dict(post_raw["authorId"], viewer_id),
            "media": self._get_media_for_post(post_id) if post_raw["kind"] == "original" else [],
            "likeCount": self._count_likes(post_id),
            "replyCount": self._count_replies(post_id),
            "repostCount": self._count_reposts(post_id),
            "likedByViewer": self._is_liked_by_viewer(post_id, viewer_id),
            "repostedByViewer": self._is_reposted_by_viewer(post_id, viewer_id),
            "replyToId": post_raw.get("replyToId"),
            "repostOfId": post_raw.get("repostOfId"),
        }

    @staticmethod
    def _is_strictly_before(
        item_created_at: datetime,
        item_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
    ) -> bool:
        if cursor_tuple is None:
            return True
        cursor_time, cursor_id = cursor_tuple
        # Tuple comparison for descending order (created_at DESC, id DESC)
        if item_created_at < cursor_time:
            return True
        if item_created_at == cursor_time and item_id < cursor_id:
            return True
        return False

    # -----------------------------------------------------------------------
    # Protocol Methods
    # -----------------------------------------------------------------------
    async def list_original_feed(
        self,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        await self._simulate_io()

        # 1. Filter only original posts
        originals = list(self._originals)

        # 2. Sort descending by (createdAt DESC, id DESC)
        originals.sort(key=lambda p: (p["createdAt"], p["id"]), reverse=True)

        # 3. Apply tuple predicate strictly
        filtered = [
            p for p in originals
            if self._is_strictly_before(p["createdAt"], p["id"], cursor_tuple)
        ]

        # 4. Fetch at most limit + 1 items
        batch = filtered[: limit + 1]

        # 5. Assemble full post contracts
        return [self._assemble_post(p, viewer_id) for p in batch]

    async def get_post_detail(
        self,
        post_id: str,
        viewer_id: str,
    ) -> Optional[Dict[str, Any]]:
        await self._simulate_io()
        for p in self._all_posts:
            if p["id"] == post_id:
                return self._assemble_post(p, viewer_id)
        return None

    async def get_user_profile(
        self,
        user_id: str,
        viewer_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        await self._simulate_io()
        user = self._find_user(user_id)
        if not user:
            return None

        # Count statistics accurately
        post_count = sum(1 for p in self._originals if p["authorId"] == user_id)
        follower_count = sum(1 for f in self._follows if f["followingId"] == user_id)
        following_count = sum(1 for f in self._follows if f["followerId"] == user_id)
        followed_by_viewer = self._is_following(viewer_id, user_id) if viewer_id else False

        return {
            "id": user["id"],
            "handle": user["handle"],
            "displayName": user["displayName"],
            "bio": user.get("bio"),
            "avatar": user.get("avatar"),
            "postCount": post_count,
            "followerCount": follower_count,
            "followingCount": following_count,
            "followedByViewer": followed_by_viewer,
        }

    async def follow_user(
        self,
        follower_id: str,
        following_id: str,
    ) -> Tuple[bool, int]:
        await self._simulate_io()
        if follower_id == following_id:
            raise ValueError("Self-follow is not allowed.")
        if not any(f["followerId"] == follower_id and f["followingId"] == following_id for f in self._follows):
            self._follows.append({
                "followerId": follower_id,
                "followingId": following_id,
                "createdAt": datetime.utcnow().isoformat() + "Z"
            })
        follower_count = sum(1 for f in self._follows if f["followingId"] == following_id)
        return True, follower_count

    async def unfollow_user(
        self,
        follower_id: str,
        following_id: str,
    ) -> Tuple[bool, int]:
        await self._simulate_io()
        self._follows = [
            f for f in self._follows
            if not (f["followerId"] == follower_id and f["followingId"] == following_id)
        ]
        follower_count = sum(1 for f in self._follows if f["followingId"] == following_id)
        return False, follower_count

    async def is_following(
        self,
        follower_id: str,
        following_id: str,
    ) -> bool:
        await self._simulate_io()
        return self._is_following(follower_id, following_id)

    async def list_direct_replies(
        self,
        post_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        await self._simulate_io()
        replies = [r for r in self._replies if r["replyToId"] == post_id]
        replies.sort(key=lambda r: (r["createdAt"], r["id"]), reverse=True)

        filtered = [
            r for r in replies
            if self._is_strictly_before(r["createdAt"], r["id"], cursor_tuple)
        ]
        batch = filtered[: limit + 1]
        return [self._assemble_post(r, viewer_id) for r in batch]

    async def list_profile_media(
        self,
        user_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        await self._simulate_io()
        user_original_ids = {p["id"] for p in self._originals if p["authorId"] == user_id}
        user_media = [m for m in self._media if m["postId"] in user_original_ids]
        user_media.sort(key=lambda m: (m["createdAt"], m["id"]), reverse=True)

        filtered = [
            m for m in user_media
            if self._is_strictly_before(m["createdAt"], m["id"], cursor_tuple)
        ]
        batch = filtered[: limit + 1]
        return [
            {
                "id": m["id"],
                "postId": m["postId"],
                "altText": m["altText"],
                "width": m["width"],
                "height": m["height"],
                "position": m["position"],
                "smallUrl": m["smallUrl"],
                "largeUrl": m["largeUrl"],
                "createdAt": m["createdAt"],
            }
            for m in batch
        ]

    async def search_originals(
        self,
        query: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        await self._simulate_io()
        clean_query = query.strip().lower()

        # Case-insensitive literal substring match on original post text
        matches = [
            p for p in self._originals
            if p.get("text") and clean_query in p["text"].lower()
        ]
        matches.sort(key=lambda p: (p["createdAt"], p["id"]), reverse=True)

        filtered = [
            p for p in matches
            if self._is_strictly_before(p["createdAt"], p["id"], cursor_tuple)
        ]
        batch = filtered[: limit + 1]
        return [self._assemble_post(p, viewer_id) for p in batch]

    async def user_exists(self, user_id: str) -> bool:
        await self._simulate_io()
        return any(u["id"] == user_id for u in self._users)

    async def get_post_kind(self, post_id: str) -> Optional[str]:
        await self._simulate_io()
        for p in self._all_posts:
            if p["id"] == post_id:
                return p["kind"]
        return None

    async def create_repost(self, user_id: str, post_id: str) -> Dict[str, Any]:
        await self._simulate_io()
        if not any(r.get("repostOfId") == post_id and r.get("authorId") == user_id for r in self._reposts):
            import uuid
            self._reposts.append({
                "id": str(uuid.uuid4()),
                "authorId": user_id,
                "kind": "repost",
                "repostOfId": post_id,
                "createdAt": datetime.utcnow().isoformat() + "Z",
            })
        repost_count = self._count_reposts(post_id)
        return {
            "postId": post_id,
            "repostedByViewer": True,
            "repostCount": repost_count,
        }

    async def remove_repost(self, user_id: str, post_id: str) -> Dict[str, Any]:
        await self._simulate_io()
        self._reposts = [
            r for r in self._reposts
            if not (r.get("repostOfId") == post_id and r.get("authorId") == user_id)
        ]
        repost_count = self._count_reposts(post_id)
        return {
            "postId": post_id,
            "repostedByViewer": False,
            "repostCount": repost_count,
        }
