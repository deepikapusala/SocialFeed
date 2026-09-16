"""
Tests for GET /posts/{id} endpoint (Stage A).
"""

from fastapi.testclient import TestClient


def test_get_post_detail_valid_existing(client: TestClient):
    post_id = "11111111-1111-4111-8111-111111111101"
    res = client.get(f"/posts/{post_id}")
    assert res.status_code == 200
    data = res.json()
    assert "item" in data
    item = data["item"]
    assert item["id"] == post_id
    assert item["kind"] == "original"
    assert "createdAt" in item
    assert "likeCount" in item
    assert "replyCount" in item
    assert "likedByViewer" in item
    assert "author" in item
    assert "media" in item
    assert item["author"]["handle"] is not None


def test_get_post_detail_viewer_liked_state(client: TestClient):
    # Post 1 is liked by asha (DEMO_USER_ID)
    post_id = "11111111-1111-4111-8111-111111111101"
    res = client.get(f"/posts/{post_id}")
    assert res.status_code == 200
    assert res.json()["item"]["likedByViewer"] is True

    # Post 5 is not liked by asha in manifest (only liked by user 2)
    post_id_unliked = "11111111-1111-4111-8111-111111111105"
    res_unliked = client.get(f"/posts/{post_id_unliked}")
    assert res_unliked.status_code == 200
    assert res_unliked.json()["item"]["likedByViewer"] is False


def test_get_post_detail_malformed_uuid_returns_400(client: TestClient):
    res = client.get("/posts/not-a-uuid")
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "requestId" in data


def test_get_post_detail_valid_missing_uuid_returns_404(client: TestClient):
    missing_uuid = "99999999-9999-9999-9999-999999999999"
    res = client.get(f"/posts/{missing_uuid}")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert "requestId" in data
