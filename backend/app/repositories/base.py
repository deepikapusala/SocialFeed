"""
Social Repository Protocol / Interface (Stage A).

Defines the abstract contract for data access operations.
Will be implemented by FixtureRepository in Stage A and PostgreSQL repository in Stage C.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Protocol, Tuple, runtime_checkable


@runtime_checkable
class SocialRepositoryProtocol(Protocol):
    """
    Protocol defining the data access boundary for social feed operations.
    """

    async def list_original_feed(
        self,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetches at most limit + 1 original posts ordered by (createdAt DESC, id DESC)
        where (createdAt, id) < cursor_tuple.
        """
        ...

    async def get_post_detail(
        self,
        post_id: str,
        viewer_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches post detail by UUID, including author, media, counts, and likedByViewer.
        """
        ...

    async def get_user_profile(
        self,
        user_id: str,
        viewer_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches user profile by UUID, including author info, bio, avatar, statistics,
        and followedByViewer state.
        """
        ...

    async def follow_user(
        self,
        follower_id: str,
        following_id: str,
    ) -> Tuple[bool, int]:
        """
        Establishes a follow edge between follower_id and following_id.
        Returns (followedByViewer, updatedFollowerCount).
        """
        ...

    async def unfollow_user(
        self,
        follower_id: str,
        following_id: str,
    ) -> Tuple[bool, int]:
        """
        Removes a follow edge between follower_id and following_id.
        Returns (followedByViewer, updatedFollowerCount).
        """
        ...

    async def is_following(
        self,
        follower_id: str,
        following_id: str,
    ) -> bool:
        """
        Checks if follower_id is following following_id.
        """
        ...

    async def list_direct_replies(
        self,
        post_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetches at most limit + 1 direct replies to the specified original post.
        """
        ...

    async def list_profile_media(
        self,
        user_id: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetches at most limit + 1 media rows from the specified user's original posts.
        """
        ...

    async def search_originals(
        self,
        query: str,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Performs a case-insensitive literal substring search on original posts.
        """
        ...

    async def user_exists(self, user_id: str) -> bool:
        """
        Checks if a user with the given UUID exists.
        """
        ...

    async def get_post_kind(self, post_id: str) -> Optional[str]:
        """
        Returns the kind ('original', 'reply', 'repost') of a post if it exists.
        """
        ...

    async def create_repost(self, user_id: str, post_id: str) -> Dict[str, Any]:
        """
        Creates a repost of an original post for viewer.
        Returns Dict with postId, repostedByViewer, repostCount.
        """
        ...

    async def remove_repost(self, user_id: str, post_id: str) -> Dict[str, Any]:
        """
        Removes a repost of an original post for viewer.
        Returns Dict with postId, repostedByViewer, repostCount.
        """
        ...
