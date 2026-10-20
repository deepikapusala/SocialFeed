"""
Tests for Stage 2 PY-P0-02 (Owned Profile and Account State).

Validates:
- Member can update only their own allowed fields (display_name, bio, avatars).
- Immutable/unknown fields are rejected (extra="forbid").
- Checkpoint: User B cannot PATCH User A (403 Forbidden) and DB state remains byte-identical.
- Account deactivation revokes all sessions, blocks login, and hides profile.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.main import create_app
from app.database import dispose_async_engine, get_async_engine
from app.models import User


@pytest.fixture
async def client():
    """Provides an isolated AsyncClient with engine disposal between tests."""
    application = create_app()
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as ac:
        yield ac
    await dispose_async_engine()


@pytest.mark.asyncio
async def test_update_own_profile_success(client: AsyncClient):
    """Owner can update their own display_name, bio, and avatar URLs via PATCH /users/me."""
    handle = f"prof_{uuid.uuid4().hex[:8]}"
    reg = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "Initial Name",
        "password": "Password123!",
        "bio": "Initial bio",
    })
    assert reg.status_code == 201
    token = reg.json()["accessToken"]

    # Update profile
    patch_resp = await client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "displayName": "Updated Gorgeous Name",
            "bio": "Updated landscape bio 🏔️",
            "avatarSmallUrl": "https://example.com/avatar_sm.jpg",
            "avatarLargeUrl": "https://example.com/avatar_lg.jpg",
        },
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()["item"]
    assert data["displayName"] == "Updated Gorgeous Name"
    assert data["bio"] == "Updated landscape bio 🏔️"
    assert data["avatar"]["smallUrl"] == "https://example.com/avatar_sm.jpg"
    assert data["avatar"]["largeUrl"] == "https://example.com/avatar_lg.jpg"
    assert data["handle"] == handle  # handle remains intact


@pytest.mark.asyncio
async def test_checkpoint_cross_user_patch_forbidden_and_db_byte_identical(client: AsyncClient):
    """
    PRD PY-P0-02 Checkpoint:
    User B attempts to PATCH User A's profile.
    Must receive 403 Forbidden, and User A's database state must remain 100% byte-identical.
    """
    # 1. Register User A
    handle_a = f"usera_{uuid.uuid4().hex[:8]}"
    reg_a = await client.post("/auth/register", json={
        "handle": handle_a,
        "displayName": "Untouched Name A",
        "password": "Password123!",
        "bio": "Original Pristine Bio A",
    })
    assert reg_a.status_code == 201
    user_a_id = reg_a.json()["user"]["id"]

    # 2. Register User B
    handle_b = f"userb_{uuid.uuid4().hex[:8]}"
    reg_b = await client.post("/auth/register", json={
        "handle": handle_b,
        "displayName": "Attacker B",
        "password": "Password123!",
    })
    assert reg_b.status_code == 201
    token_b = reg_b.json()["accessToken"]

    # 3. Read User A's state before attack
    engine = get_async_engine()
    async with engine.connect() as conn:
        row_before = (
            await conn.execute(select(User).where(User.id == uuid.UUID(user_a_id)))
        ).first()
    assert row_before is not None

    # 4. User B attempts to maliciously update User A
    hack_resp = await client.patch(
        f"/users/{user_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "displayName": "Hacked Display Name!",
            "bio": "Hacked Bio!",
        },
    )
    assert hack_resp.status_code == 403
    hack_data = hack_resp.json()
    assert hack_data["error"]["code"] == "FORBIDDEN"

    # 5. Read User A's state after attack and verify byte-identical match
    async with engine.connect() as conn:
        row_after = (
            await conn.execute(select(User).where(User.id == uuid.UUID(user_a_id)))
        ).first()

    assert row_after is not None
    assert row_before == row_after
    assert row_after.display_name == "Untouched Name A"
    assert row_after.bio == "Original Pristine Bio A"


@pytest.mark.asyncio
async def test_update_profile_rejects_immutable_and_unknown_fields(client: AsyncClient):
    """
    PRD PY-P0-02:
    Immutable IDs, counts, timestamps, ownership, relationship state, and unknown fields
    are strictly rejected with 422/400.
    """
    handle = f"immut_{uuid.uuid4().hex[:8]}"
    reg = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "Normal User",
        "password": "Password123!",
    })
    token = reg.json()["accessToken"]

    # Attempt to change immutable handle
    resp1 = await client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"handle": "new_handle"},
    )
    assert resp1.status_code in (400, 422)

    # Attempt to change immutable ID
    resp2 = await client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"id": str(uuid.uuid4())},
    )
    assert resp2.status_code in (400, 422)

    # Attempt to manipulate follower count
    resp3 = await client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"followerCount": 1000000},
    )
    assert resp3.status_code in (400, 422)

    # Attempt to pass unknown field
    resp4 = await client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"isAdmin": True},
    )
    assert resp4.status_code in (400, 422)


@pytest.mark.asyncio
async def test_deactivate_own_account_flow(client: AsyncClient):
    """
    PRD PY-P0-02:
    Deactivating account sets is_active=False, revokes sessions, blocks login,
    and removes profile from public resolution.
    """
    handle = f"deact_{uuid.uuid4().hex[:8]}"
    password = "DeactPassword123!"

    reg = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "Leaving User",
        "password": password,
    })
    token = reg.json()["accessToken"]
    user_id = reg.json()["user"]["id"]

    # 1. Deactivate account
    deact_resp = await client.post(
        "/users/me/deactivate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deact_resp.status_code == 204

    # 2. Existing session token is immediately invalid (401)
    me_resp = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 401

    # 3. Login attempt with deactivated credentials fails (401)
    login_resp = await client.post("/auth/login", json={
        "handle": handle,
        "password": password,
    })
    assert login_resp.status_code == 401

    # 4. Direct profile lookup returns 404 (hidden)
    profile_resp = await client.get(f"/users/{user_id}")
    assert profile_resp.status_code == 404
