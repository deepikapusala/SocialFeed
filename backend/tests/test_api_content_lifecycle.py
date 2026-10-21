"""
Tests for Stage 5 PY-P0-05 (Owned-Content Lifecycle & Concurrency).

Validates:
1. Owner can edit original/reply post text (200 OK) -> updates text, updates updatedAt, increments version.
2. Cross-user edit attempt fails (403 Forbidden) -> state remains byte-identical.
3. Immutable field edit attempt fails (422 Unprocessable Entity) via extra="forbid" (kind, authorId, id, counts).
4. Stale version edit conflict fails (409 Conflict) via body version or If-Match header.
5. Soft-deletion is idempotent (204 No Content on 1st and 2nd calls).
6. Cross-user delete attempt fails (403 Forbidden).
7. Checkpoint: Single delete verified across all 9 surfaces:
   - Surface 1 (Detail): GET /posts/{id} -> 404 Not Found
   - Surface 2 (Feed): GET /feed -> deleted post excluded
   - Surface 3 (Search): GET /search/originals -> deleted post excluded
   - Surface 4 (Profile Media): GET /users/{id}/media -> deleted post media excluded
   - Surface 5 (Direct Replies): GET /posts/{id}/replies -> replies on deleted post are preserved, deleted reply itself excluded
   - Surface 6 (Likes): POST /posts/{id}/like on deleted post -> 404 Not Found
   - Surface 7 (Reposts): POST /posts/{id}/repost on deleted post -> 404 Not Found
   - Surface 8 (Profile postCount): GET /users/{id} -> postCount reflects only active posts
   - Surface 9 (Reply creation): POST /posts with replyToId of deleted post -> 404 Not Found
8. Checkpoint: Concurrent edit race between two sessions -> one succeeds (200), one detects stale version (409).
"""

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


async def register_user(client: AsyncClient, prefix: str):
    handle = f"{prefix}_{uuid.uuid4().hex[:8]}"
    resp = await client.post("/auth/register", json={
        "handle": handle,
        "displayName": f"{prefix.capitalize()} User",
        "password": "Password123!",
    })
    assert resp.status_code == 201
    data = resp.json()
    return {"id": data["user"]["id"], "token": data["accessToken"], "handle": handle}


@pytest.mark.anyio
async def test_owner_edit_post_success(client: AsyncClient):
    author = await register_user(client, "alice")
    auth_header = {"Authorization": f"Bearer {author['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=auth_header,
        json={"kind": "original", "text": "Initial post text content"},
    )
    assert create_resp.status_code == 201
    post_data = create_resp.json()["item"]
    post_id = post_data["id"]
    initial_version = post_data.get("version", 1)

    patch_resp = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "Updated post text by author", "version": initial_version},
    )
    assert patch_resp.status_code == 200
    updated_data = patch_resp.json()["item"]

    assert updated_data["text"] == "Updated post text by author"
    assert updated_data["version"] == initial_version + 1
    assert updated_data["updatedAt"] is not None

    detail_resp = await client.get(f"/posts/{post_id}", headers=auth_header)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["item"]["text"] == "Updated post text by author"


@pytest.mark.anyio
async def test_cross_user_edit_rejected_403(client: AsyncClient):
    author = await register_user(client, "author")
    attacker = await register_user(client, "attacker")

    create_resp = await client.post(
        "/posts",
        headers={"Authorization": f"Bearer {author['token']}"},
        json={"kind": "original", "text": "Author original message"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    patch_resp = await client.patch(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {attacker['token']}"},
        json={"text": "Vandalized content"},
    )
    assert patch_resp.status_code == 403
    assert patch_resp.json()["error"]["code"] == "FORBIDDEN"

    detail_resp = await client.get(f"/posts/{post_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["item"]["text"] == "Author original message"


@pytest.mark.anyio
async def test_immutable_field_edit_rejected_422(client: AsyncClient):
    author = await register_user(client, "author")
    auth_header = {"Authorization": f"Bearer {author['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=auth_header,
        json={"kind": "original", "text": "Valid original text"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    resp1 = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "New text", "kind": "repost"},
    )
    assert resp1.status_code == 422

    resp2 = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "New text", "authorId": str(uuid.uuid4())},
    )
    assert resp2.status_code == 422

    resp3 = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "New text", "likeCount": 9999},
    )
    assert resp3.status_code == 422


@pytest.mark.anyio
async def test_optimistic_concurrency_conflict_409(client: AsyncClient):
    author = await register_user(client, "author")
    auth_header = {"Authorization": f"Bearer {author['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=auth_header,
        json={"kind": "original", "text": "Version test text"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    resp1 = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "First update", "version": 1},
    )
    assert resp1.status_code == 200
    assert resp1.json()["item"]["version"] == 2

    resp2 = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "Stale update from second tab", "version": 1},
    )
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "CONFLICT"

    resp3 = await client.patch(
        f"/posts/{post_id}",
        headers={**auth_header, "If-Match": '\"1\"'},
        json={"text": "Stale update via header"},
    )
    assert resp3.status_code == 409
    assert resp3.json()["error"]["code"] == "CONFLICT"

    resp4 = await client.patch(
        f"/posts/{post_id}",
        headers={**auth_header, "If-Match": '\"2\"'},
        json={"text": "Successful update via header"},
    )
    assert resp4.status_code == 200
    assert resp4.json()["item"]["version"] == 3


