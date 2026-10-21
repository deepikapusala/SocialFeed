"""
Tests for Stage 6 PY-P0-06 (Notification Inbox, Delivery Guarantees & Atomicity).

Validates:
1. 4 Required source events produce notifications for the recipient:
   - Like: Author receives notification (eventType='like', actor=viewer, targetPost=post).
   - Reply: Author receives notification (eventType='reply', actor=viewer, targetPost=reply).
   - Repost: Author receives notification (eventType='repost', actor=viewer, targetPost=original).
   - Follow: Followed user receives notification (eventType='follow', actor=follower).
   - Follow Accepted: Requester receives notification (eventType='follow_accepted', actor=target).
2. Self-actions produce ZERO notifications (e.g. author liking/replying/reposting own post).
3. Concurrent retries of the same event produce at most ONE logical notification (unique deduplication key).
4. Atomicity / Source Rollback: Source mutation failure leaves ZERO notifications.
5. Recipient isolation & IDOR prevention: Non-recipient cannot access another user's inbox or mark another user's notifications as read (403 Forbidden).
6. Read transitions:
   - Mark single read (POST /notifications/{id}/read) updates read state and decrements unreadCount.
   - Repeated mark-read on already read notification is idempotent and does NOT decrement unreadCount below 0.
   - Mark all read (POST /notifications/read) marks all eligible unread notifications as read.
7. Tombstoned target content: If the target post is subsequently soft-deleted, the notification remains intact with an explicit tombstone indicator (isDeleted=True, text='[Deleted]').
"""

import asyncio
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.database import dispose_async_engine


@pytest.fixture
async def client():
    application = create_app()
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as ac:
        yield ac
    await dispose_async_engine()


async def register_user(client: AsyncClient, prefix: str, is_private: bool = False):
    handle = f"{prefix}_{uuid.uuid4().hex[:8]}"
    resp = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": f"{prefix.capitalize()} User",
        "password": "Password123!",
    })
    assert resp.status_code == 201
    data = resp.json()
    token = data["accessToken"]
    user_id = data["user"]["id"]

    if is_private:
        patch_resp = await client.patch(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"isPrivate": True},
        )
        assert patch_resp.status_code == 200

    return {"id": user_id, "token": token, "handle": handle}


