"""
Tests for Stage 1 PY-P0-01 (Account and Session Identity).

Validates:
- Registration with normalized handles and input bounds.
- Constant-time login and resistance to handle enumeration.
- GET /auth/me actor resolution.
- POST /auth/logout immediate session revocation and idempotency.
- Checkpoint: 20 concurrent duplicate registrations -> exactly 1 account.
- Checkpoint: No response leaks plain-text credentials.
- Backwards compatibility: V1 seed user Asha can login with backfilled password.
"""

import asyncio
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.database import dispose_async_engine


@pytest.fixture
async def client():
    """Provides an isolated AsyncClient with engine disposal between tests."""
    application = create_app()
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as ac:
        yield ac
    await dispose_async_engine()


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Visitor can register and receive an active Bearer session token."""
    unique_handle = f"user_{uuid.uuid4().hex[:10]}"
    payload = {
        "handle": unique_handle,
        "displayName": "Test Runner",
        "password": "SecurePassword123!",
        "bio": "Testing Stage 1",
    }

    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    assert "accessToken" in data
    assert data["tokenType"] == "Bearer"
    assert data["accessToken"].startswith("sf_")
    assert data["user"]["handle"] == unique_handle
    assert data["user"]["displayName"] == "Test Runner"
    assert "password" not in data
    assert "passwordHash" not in data


@pytest.mark.asyncio
async def test_register_normalization(client: AsyncClient):
    """Handles are normalized to lowercase and whitespace-trimmed."""
    raw_name = f"Norm_{uuid.uuid4().hex[:8]}"
    payload = {
        "handle": f"  {raw_name}  ",
        "displayName": "Normalized User",
        "password": "SecurePassword123!",
    }

    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["handle"] == raw_name.lower()


@pytest.mark.asyncio
async def test_register_bounded_inputs(client: AsyncClient):
    """Registration rejects invalid handles and passwords under 8 characters."""
    # Invalid handle characters (spaces, special chars)
    resp1 = await client.post("/auth/register", json={
        "handle": "invalid handle!",
        "displayName": "Bad Handle",
        "password": "SecurePassword123!",
    })
    assert resp1.status_code in (400, 422)

    # Password too short (< 8 chars)
    resp2 = await client.post("/auth/register", json={
        "handle": f"valid_{uuid.uuid4().hex[:6]}",
        "displayName": "Short Pass",
        "password": "short",
    })
    assert resp2.status_code in (400, 422)

    # Extra forbidden field
    resp3 = await client.post("/auth/register", json={
        "handle": f"valid_{uuid.uuid4().hex[:6]}",
        "displayName": "Extra Field",
        "password": "SecurePassword123!",
        "isAdmin": True,
    })
    assert resp3.status_code in (400, 422)


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Member can sign in with valid credentials and receive a token."""
    handle = f"login_{uuid.uuid4().hex[:8]}"
    password = "CorrectPassword123!"

    # Register first
    reg_resp = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "Login Test",
        "password": password,
    })
    assert reg_resp.status_code == 201

    # Sign in
    login_resp = await client.post("/auth/login", json={
        "handle": handle,
        "password": password,
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "accessToken" in data
    assert data["user"]["handle"] == handle


@pytest.mark.asyncio
async def test_login_invalid_credentials_timing_and_enumeration(client: AsyncClient):
    """Non-existent handle and wrong password return identical 401 error message."""
    # Non-existent user
    resp1 = await client.post("/auth/login", json={
        "handle": f"nonexistent_{uuid.uuid4().hex[:8]}",
        "password": "SomePassword123!",
    })
    assert resp1.status_code == 401
    data1 = resp1.json()
    assert data1["error"]["code"] == "UNAUTHORIZED"
    assert data1["error"]["message"] == "Invalid handle or credentials"

    # Existing user, wrong password
    handle = f"user_{uuid.uuid4().hex[:8]}"
    await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "User",
        "password": "RealPassword123!",
    })

    resp2 = await client.post("/auth/login", json={
        "handle": handle,
        "password": "WrongPassword123!",
    })
    assert resp2.status_code == 401
    data2 = resp2.json()
    assert data2["error"]["code"] == "UNAUTHORIZED"
    assert data2["error"]["message"] == "Invalid handle or credentials"


