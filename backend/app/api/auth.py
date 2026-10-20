"""
Authentication Router (Stage 1 PY-P0-01).

Implements:
- POST /auth/register: Create new account + return Bearer session token.
- POST /auth/login: Verify credentials + return Bearer session token.
- POST /auth/logout: Revoke active session token.
- GET /auth/me: Return current authenticated user profile.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import (
    get_async_session,
    get_auth_service,
    get_required_actor,
)
from app.common.errors import UnauthorizedError
from app.models import User
from app.schemas.auth import (
    AuthTokenResponse,
    CurrentUserResponse,
    LoginRequest,
    RegisterRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new member account",
)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthTokenResponse:
    """
    Registers a new member account with unique normalized handle, display name,
    and hashed password. Returns an active Bearer session token upon success.
    """
    return await service.register(payload)


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in to an existing account",
)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthTokenResponse:
    """
    Validates user credentials and issues an active Bearer session token.
    Resists account enumeration with timing mitigation.
    """
    return await service.login(payload)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate current session token",
)
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None),
    service: AuthService = Depends(get_auth_service),
) -> None:
    """
    Revokes the caller's active session token immediately. Idempotent.
    """
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization[7:].strip()
        await service.logout(raw_token)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current authenticated actor profile",
)
async def get_me(
    current_user: User = Depends(get_required_actor),
    service: AuthService = Depends(get_auth_service),
) -> CurrentUserResponse:
    """
    Returns the profile and stats of the currently authenticated actor.
    """
    profile = await service.get_me(str(current_user.id))
    return CurrentUserResponse(item=profile)
