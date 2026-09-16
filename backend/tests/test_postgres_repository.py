"""
Unit and integration tests for PostgresRepository (Stage C Step 3).
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.common.errors import ConflictError, NotFoundError, ValidationError
from app.repositories.base import SocialRepositoryProtocol
from app.repositories.postgres_repository import PostgresRepository
from app.models import Post, User, PostMedia


def test_postgres_repository_implements_protocol():
    """Verify PostgresRepository satisfies the SocialRepositoryProtocol interface."""
    dummy_session = MagicMock()
    repo = PostgresRepository(session=dummy_session)
    assert isinstance(repo, SocialRepositoryProtocol)


@pytest.mark.asyncio
async def test_create_original_validation_errors():
    """Verify create_post validates text length and media cap for originals."""
    session = MagicMock()
    repo = PostgresRepository(session=session)
    repo.user_exists = AsyncMock(return_value=True)

    # Empty text error
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="original",
            text="",
        )
    assert exc.value.status_code == 422

    # Exceeding 280 chars
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="original",
            text="A" * 281,
        )
    assert exc.value.status_code == 422

    # Media cap > 4
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="original",
            text="Valid text",
            media=[{"altText": "img"} for _ in range(5)],
        )
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_reply_validation_errors():
    """Verify create_post validates parent post existence and kind for replies."""
    session = MagicMock()
    repo = PostgresRepository(session=session)
    repo.user_exists = AsyncMock(return_value=True)

    # Missing reply_to_id
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="reply",
            text="Reply text",
        )
    assert exc.value.status_code == 422

    # Missing parent post (404)
    repo.get_post_kind = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="reply",
            reply_to_id=str(uuid.uuid4()),
            text="Reply text",
        )
    assert exc.value.status_code == 404

    # Non-original parent post (422)
    repo.get_post_kind = AsyncMock(return_value="reply")
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="reply",
            reply_to_id=str(uuid.uuid4()),
            text="Reply text",
        )
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_repost_validation_errors():
    """Verify create_post validates repost rules and duplicate prevention."""
    session = MagicMock()
    repo = PostgresRepository(session=session)
    repo.user_exists = AsyncMock(return_value=True)

    # Missing repost_of_id
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="repost",
        )
    assert exc.value.status_code == 422

    # Repost containing text is rejected
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="repost",
            repost_of_id=str(uuid.uuid4()),
            text="Text not allowed",
        )
    assert exc.value.status_code == 422

    # Non-original target (422)
    repo.get_post_kind = AsyncMock(return_value="repost")
    with pytest.raises(ValidationError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="repost",
            repost_of_id=str(uuid.uuid4()),
        )
    assert exc.value.status_code == 422

    # Duplicate repost conflict (409)
    repo.get_post_kind = AsyncMock(return_value="original")
    repo.get_repost_lookup = AsyncMock(return_value={"repostId": str(uuid.uuid4())})
    with pytest.raises(ConflictError) as exc:
        await repo.create_post(
            author_id=str(uuid.uuid4()),
            kind="repost",
            repost_of_id=str(uuid.uuid4()),
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_like_repost_rejected():
    """Verify set_like and remove_like reject liking a repost row with 422."""
    session = MagicMock()
    repo = PostgresRepository(session=session)
    repo.get_post_kind = AsyncMock(return_value="repost")

    with pytest.raises(ValidationError) as exc:
        await repo.set_like(user_id=str(uuid.uuid4()), post_id=str(uuid.uuid4()))
    assert exc.value.status_code == 422

    with pytest.raises(ValidationError) as exc:
        await repo.remove_like(user_id=str(uuid.uuid4()), post_id=str(uuid.uuid4()))
    assert exc.value.status_code == 422