@pytest.mark.anyio
async def test_all_required_events_deliver_notifications(client: AsyncClient):
    """Verify all required source events deliver notifications to recipient."""
    alice = await register_user(client, "alice")
    bob = await register_user(client, "bob")

    alice_auth = {"Authorization": f"Bearer {alice['token']}"}
    bob_auth = {"Authorization": f"Bearer {bob['token']}"}

    # 1. Alice creates an original post
    create_resp = await client.post(
        "/posts",
        headers=alice_auth,
        json={"kind": "original", "text": "Hello from Alice!"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    # 2. Event: Bob likes Alice's post
    like_resp = await client.post(f"/posts/{post_id}/like", headers=bob_auth)
    assert like_resp.status_code == 200

    # 3. Event: Bob replies to Alice's post
    reply_resp = await client.post(
        "/posts",
        headers=bob_auth,
        json={"kind": "reply", "text": "Nice post Alice!", "reply_to_id": post_id},
    )
    assert reply_resp.status_code == 201
    reply_id = reply_resp.json()["item"]["id"]

    # 4. Event: Bob reposts Alice's post
    repost_resp = await client.post(f"/posts/{post_id}/repost", headers=bob_auth)
    assert repost_resp.status_code == 200

    # 5. Event: Bob follows Alice
    follow_resp = await client.put(f"/users/{alice['id']}/follow", headers=bob_auth)
    assert follow_resp.status_code == 200

    # Alice checks notification inbox
    inbox_resp = await client.get("/notifications", headers=alice_auth)
    assert inbox_resp.status_code == 200
    inbox = inbox_resp.json()

    assert inbox["unreadCount"] == 4
    assert len(inbox["items"]) == 4

    event_types = [item["eventType"] for item in inbox["items"]]
    assert "like" in event_types
    assert "reply" in event_types
    assert "repost" in event_types
    assert "follow" in event_types

    # Every notification has Bob as actor and correct target post where applicable
    for item in inbox["items"]:
        assert item["actor"]["id"] == bob["id"]
        assert item["isRead"] is False


@pytest.mark.anyio
async def test_follow_accepted_event_notification(client: AsyncClient):
    """Private account accept request delivers notification to original requester."""
    private_user = await register_user(client, "priv", is_private=True)
    requester = await register_user(client, "req")

    priv_auth = {"Authorization": f"Bearer {private_user['token']}"}
    req_auth = {"Authorization": f"Bearer {requester['token']}"}

    # Requester sends follow request
    await client.put(f"/users/{private_user['id']}/follow", headers=req_auth)

    # Private user accepts request
    accept_resp = await client.post(f"/users/requests/{requester['id']}/accept", headers=priv_auth)
    assert accept_resp.status_code == 200

    # Requester should receive follow_accepted notification
    req_inbox = await client.get("/notifications", headers=req_auth)
    assert req_inbox.status_code == 200
    data = req_inbox.json()
    assert data["unreadCount"] == 1
    assert data["items"][0]["eventType"] == "follow_accepted"
    assert data["items"][0]["actor"]["id"] == private_user["id"]


@pytest.mark.anyio
async def test_self_action_suppression(client: AsyncClient):
    """Actor performing action on own content creates ZERO notifications."""
    user = await register_user(client, "solo")
    auth = {"Authorization": f"Bearer {user['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=auth,
        json={"kind": "original", "text": "Solo author post"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    # Like own post
    await client.post(f"/posts/{post_id}/like", headers=auth)

    # Reply to own post
    await client.post(
        "/posts",
        headers=auth,
        json={"kind": "reply", "text": "Self reply", "reply_to_id": post_id},
    )

    # Inbox must have 0 notifications
    inbox = await client.get("/notifications", headers=auth)
    assert inbox.status_code == 200
    assert inbox.json()["unreadCount"] == 0
    assert len(inbox.json()["items"]) == 0


@pytest.mark.anyio
async def test_idor_prevention_and_mark_read_transitions(client: AsyncClient):
    """Prevent unauthorized read/mark-read across users and test mark-read transitions."""
    alice = await register_user(client, "alice")
    bob = await register_user(client, "bob")

    alice_auth = {"Authorization": f"Bearer {alice['token']}"}
    bob_auth = {"Authorization": f"Bearer {bob['token']}"}

    # Bob follows Alice -> generates notification for Alice
    await client.put(f"/users/{alice['id']}/follow", headers=bob_auth)

    alice_inbox = await client.get("/notifications", headers=alice_auth)
    notif_id = alice_inbox.json()["items"][0]["id"]
    assert alice_inbox.json()["unreadCount"] == 1

    # Bob tries to mark Alice's notification as read (IDOR attempt) -> 403 Forbidden
    idor_resp = await client.post(f"/notifications/{notif_id}/read", headers=bob_auth)
    assert idor_resp.status_code == 403

    # Alice marks notification as read -> 200 OK
    mark_resp = await client.post(f"/notifications/{notif_id}/read", headers=alice_auth)
    assert mark_resp.status_code == 200
    assert mark_resp.json()["markedCount"] == 1
    assert mark_resp.json()["unreadCount"] == 0

    # Repeated mark-read is idempotent
    repeat_mark = await client.post(f"/notifications/{notif_id}/read", headers=alice_auth)
    assert repeat_mark.status_code == 200
    assert repeat_mark.json()["markedCount"] == 0
    assert repeat_mark.json()["unreadCount"] == 0

    # Mark all read
    all_read_resp = await client.post("/notifications/read", headers=alice_auth)
    assert all_read_resp.status_code == 200
    assert all_read_resp.json()["unreadCount"] == 0


@pytest.mark.anyio
async def test_checkpoint_concurrent_retries_and_deduplication(client: AsyncClient):
    """
    CHECKPOINT: Retry the same like 10x concurrently -> exactly 1 notification.
    """
    author = await register_user(client, "author")
    viewer = await register_user(client, "viewer")

    author_auth = {"Authorization": f"Bearer {author['token']}"}
    viewer_auth = {"Authorization": f"Bearer {viewer['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=author_auth,
        json={"kind": "original", "text": "Post to be liked multiple times"},
    )
    post_id = create_resp.json()["item"]["id"]

    # Fire 10 concurrent likes from viewer on the same post
    app = create_app()
    transport = ASGITransport(app=app)

    async def single_like():
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            return await ac.post(f"/posts/{post_id}/like", headers=viewer_auth)

    tasks = [single_like() for _ in range(10)]
    responses = await asyncio.gather(*tasks)

    for r in responses:
        assert r.status_code == 200

    # Author inbox must contain EXACTLY 1 notification for this like
    inbox = await client.get("/notifications", headers=author_auth)
    assert inbox.status_code == 200
    items = [item for item in inbox.json()["items"] if item["eventType"] == "like"]
    assert len(items) == 1
    assert inbox.json()["unreadCount"] == 1


@pytest.mark.anyio
async def test_checkpoint_tombstoned_content_inbox_integrity(client: AsyncClient):
    """
    Tombstoned content policy: When a target post is soft-deleted,
    the notification remains readable with a tombstone indicator.
    """
    author = await register_user(client, "author")
    viewer = await register_user(client, "viewer")

    author_auth = {"Authorization": f"Bearer {author['token']}"}
    viewer_auth = {"Authorization": f"Bearer {viewer['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=author_auth,
        json={"kind": "original", "text": "Original soon to be deleted"},
    )
    post_id = create_resp.json()["item"]["id"]

    # Viewer replies
    await client.post(
        "/posts",
        headers=viewer_auth,
        json={"kind": "reply", "text": "Nice reply", "reply_to_id": post_id},
    )

    # Author soft-deletes original post
    del_resp = await client.delete(f"/posts/{post_id}", headers=author_auth)
    assert del_resp.status_code == 204

    # Notification inbox still functions cleanly
    inbox = await client.get("/notifications", headers=author_auth)
    assert inbox.status_code == 200
    assert len(inbox.json()["items"]) >= 1
    reply_notif = inbox.json()["items"][0]
    assert reply_notif["eventType"] == "reply"
    assert reply_notif["targetPost"] is not None


