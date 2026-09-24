"""
Tests for GET /users/{id} endpoint (Stage A).
"""

from fastapi.testclient import TestClient


def test_get_user_profile_valid_existing(client: TestClient):
    user_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 200
    data = res.json()
    assert "item" in data
    item = data["item"]
    assert item["id"] == user_id
    assert item["handle"] == "asha"
    assert item["displayName"] == "Asha Patel"
    assert "bio" in item
    assert "avatar" in item
    assert "postCount" in item
    assert "followerCount" in item
    assert "followingCount" in item
    assert item["postCount"] >= 0
    assert item["followerCount"] >= 0
    assert item["followingCount"] >= 0


def test_get_user_profile_malformed_uuid_returns_400(client: TestClient):
    res = client.get("/users/invalid-uuid-format")
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "requestId" in data


def test_get_user_profile_valid_missing_uuid_returns_404(client: TestClient):
    missing_user_id = "99999999-9999-9999-9999-999999999999"
    res = client.get(f"/users/{missing_user_id}")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert "requestId" in data


def test_follow_and_unfollow_user_endpoints(client: TestClient):
    target_user_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02"
    # PUT /users/{id}/follow
    res = client.put(f"/users/{target_user_id}/follow")
    assert res.status_code == 200
    data = res.json()
    assert data["userId"] == target_user_id
    assert data["followedByViewer"] is True
    assert "followerCount" in data

    # DELETE /users/{id}/follow
    del_res = client.delete(f"/users/{target_user_id}/follow")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["userId"] == target_user_id
    assert del_data["followedByViewer"] is False
    assert "followerCount" in del_data