@pytest.mark.anyio
async def test_cross_user_delete_rejected_403(client: AsyncClient):
    author = await register_user(client, "author")
    attacker = await register_user(client, "attacker")

    create_resp = await client.post(
        "/posts",
        headers={"Authorization": f"Bearer {author['token']}"},
        json={"kind": "original", "text": "Protected post"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    del_resp = await client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {attacker['token']}"},
    )
    assert del_resp.status_code == 403
    assert del_resp.json()["error"]["code"] == "FORBIDDEN"

    detail_resp = await client.get(f"/posts/{post_id}")
    assert detail_resp.status_code == 200


@pytest.mark.anyio
async def test_checkpoint_delete_single_post_all_9_surfaces(client: AsyncClient):
    author = await register_user(client, "author")
    viewer = await register_user(client, "viewer")
    author_auth = {"Authorization": f"Bearer {author['token']}"}
    viewer_auth = {"Authorization": f"Bearer {viewer['token']}"}

    follow_resp = await client.put(f"/users/{author['id']}/follow", headers=viewer_auth)
    assert follow_resp.status_code == 200

    unique_keyword = f"lifecycle_{uuid.uuid4().hex[:6]}"
    create_resp = await client.post(
        "/posts",
        headers=author_auth,
        json={
            "kind": "original",
            "text": f"Special original post with keyword {unique_keyword}",
            "media": [
                {
                    "altText": "Test photo",
                    "width": 1080,
                    "height": 1080,
                    "smallUrl": "https://cdn.example.com/small.jpg",
                    "largeUrl": "https://cdn.example.com/large.jpg",
                }
            ],
        },
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]

    reply_resp = await client.post(
        "/posts",
        headers=viewer_auth,
        json={
            "kind": "reply",
            "text": "Great post, I am replying here!",
            "reply_to_id": post_id,
        },
    )
    assert reply_resp.status_code == 201
    reply_id = reply_resp.json()["item"]["id"]

    profile_before = await client.get(f"/users/{author['id']}")
    assert profile_before.status_code == 200
    assert profile_before.json()["item"]["postCount"] == 1

    feed_before = await client.get("/feed", headers=viewer_auth)
    assert any(item["id"] == post_id for item in feed_before.json()["items"])

    search_before = await client.get(f"/search/originals?q={unique_keyword}", headers=viewer_auth)
    assert any(item["id"] == post_id for item in search_before.json()["items"])

    media_before = await client.get(f"/users/{author['id']}/media")
    assert any(m["smallUrl"] == "https://cdn.example.com/small.jpg" for m in media_before.json()["items"])

    # EXECUTE SOFT DELETE
    del_resp = await client.delete(f"/posts/{post_id}", headers=author_auth)
    assert del_resp.status_code == 204

    # Idempotent repeat
    del_again = await client.delete(f"/posts/{post_id}", headers=author_auth)
    assert del_again.status_code == 204

    # Surface 1: Detail -> 404
    detail_resp = await client.get(f"/posts/{post_id}")
    assert detail_resp.status_code == 404

    # Surface 2: Feed -> excluded
    feed_after = await client.get("/feed", headers=viewer_auth)
    assert all(item["id"] != post_id for item in feed_after.json()["items"])

    # Surface 3: Search -> excluded
    search_after = await client.get(f"/search/originals?q={unique_keyword}", headers=viewer_auth)
    assert all(item["id"] != post_id for item in search_after.json()["items"])

    # Surface 4: Profile Media -> excluded
    media_after = await client.get(f"/users/{author['id']}/media")
    assert all(m["smallUrl"] != "https://cdn.example.com/small.jpg" for m in media_after.json()["items"])

    # Surface 5: Direct Replies
    replies_resp = await client.get(f"/posts/{post_id}/replies")
    assert replies_resp.status_code == 200
    assert any(item["id"] == reply_id for item in replies_resp.json()["items"])

    del_reply_resp = await client.delete(f"/posts/{reply_id}", headers=viewer_auth)
    assert del_reply_resp.status_code == 204
    replies_after_reply_del = await client.get(f"/posts/{post_id}/replies")
    assert all(item["id"] != reply_id for item in replies_after_reply_del.json()["items"])

    # Surface 6: Likes on deleted post -> 404
    like_resp = await client.post(f"/posts/{post_id}/like", headers=viewer_auth)
    assert like_resp.status_code == 404

    # Surface 7: Reposts on deleted post -> 404
    repost_resp = await client.post(f"/posts/{post_id}/repost", headers=viewer_auth)
    assert repost_resp.status_code == 404

    # Surface 8: Profile postCount decrements
    profile_after = await client.get(f"/users/{author['id']}")
    assert profile_after.status_code == 200
    assert profile_after.json()["item"]["postCount"] == 0

    # Surface 9: Creating a reply pointing to a deleted post -> 404 Not Found
    reply_to_deleted = await client.post(
        "/posts",
        headers=viewer_auth,
        json={"kind": "reply", "text": "Replying to deleted post", "reply_to_id": post_id},
    )
    assert reply_to_deleted.status_code == 404


@pytest.mark.anyio
async def test_checkpoint_two_session_edit_race(client: AsyncClient):
    author = await register_user(client, "author")
    auth_header = {"Authorization": f"Bearer {author['token']}"}

    create_resp = await client.post(
        "/posts",
        headers=auth_header,
        json={"kind": "original", "text": "Draft content"},
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["item"]["id"]
    current_version = create_resp.json()["item"]["version"]
    assert current_version == 1

    phone_edit = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "Phone edit revision", "version": current_version},
    )
    assert phone_edit.status_code == 200
    assert phone_edit.json()["item"]["version"] == 2

    laptop_edit = await client.patch(
        f"/posts/{post_id}",
        headers=auth_header,
        json={"text": "Laptop conflicting revision", "version": current_version},
    )
    assert laptop_edit.status_code == 409
    assert laptop_edit.json()["error"]["code"] == "CONFLICT"
    assert "version" in laptop_edit.json()["error"]["details"][0]["field"]
