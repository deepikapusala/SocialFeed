"""
Tests for dependency injection overrides on FastAPI routes (Stage A).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from fastapi.testclient import TestClient
from app.common.dependencies import get_repository
from app.repositories.base import SocialRepositoryProtocol


class MockTestRepository(SocialRepositoryProtocol):
    """
    Mock test repository returning isolated, custom data.
    """

    async def list_original_feed(
        self,
        cursor_tuple: Optional[Tuple[datetime, str]],
        limit: int,
        viewer_id: str,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mock-feed-post-id-1",
                "kind": "original",
                "text": "Overridden mock feed post",
                "createdAt": datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc),
                "author": {
                    "id": "mock-author-id-1",
                    "handle": "mockuser",
                    "displayName": "Mock User",
                    "avatar": None,
                },
                "media": [],
                "likeCount": 99,
                "replyCount": 5,
                "likedByViewer": True,
                "replyToId": None,
                "repostOfId": None,
            }
        ]

    async def get_post_detail(
        self,
        post_id: str,
        viewer_id: str,
    ) -> Optional[Dict[str, Any]]:
        return {
            "id": post_id,
            "kind": "original",
            "text": "Overridden mock detail post",
            "createdAt": datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc),
            "author": {
                "id": "mock-author-id-1",
                "handle": "mockuser",
                "displayName": "Mock User",
                "avatar": None,
            },
            "media": [],
            "likeCount": 42,
            "replyCount": 0,
            "likedByViewer": False,
            "replyToId": None,
            "repostOfId": None,
        }

    async def get_user_profile(
        self,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        return {
            "id": user_id,
            "handle": "mock_custom_handle",
            "displayName": "Mock Custom Name",
            "bio": "Mock custom bio for test override",
            "avatar": None,
            "postCount": 100,
            "followerCount": 200,
            "followingCount": 300,
        }

    async def list_direct_replies(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return []

    async def list_profile_media(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return []

    async def search_originals(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return []

    async def user_exists(self, user_id: str) -> bool:
        return True

    async def get_post_kind(self, post_id: str) -> Optional[str]:
        return "original"


def test_repository_dependency_override_on_feed(app, client: TestClient):
    mock_repo = MockTestRepository()
    app.dependency_overrides[get_repository] = lambda: mock_repo

    response = client.get("/feed")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["text"] == "Overridden mock feed post"
    assert data["items"][0]["likeCount"] == 99


def test_repository_dependency_override_on_post_detail(app, client: TestClient):
    mock_repo = MockTestRepository()
    app.dependency_overrides[get_repository] = lambda: mock_repo

    post_id = "11111111-1111-1111-1111-111111111111"
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["item"]["text"] == "Overridden mock detail post"
    assert data["item"]["likeCount"] == 42


def test_repository_dependency_override_on_user_profile(app, client: TestClient):
    mock_repo = MockTestRepository()
    app.dependency_overrides[get_repository] = lambda: mock_repo

    user_id = "22222222-2222-2222-2222-222222222222"
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["item"]["handle"] == "mock_custom_handle"
    assert data["item"]["followerCount"] == 200
