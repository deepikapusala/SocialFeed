"""
Dependency Injection Foundation (Stage A & C).

Defines dependency providers for:
1. Repository interface provider (PostgresRepository with FixtureRepository fallback/override).
2. Development actor identity (DEMO_USER_ID from settings).
3. Active request ID.
4. Async database session.
"""

import uuid
from typing import Any
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_async_session
from app.common.middleware import get_current_request_id
from app.repositories.base import SocialRepositoryProtocol
from app.repositories.fixture_repository import FixtureRepository
from app.repositories.postgres_repository import PostgresRepository


def get_fixture_repository() -> SocialRepositoryProtocol:
    """Provides the in-memory FixtureRepository for Stage A and unit tests."""
    return FixtureRepository()


def get_postgres_repository(
    session: AsyncSession = Depends(get_async_session),
) -> SocialRepositoryProtocol:
    """Provides the request-scoped PostgresRepository bound to the current AsyncSession."""
    return PostgresRepository(session=session)


def get_repository(
    session: AsyncSession = Depends(get_async_session),
) -> SocialRepositoryProtocol:
    """
    Main repository dependency provider for FastAPI routes.
    Returns request-scoped PostgresRepository bound to an active AsyncSession.
    Can be overridden in tests via app.dependency_overrides[get_repository].
    """
    return PostgresRepository(session=session)


def get_current_actor_id(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Resolves the development identity actor ID.
    Prioritizes x-viewer-id header if present and valid UUID,
    otherwise falls back to DEMO_USER_ID from settings.
    """
    header_val = request.headers.get("x-viewer-id")
    if header_val:
        try:
            uuid.UUID(header_val)
            return header_val
        except ValueError:
            pass
    return settings.DEMO_USER_ID


def get_request_id(request: Request) -> str:
    """
    Retrieves the active request ID from request.state or contextvar.
    """
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return get_current_request_id()
