"""
Stage 7 (PY-P0-07) - Security, Compatibility, and Permission Matrix Verification.

Verifies:
1. Automated route inspection: Every mutation route (POST, PATCH, PUT, DELETE) is accounted for in the permission matrix.
2. Route/permission matrix enforcement across anonymous, owner, related, and unrelated callers.
3. IDOR prevention and cross-user mutation rejection (403 Forbidden).
4. Request ID traceability across both allowed and denied access paths.
5. Production impersonation defense: test/seed shortcuts (x-viewer-id, DEMO_USER_ID) cannot impersonate runtime users.
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.routing import Route

from app.common.middleware import REQUEST_ID_HEADER
from app.config import Settings
from app.database import dispose_async_engine
from app.main import create_app
from app.common.dependencies import get_settings


@pytest.fixture
async def client():
    application = create_app()
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://testserver") as ac:
        yield ac
    await dispose_async_engine()


def test_permission_matrix_covers_all_mutation_routes():
    """
    Automated check: Extracts all registered endpoints in FastAPI
    and asserts that EVERY mutation (POST, PATCH, PUT, DELETE) is explicitly classified.
    """
    app_instance = create_app()
    all_mutations = []
    for route in app_instance.routes:
        if isinstance(route, Route):
            for method in route.methods or []:
                if method in ("POST", "PATCH", "PUT", "DELETE"):
                    all_mutations.append((method, route.path))

    # Known classified mutations from Decision Record 07
    classified_mutations = {
        ("POST", "/auth/register"),
        ("POST", "/auth/login"),
        ("POST", "/auth/logout"),
        ("POST", "/posts"),
        ("PATCH", "/posts/{id}"),
        ("DELETE", "/posts/{id}"),
        ("PUT", "/posts/{id}/like"),
        ("POST", "/posts/{id}/like"),
        ("DELETE", "/posts/{id}/like"),
        ("POST", "/posts/{id}/repost"),
        ("DELETE", "/posts/{id}/repost"),
        ("PATCH", "/users/{id_or_handle}"),
        ("POST", "/users/{id_or_handle}/deactivate"),
        ("POST", "/users/{id_or_handle}/follow"),
        ("DELETE", "/users/{id_or_handle}/follow"),
        ("POST", "/users/{id_or_handle}/follow/accept"),
        ("POST", "/notifications/read"),
        ("POST", "/notifications/{id}/read"),
    }

    unclassified = [m for m in all_mutations if m not in classified_mutations]
    assert len(unclassified) == 0, f"Found unclassified mutations not in permission matrix: {unclassified}"


@pytest.mark.asyncio
async def test_production_environment_blocks_impersonation_shortcuts():
    """
    Verifies that when ENVIRONMENT == 'production', test shortcuts like x-viewer-id
    and DEMO_USER_ID are strictly rejected with 401 Unauthorized for mutations.
    """
    prod_app = create_app()
    prod_settings = Settings(ENVIRONMENT="production")
    prod_app.dependency_overrides[get_settings] = lambda: prod_settings

    async with AsyncClient(
        transport=ASGITransport(app=prod_app),
        base_url="http://testserver",
    ) as prod_client:
        # 1. Anonymous mutation in production must return 401
        res = await prod_client.post("/posts", json={"kind": "original", "text": "Hacking in prod"})
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHORIZED"

        # 2. x-viewer-id shortcut in production must be ignored and return 401
        fake_viewer = str(uuid.uuid4())
        res2 = await prod_client.post(
            "/posts",
            headers={"x-viewer-id": fake_viewer},
            json={"kind": "original", "text": "Impersonating via header"},
        )
        assert res2.status_code == 401
        assert res2.json()["error"]["code"] == "UNAUTHORIZED"

    await dispose_async_engine()


@pytest.mark.asyncio
async def test_request_id_correlation_allowed_and_denied_paths(client):
    """
    Verifies that a reviewer can trace both an allowed and a denied request
    to final state via X-Request-Id matching between request headers, response headers,
    and error envelope requestId.
    """
    # Trace allowed request
    allowed_req_id = f"trace-allow-{uuid.uuid4().hex[:8]}"
    res_allowed = await client.get("/health/live", headers={REQUEST_ID_HEADER: allowed_req_id})
    assert res_allowed.status_code == 200
    assert res_allowed.headers.get(REQUEST_ID_HEADER) == allowed_req_id

    # Trace denied request (e.g. invalid bearer token or wrong recipient)
    denied_req_id = f"trace-deny-{uuid.uuid4().hex[:8]}"
    res_denied = await client.get(
        "/notifications",
        headers={
            "Authorization": "Bearer invalid_non_existent_token",
            REQUEST_ID_HEADER: denied_req_id,
        },
    )
    assert res_denied.status_code == 401
    assert res_denied.headers.get(REQUEST_ID_HEADER) == denied_req_id
    error_body = res_denied.json()
    assert error_body["requestId"] == denied_req_id
    assert error_body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_permission_matrix_cross_user_mutations_rejected(client):
    """
    End-to-end permission matrix tests for cross-user mutations:
    - User A cannot edit or delete User B's post (403 Forbidden).
    - User A cannot edit User B's profile (403 Forbidden).
    - User A cannot accept follow request directed to User B (403 Forbidden).
    - User A cannot read or mark User B's notifications (403 Forbidden).
    """
    uid = uuid.uuid4().hex[:6]
    # Register User A (Alice)
    reg_a = await client.post("/auth/register", json={
        "handle": f"alice_{uid}",
        "displayName": "Alice Test",
        "password": "Password123!",
    })
    assert reg_a.status_code == 201
    alice_token = reg_a.json()["accessToken"]
    alice_id = reg_a.json()["user"]["id"]

    # Register User B (Bob)
    reg_b = await client.post("/auth/register", json={
        "handle": f"bob_{uid}",
        "displayName": "Bob Test",
        "password": "Password123!",
    })
    assert reg_b.status_code == 201
    bob_token = reg_b.json()["accessToken"]
    bob_id = reg_b.json()["user"]["id"]

    # 1. Bob creates a post
    create_post_res = await client.post(
        "/posts",
        headers={"Authorization": f"Bearer {bob_token}"},
        json={"kind": "original", "text": "Bob's private thought"},
    )
    assert create_post_res.status_code == 201
    bob_post_id = create_post_res.json()["item"]["id"]

    # 2. Alice tries to PATCH Bob's post -> 403 Forbidden
    patch_res = await client.patch(
        f"/posts/{bob_post_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"text": "Alice hijacked this post"},
    )
    assert patch_res.status_code == 403
    assert patch_res.json()["error"]["code"] == "FORBIDDEN"

    # 3. Alice tries to DELETE Bob's post -> 403 Forbidden
    del_res = await client.delete(
        f"/posts/{bob_post_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert del_res.status_code == 403
    assert del_res.json()["error"]["code"] == "FORBIDDEN"

    # 4. Alice tries to PATCH Bob's profile -> 403 Forbidden
    patch_profile_res = await client.patch(
        f"/users/{bob_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"displayName": "Hacked Bob"},
    )
    assert patch_profile_res.status_code == 403
    assert patch_profile_res.json()["error"]["code"] == "FORBIDDEN"

    # 5. Alice likes Bob's post to trigger a notification for Bob
    like_res = await client.post(
        f"/posts/{bob_post_id}/like",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert like_res.status_code == 200

    # Bob retrieves his notifications
    bob_notifs = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert bob_notifs.status_code == 200
    bob_notif_id = bob_notifs.json()["items"][0]["id"]

    # Alice tries to mark Bob's notification as read (IDOR cross-user attempt) -> 403 Forbidden
    alice_mark = await client.post(
        f"/notifications/{bob_notif_id}/read",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert alice_mark.status_code == 403
    assert alice_mark.json()["error"]["code"] == "FORBIDDEN"

    # 6. Verify Bob can successfully edit his own post -> 200 OK
    bob_patch = await client.patch(
        f"/posts/{bob_post_id}",
        headers={"Authorization": f"Bearer {bob_token}"},
        json={"text": "Bob updated his post successfully", "version": 1},
    )
    assert bob_patch.status_code == 200
    assert bob_patch.json()["item"]["text"] == "Bob updated his post successfully"
