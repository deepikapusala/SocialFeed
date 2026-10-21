"""
Dependency Injection Foundation (Stage A & C).

Defines dependency providers for:
1. Repository interface provider (PostgresRepository with FixtureRepository fallback/override).
2. Development actor identity (DEMO_USER_ID from settings).
3. Active request ID.
4. Async database session.
"""

import uuid
from typing import Any, Optional
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


from app.common.errors import UnauthorizedError
from app.models import User
from app.services.auth_service import AuthService


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    """Provides the AuthService bound to the current request AsyncSession."""
    return AuthService(session=session)


async def get_required_actor(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Strict dependency for authenticated routes.
    Extracts Bearer token, verifies active session, and returns User ORM instance.
    Raises 401 Unauthorized if missing, malformed, expired, or revoked.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError(
            "Authentication required",
            details=[{"field": "Authorization", "reason": "missing_bearer_token"}],
        )

    raw_token = auth_header[7:].strip()
    if not raw_token:
        raise UnauthorizedError(
            "Authentication required",
            details=[{"field": "Authorization", "reason": "empty_bearer_token"}],
        )

    return await auth_service.verify_session_token(raw_token)


async def get_required_actor_id(
    actor: User = Depends(get_required_actor),
) -> str:
    """Returns the verified actor UUID string for strictly authenticated routes."""
    return str(actor.id)


async def get_current_actor_id(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> Optional[str]:
    """
    Resolves the actor ID for routes that support both authenticated and development actors.
    1. If 'Authorization: Bearer <token>' is provided, resolves actor from verified session.
    2. In non-production environments (test/development):
       - If 'x-viewer-id' header is provided with valid UUID (tests), returns it.
       - Falls back to DEMO_USER_ID from settings for Stage A/C V1 backwards compatibility.
    3. In production environment:
       - Test shortcuts ('x-viewer-id' and DEMO_USER_ID) are strictly disabled.
       - Mutations (POST/PATCH/PUT/DELETE) require Bearer auth (401 Unauthorized if missing).
       - Safe reads without token return None (anonymous viewer).
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        raw_token = auth_header[7:].strip()
        if raw_token:
            user = await auth_service.verify_session_token(raw_token)
            return str(user.id)

    if settings.ENVIRONMENT != "production":
        header_val = request.headers.get("x-viewer-id")
        if header_val:
            try:
                uuid.UUID(header_val)
                return header_val
            except ValueError:
                pass
        return settings.DEMO_USER_ID

    # Production environment protections
    if request.method in ("POST", "PATCH", "PUT", "DELETE"):
        raise UnauthorizedError(
            "Authentication required",
            details=[{"field": "Authorization", "reason": "missing_bearer_token"}],
        )

    return None


def get_request_id(request: Request) -> str:
    """
    Retrieves the active request ID from request.state or contextvar.
    """
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return get_current_request_id()
