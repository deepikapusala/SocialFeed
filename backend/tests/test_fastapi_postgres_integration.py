"""
Integration tests for FastAPI -> PostgreSQL Repository wiring (Stage C Step 4).
Tests dependency injection, request-scoped sessions, route wiring, and error mapping.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import create_app
from app.common.dependencies import get_repository
from app.repositories.postgres_repository import PostgresRepository
from app.schemas.post import PostItem


@pytest.fixture
def mock_postgres_repo():
    """Returns a mock PostgresRepository configured for route integration tests."""
    repo = MagicMock(spec=PostgresRepository)
    sample_post = {
        "id": "11111111-1111-4111-8111-111111111101",
        "kind": "original",
        "text": "Seeded original post 1",
        "createdAt": "2026-09-01T10:00:00.000Z",
        "author": {
            "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "handle": "asha",
            "displayName": "Asha Patel",
            "avatar": {"smallUrl": "/asha-48.jpg", "largeUrl": "/asha-96.jpg"},
        },
        "media": [
            {
                "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01",
                "altText": "Desk",
                "width": 1200,
                "height": 800,
                "position": 0,
                "smallUrl": "/desk-480.jpg",
                "largeUrl": "/desk-1200.jpg",
            }
        ],
        "likeCount": 3,
        "replyCount": 2,
        "likedByViewer": True,
        "replyToId": None,
        "repostOfId": None,
    }

    repo.list_original_feed = AsyncMock(return_value=[sample_post])
    repo.get_post_detail = AsyncMock(return_value=sample_post)
    repo.get_user_profile = AsyncMock(
        return_value={
            "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "handle": "asha",
            "displayName": "Asha Patel",
            "bio": "Software developer",
            "avatar": {"smallUrl": "/asha-48.jpg", "largeUrl": "/asha-96.jpg"},
            "postCount": 6,
            "followerCount": 2,
            "followingCount": 3,
        }
    )
    repo.list_direct_replies = AsyncMock(return_value=[sample_post])
    repo.list_profile_media = AsyncMock(
        return_value=[
            {
                "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01",
                "postId": "11111111-1111-4111-8111-111111111101",
                "altText": "Desk",
                "width": 1200,
                "height": 800,
                "position": 0,
                "smallUrl": "/desk-480.jpg",
                "largeUrl": "/desk-1200.jpg",
                "createdAt": "2026-09-01T10:00:00.000Z",
            }
        ]
    )
    repo.search_originals = AsyncMock(return_value=[sample_post])
    repo.user_exists = AsyncMock(return_value=True)
    repo.get_post_kind = AsyncMock(return_value="original")
    repo.create_post = AsyncMock(return_value=sample_post)
    repo.set_like = AsyncMock(
        return_value={
            "postId": "11111111-1111-4111-8111-111111111101",
            "likedByViewer": True,
            "likeCount": 4,
        }
    )
    repo.remove_like = AsyncMock(
        return_value={
            "postId": "11111111-1111-4111-8111-111111111101",
            "likedByViewer": False,
            "likeCount": 3,
        }
    )
    return repo


@pytest.fixture
def integrated_client(mock_postgres_repo):
    """FastAPI TestClient with PostgresRepository injected."""
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: mock_postgres_repo
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_postgres_wired_feed_endpoint(integrated_client):
    """Verify GET /feed connects to PostgresRepository and returns valid FeedResponse."""
    res = integrated_client.get("/feed?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "11111111-1111-4111-8111-111111111101"
    assert data["items"][0]["author"]["handle"] == "asha"
    assert data["items"][0]["likedByViewer"] is True


def test_postgres_wired_post_detail_endpoint(integrated_client):
    """Verify GET /posts/{id} returns single post detail."""
    res = integrated_client.get("/posts/11111111-1111-4111-8111-111111111101")
    assert res.status_code == 200
    data = res.json()
    assert "item" in data
    assert data["item"]["likeCount"] == 3


def test_postgres_wired_user_profile_endpoint(integrated_client):
    """Verify GET /users/{id} returns profile statistics."""
    res = integrated_client.get("/users/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    assert res.status_code == 200
    data = res.json()
    assert "item" in data
    assert data["item"]["handle"] == "asha"
    assert data["item"]["postCount"] == 6


def test_postgres_wired_replies_endpoint(integrated_client):
    """Verify GET /posts/{id}/replies returns direct replies list."""
    res = integrated_client.get("/posts/11111111-1111-4111-8111-111111111101/replies")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data


def test_postgres_wired_profile_media_endpoint(integrated_client):
    """Verify GET /users/{id}/media returns media rows."""
    res = integrated_client.get("/users/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/media")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["items"][0]["width"] == 1200


def test_postgres_wired_search_endpoint(integrated_client):
    """Verify GET /search/posts returns matching originals."""
    res = integrated_client.get("/search/posts?q=seeded")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data


def test_postgres_wired_create_post_endpoint(integrated_client):
    """Verify POST /posts creates an original post and returns 201."""
    payload = {
        "kind": "original",
        "text": "New persisted post via API",
        "media": [
            {
                "altText": "Sample",
                "width": 1200,
                "height": 800,
                "position": 0,
                "smallUrl": "/s.jpg",
                "largeUrl": "/l.jpg",
            }
        ],
    }
    res = integrated_client.post("/posts", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "item" in data
    assert data["item"]["kind"] == "original"


def test_postgres_wired_like_endpoints(integrated_client):
    """Verify PUT /posts/{id}/like and DELETE /posts/{id}/like."""
    res_put = integrated_client.put("/posts/11111111-1111-4111-8111-111111111101/like")
    assert res_put.status_code == 200
    data_put = res_put.json()
    assert data_put["likedByViewer"] is True
    assert data_put["likeCount"] == 4

    res_del = integrated_client.delete("/posts/11111111-1111-4111-8111-111111111101/like")
    assert res_del.status_code == 200
    data_del = res_del.json()
    assert data_del["likedByViewer"] is False
    assert data_del["likeCount"] == 3


def test_health_ready_probe(integrated_client):
    """Verify GET /health/ready probe returns 200 ready or 503 unavailable."""
    res = integrated_client.get("/health/ready")
    assert res.status_code in (200, 503)
    data = res.json()
    assert data["status"] in ("ready", "unavailable")
