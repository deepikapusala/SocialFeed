"""
Tests for Stage 3 PY-P0-03 (Follow Graph and Privacy).

Validates:
- Follow/unfollow are desired-state and idempotent under repetition.
- Self-follow is physically blocked at DB engine level (check constraint) and API level.
- Public follow activates immediately ('accepted').
- Private follow enters 'pending' state.
- Target user can accept ('accepted') or reject (deleted) pending requests.
- Requester can cancel pending requests via DELETE /follow.
- Unauthorized transitions (third-party acceptance/rejection) are rejected.
- Private account visibility gates: followers, following, media blocked (403) for non-followers.
- Checkpoint: 50 concurrent follow requests for the same pair yield exactly 1 DB row.
"""

import asyncio
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import func, select
from app.main import create_app
from app.database import dispose_async_engine, get_async_engine
from app.models import Follow, User


@pytest.fixture
async def client():
    """Provides an isolated AsyncClient with engine disposal between tests."""
    application = create_app()
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as ac:
        yield ac
    await dispose_async_engine()


async def register_user(client: AsyncClient, prefix: str, is_private: bool = False):
    """Helper to register and optionally privatize a test user."""
    handle = f"{prefix}_{uuid.uuid4().hex[:8]}"
    resp = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": f"{prefix.capitalize()} User",
        "password": "Password123!",
    })
    assert resp.status_code == 201
    data = resp.json()
    user_id = data["user"]["id"]
    token = data["accessToken"]

    if is_private:
        patch_resp = await client.patch(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"isPrivate": True},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["item"]["isPrivate"] is True

    return {"id": user_id, "token": token, "handle": handle}


