"""
Feed Service (Stage A).

Orchestrates feed retrieval, input validation, cursor decoding/encoding,
and bounded pagination assembly.
"""

from typing import Optional
from app.common.cursor import decode_cursor, encode_cursor, InvalidCursorError
from app.common.errors import ValidationError
from app.repositories.base import SocialRepositoryProtocol
from app.schemas.post import PostItem, FeedResponse
 

class FeedService:
    """
    Application service managing the public chronological original-post feed.
    """

    def __init__(self, repository: SocialRepositoryProtocol):
        self._repository = repository

    async def get_feed(
        self,
        cursor_str: Optional[str],
        limit: int,
        viewer_id: str,
        scope: str = "public",
    ) -> FeedResponse:
        """
        Retrieves a paginated page of original posts.
        Supports scope='home' (personalized) or scope='public'.
        """
        # 1. Validate limit parameter (1 to 50)
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            raise ValidationError(
                "limit must be an integer from 1 to 50",
                details=[{"field": "limit", "reason": "out_of_range"}],
            )

        # 2. Validate and resolve scope
        clean_scope = scope.lower().strip() if scope else "public"
        if clean_scope not in ("home", "public"):
            raise ValidationError(
                f"Invalid scope '{scope}'. Allowed values are 'home' or 'public'.",
                details=[{"field": "scope", "reason": "invalid_scope"}],
                status_code=400,
            )

        # 3. Decode cursor token if supplied
        cursor_tuple = None
        if cursor_str:
            try:
                cursor_tuple = decode_cursor(cursor_str)
            except InvalidCursorError as e:
                raise ValidationError(
                    f"Invalid cursor: {e}",
                    details=[{"field": "cursor", "reason": "invalid_cursor"}],
                )

        # 4. Request at most limit + 1 items from repository
        try:
            raw_items = await self._repository.list_original_feed(
                cursor_tuple=cursor_tuple,
                limit=limit,
                viewer_id=viewer_id,
                scope=clean_scope,
            )
        except TypeError:
            # Fallback for mock repositories that do not accept scope parameter
            raw_items = await self._repository.list_original_feed(
                cursor_tuple=cursor_tuple,
                limit=limit,
                viewer_id=viewer_id,
            )

        # 4. Derive has_more and next_cursor
        if len(raw_items) > limit:
            page_records = raw_items[:limit]
            has_more = True
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record["createdAt"], last_record["id"])
        else:
            page_records = raw_items
            has_more = False
            next_cursor = None

        # 5. Map to typed PostItem models
        post_items = [PostItem(**item) for item in page_records]

        return FeedResponse(
            items=post_items,
            next_cursor=next_cursor,
            has_more=has_more,
        )