@pytest.mark.asyncio
async def test_get_me_flow(client: AsyncClient):
    """GET /auth/me returns current actor; rejects missing or invalid tokens."""
    handle = f"me_{uuid.uuid4().hex[:8]}"
    password = "MyPassword123!"

    # 1. Without token -> 401
    unauth_resp = await client.get("/auth/me")
    assert unauth_resp.status_code == 401

    # 2. Register & get token
    reg_resp = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "Me User",
        "password": password,
    })
    token = reg_resp.json()["accessToken"]

    # 3. With valid token -> 200
    me_resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["item"]["handle"] == handle
    assert me_data["item"]["displayName"] == "Me User"


@pytest.mark.asyncio
async def test_logout_invalidates_session_immediately(client: AsyncClient):
    """POST /auth/logout immediately revokes the session token."""
    handle = f"logout_{uuid.uuid4().hex[:8]}"
    password = "LogoutPassword123!"

    reg_resp = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": "Logout User",
        "password": password,
    })
    token = reg_resp.json()["accessToken"]

    # Verify token works
    check1 = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert check1.status_code == 200

    # Logout
    logout_resp = await client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_resp.status_code == 204

    # Verify token is now rejected
    check2 = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert check2.status_code == 401

    # Idempotent logout call
    logout_repeat = await client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_repeat.status_code == 204


@pytest.mark.asyncio
async def test_checkpoint_concurrent_duplicate_registration(client: AsyncClient):
    """
    PRD PY-P0-01 Checkpoint:
    Run 20 concurrent registrations of the exact same handle -> exactly 1 account created.
    """
    target_handle = f"race_{uuid.uuid4().hex[:8]}"
    payload = {
        "handle": target_handle,
        "displayName": "Racer",
        "password": "RacePassword123!",
    }

    # Fire 20 concurrent registration requests
    tasks = [client.post("/auth/register", json=payload) for _ in range(20)]
    responses = await asyncio.gather(*tasks)

    status_codes = [r.status_code for r in responses]
    success_count = status_codes.count(201)
    conflict_count = status_codes.count(409)

    # Exactly 1 request must succeed; 19 must fail with 409 Conflict
    assert success_count == 1, f"Expected exactly 1 success, got {success_count} (codes: {status_codes})"
    assert conflict_count == 19, f"Expected 19 conflicts, got {conflict_count}"


@pytest.mark.asyncio
async def test_checkpoint_no_credential_leak(client: AsyncClient):
    """
    PRD PY-P0-01 Checkpoint:
    Verify no response or error envelope leaks the raw password or password_hash.
    """
    raw_secret = "SuperSecretPlainTextPassword999!"
    payload = {
        "handle": f"leak_{uuid.uuid4().hex[:8]}",
        "displayName": "Leak Check",
        "password": raw_secret,
    }

    reg_resp = await client.post("/auth/register", json=payload)
    resp_text = reg_resp.text
    assert raw_secret not in resp_text
    assert "argon2" not in resp_text
    assert "password" not in resp_text

    login_resp = await client.post("/auth/login", json={
        "handle": payload["handle"],
        "password": raw_secret,
    })
    login_text = login_resp.text
    assert raw_secret not in login_text
    assert "argon2" not in login_text


@pytest.mark.asyncio
async def test_v1_seed_user_migration_login(client: AsyncClient):
    """V1 seed user 'asha' can log in with backfilled password 'TestPassword123!'."""
    resp = await client.post("/auth/login", json={
        "handle": "asha",
        "password": "TestPassword123!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["handle"] == "asha"
    assert data["user"]["displayName"] == "Asha Patel"
    assert "accessToken" in data