@pytest.mark.asyncio
async def test_follow_public_user_and_idempotency(client: AsyncClient):
    """Public user follow activates immediately ('accepted') and is fully idempotent."""
    user_a = await register_user(client, "fol_a")
    user_b = await register_user(client, "fol_b")

    # First follow call
    resp1 = await client.put(
        f"/users/{user_b['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["relationshipStatus"] == "accepted"
    assert d1["followedByViewer"] is True
    assert d1["followerCount"] == 1

    # Idempotent second and third calls
    resp2 = await client.put(
        f"/users/{user_b['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["relationshipStatus"] == "accepted"
    assert resp2.json()["followerCount"] == 1

    resp3 = await client.put(
        f"/users/{user_b['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp3.status_code == 200
    assert resp3.json()["followerCount"] == 1

    # Verify target's profile
    prof = await client.get(
        f"/users/{user_b['id']}",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert prof.status_code == 200
    item = prof.json()["item"]
    assert item["followerCount"] == 1
    assert item["followedByViewer"] is True
    assert item["relationshipStatus"] == "accepted"


@pytest.mark.asyncio
async def test_unfollow_public_user_and_idempotency(client: AsyncClient):
    """Unfollow resets relationship to 'none' and is fully idempotent."""
    user_a = await register_user(client, "unf_a")
    user_b = await register_user(client, "unf_b")

    # Establish initial follow
    await client.put(
        f"/users/{user_b['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )

    # First unfollow
    resp1 = await client.delete(
        f"/users/{user_b['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["relationshipStatus"] == "none"
    assert d1["followedByViewer"] is False
    assert d1["followerCount"] == 0

    # Idempotent second unfollow
    resp2 = await client.delete(
        f"/users/{user_b['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["relationshipStatus"] == "none"
    assert resp2.json()["followerCount"] == 0


@pytest.mark.asyncio
async def test_self_follow_prohibited(client: AsyncClient):
    """Self-follow is rejected at API level and blocked by database check constraint."""
    user_a = await register_user(client, "self_a")

    resp = await client.put(
        f"/users/{user_a['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    # Verify physical DB engine constraint (ck_follows_no_self_follow)
    engine = get_async_engine()
    from sqlalchemy.exc import IntegrityError
    async with engine.connect() as conn:
        try:
            with pytest.raises(IntegrityError):
                await conn.execute(
                    Follow.__table__.insert().values(
                        follower_id=uuid.UUID(user_a["id"]),
                        following_id=uuid.UUID(user_a["id"]),
                        status="accepted",
                    )
                )
        finally:
            await conn.rollback()


@pytest.mark.asyncio
async def test_private_account_request_and_acceptance_lifecycle(client: AsyncClient):
    """Private account follow enters 'pending', target approves to transition to 'accepted'."""
    user_a = await register_user(client, "req_a")
    user_c = await register_user(client, "priv_c", is_private=True)

    # Requester A follows private target C -> pending
    resp = await client.put(
        f"/users/{user_c['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp.status_code == 200
    d = resp.json()
    assert d["relationshipStatus"] == "pending"
    assert d["followedByViewer"] is False
    assert d["followerCount"] == 0

    # Repeat follow while pending -> still pending (idempotent)
    resp_repeat = await client.put(
        f"/users/{user_c['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert resp_repeat.status_code == 200
    assert resp_repeat.json()["relationshipStatus"] == "pending"

    # Profile viewed by requester shows pending and 0 followerCount
    prof_before = await client.get(
        f"/users/{user_c['id']}",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert prof_before.json()["item"]["relationshipStatus"] == "pending"
    assert prof_before.json()["item"]["followerCount"] == 0

    # Target C accepts the request
    accept_resp = await client.post(
        f"/users/requests/{user_a['id']}/accept",
        headers={"Authorization": f"Bearer {user_c['token']}"},
    )
    assert accept_resp.status_code == 200
    acc_d = accept_resp.json()
    assert acc_d["accepted"] is True
    assert acc_d["followerCount"] == 1

    # Profile viewed by requester now shows accepted and 1 followerCount
    prof_after = await client.get(
        f"/users/{user_c['id']}",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert prof_after.json()["item"]["relationshipStatus"] == "accepted"
    assert prof_after.json()["item"]["followedByViewer"] is True
    assert prof_after.json()["item"]["followerCount"] == 1


@pytest.mark.asyncio
async def test_private_account_request_rejection(client: AsyncClient):
    """Target rejects a pending follow request, removing the pending relationship."""
    user_a = await register_user(client, "rej_a")
    user_c = await register_user(client, "priv_rej", is_private=True)

    # A requests C
    await client.put(
        f"/users/{user_c['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )

    # Target C rejects request
    rej_resp = await client.post(
        f"/users/requests/{user_a['id']}/reject",
        headers={"Authorization": f"Bearer {user_c['token']}"},
    )
    assert rej_resp.status_code == 204

    # Profile viewed by requester shows none
    prof = await client.get(
        f"/users/{user_c['id']}",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert prof.json()["item"]["relationshipStatus"] == "none"
    assert prof.json()["item"]["followerCount"] == 0


@pytest.mark.asyncio
async def test_private_account_request_cancel_by_requester(client: AsyncClient):
    """Requester can cancel a pending follow request via DELETE /follow."""
    user_a = await register_user(client, "canc_a")
    user_c = await register_user(client, "priv_canc", is_private=True)

    # A requests C
    await client.put(
        f"/users/{user_c['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )

    # Requester A cancels via DELETE
    canc_resp = await client.delete(
        f"/users/{user_c['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert canc_resp.status_code == 200
    assert canc_resp.json()["relationshipStatus"] == "none"


@pytest.mark.asyncio
async def test_unauthorized_request_transition_rejected(client: AsyncClient):
    """Unrelated third party cannot accept or reject someone else's follow request."""
    user_a = await register_user(client, "unauth_a")
    user_c = await register_user(client, "priv_target", is_private=True)
    user_d = await register_user(client, "unauth_d")

    # A requests C
    await client.put(
        f"/users/{user_c['id']}/follow",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )

    # Unrelated User D attempts to accept User A's request for C -> 404
    bad_accept = await client.post(
        f"/users/requests/{user_a['id']}/accept",
        headers={"Authorization": f"Bearer {user_d['token']}"},
    )
    assert bad_accept.status_code == 404

    # Unrelated User D attempts to reject User A's request for C -> 404
    bad_reject = await client.post(
        f"/users/requests/{user_a['id']}/reject",
        headers={"Authorization": f"Bearer {user_d['token']}"},
    )
    assert bad_reject.status_code == 404

    # User A's request for User C is intact as 'pending'
    prof = await client.get(
        f"/users/{user_c['id']}",
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    assert prof.json()["item"]["relationshipStatus"] == "pending"


@pytest.mark.asyncio
async def test_privacy_gates_followers_following_and_media(client: AsyncClient):
    """
    Non-followers receive 403 Forbidden when requesting followers, following, or media
    of a private account. Accepted followers and account owner receive 200 OK.
    """
    owner = await register_user(client, "gate_own", is_private=True)
    friend = await register_user(client, "gate_frnd")
    stranger = await register_user(client, "gate_strg")

    # Friend requests and owner accepts
    await client.put(
        f"/users/{owner['id']}/follow",
        headers={"Authorization": f"Bearer {friend['token']}"},
    )
    await client.post(
        f"/users/requests/{friend['id']}/accept",
        headers={"Authorization": f"Bearer {owner['token']}"},
    )

    # Stranger (non-follower) blocked with 403
    f_resp = await client.get(
        f"/users/{owner['id']}/followers",
        headers={"Authorization": f"Bearer {stranger['token']}"},
    )
    assert f_resp.status_code == 403
    assert f_resp.json()["error"]["code"] == "FORBIDDEN"

    fg_resp = await client.get(
        f"/users/{owner['id']}/following",
        headers={"Authorization": f"Bearer {stranger['token']}"},
    )
    assert fg_resp.status_code == 403

    m_resp = await client.get(
        f"/users/{owner['id']}/media",
        headers={"Authorization": f"Bearer {stranger['token']}"},
    )
    assert m_resp.status_code == 403

    # Friend (accepted follower) allowed with 200
    friend_f = await client.get(
        f"/users/{owner['id']}/followers",
        headers={"Authorization": f"Bearer {friend['token']}"},
    )
    assert friend_f.status_code == 200
    assert len(friend_f.json()["items"]) == 1
    assert friend_f.json()["items"][0]["id"] == friend["id"]

    friend_fg = await client.get(
        f"/users/{owner['id']}/following",
        headers={"Authorization": f"Bearer {friend['token']}"},
    )
    assert friend_fg.status_code == 200

    # Owner allowed with 200
    owner_f = await client.get(
        f"/users/{owner['id']}/followers",
        headers={"Authorization": f"Bearer {owner['token']}"},
    )
    assert owner_f.status_code == 200


@pytest.mark.asyncio
async def test_checkpoint_50_concurrent_follows(client: AsyncClient):
    """
    Stage 3 Checkpoint:
    Fire 50 concurrent follow requests for the same pair -> exactly 1 active DB row.
    """
    user_a = await register_user(client, "burst_a")
    user_b = await register_user(client, "burst_b")

    headers = {"Authorization": f"Bearer {user_a['token']}"}
    target_url = f"/users/{user_b['id']}/follow"

    async def single_follow():
        return await client.put(target_url, headers=headers)

    # Launch 50 concurrent follow requests
    tasks = [single_follow() for _ in range(50)]
    responses = await asyncio.gather(*tasks)

    # Every response succeeded
    for r in responses:
        assert r.status_code == 200
        assert r.json()["relationshipStatus"] == "accepted"

    # Query database directly: verify exactly 1 row exists
    engine = get_async_engine()
    async with engine.connect() as conn:
        stmt = select(func.count(Follow.follower_id)).where(
            Follow.follower_id == uuid.UUID(user_a["id"]),
            Follow.following_id == uuid.UUID(user_b["id"]),
        )
        res = await conn.execute(stmt)
        count = res.scalar()
        assert count == 1, f"Expected exactly 1 follow row, found {count}"
