"""
Tests for GET /feed endpoint (Stage A).
"""

from fastapi.testclient import TestClient


def test_feed_default_limit(client: TestClient):
    response = client.get("/feed")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "nextCursor" in data
    assert "hasMore" in data
    assert len(data["items"]) == 10
    assert data["hasMore"] is True
    assert data["nextCursor"] is not None


def test_feed_valid_custom_limits(client: TestClient):
    res_5 = client.get("/feed?limit=5")
    assert res_5.status_code == 200
    data_5 = res_5.json()
    assert len(data_5["items"]) == 5
    assert data_5["hasMore"] is True

    res_1 = client.get("/feed?limit=1")
    assert res_1.status_code == 200
    data_1 = res_1.json()
    assert len(data_1["items"]) == 1
    assert data_1["hasMore"] is True

    res_50 = client.get("/feed?limit=50")
    assert res_50.status_code == 200
    data_50 = res_50.json()
    # 30 total originals in seed fixture
    assert len(data_50["items"]) == 30
    assert data_50["hasMore"] is False
    assert data_50["nextCursor"] is None


def test_feed_limit_out_of_bounds_rejected(client: TestClient):
    res_0 = client.get("/feed?limit=0")
    assert res_0.status_code == 400
    err_0 = res_0.json()
    assert err_0["error"]["code"] == "VALIDATION_ERROR"
    assert "requestId" in err_0

    res_51 = client.get("/feed?limit=51")
    assert res_51.status_code == 400
    err_51 = res_51.json()
    assert err_51["error"]["code"] == "VALIDATION_ERROR"

    res_neg = client.get("/feed?limit=-5")
    assert res_neg.status_code == 400

    res_str = client.get("/feed?limit=abc")
    assert res_str.status_code == 400


def test_feed_pagination_three_pages_no_duplicates_or_skips(client: TestClient):
    all_seen_ids = []
    
    # Page 1
    res1 = client.get("/feed?limit=10")
    assert res1.status_code == 200
    d1 = res1.json()
    items1 = d1["items"]
    assert len(items1) == 10
    assert d1["hasMore"] is True
    cursor1 = d1["nextCursor"]
    assert cursor1 is not None
    all_seen_ids.extend([item["id"] for item in items1])

    # Page 2
    res2 = client.get(f"/feed?cursor={cursor1}&limit=10")
    assert res2.status_code == 200
    d2 = res2.json()
    items2 = d2["items"]
    assert len(items2) == 10
    assert d2["hasMore"] is True
    cursor2 = d2["nextCursor"]
    assert cursor2 is not None
    all_seen_ids.extend([item["id"] for item in items2])

    # Page 3
    res3 = client.get(f"/feed?cursor={cursor2}&limit=10")
    assert res3.status_code == 200
    d3 = res3.json()
    items3 = d3["items"]
    assert len(items3) == 10
    assert d3["hasMore"] is False
    assert d3["nextCursor"] is None
    all_seen_ids.extend([item["id"] for item in items3])

    # Total 30 items, all unique
    assert len(all_seen_ids) == 30
    assert len(set(all_seen_ids)) == 30


def test_feed_timestamp_tie_preserved(client: TestClient):
    # Posts 10 and 11 share the timestamp '2026-09-02T12:00:00.000Z'
    # Request page size 15 so the tie boundary is traversed
    res = client.get("/feed?limit=15")
    assert res.status_code == 200
    items = res.json()["items"]
    ids = [item["id"] for item in items]
    
    # Check that both tied posts are in the list in deterministic id DESC order
    post_10_id = "11111111-1111-4111-8111-111111111110"
    post_11_id = "11111111-1111-4111-8111-111111111111"
    assert post_10_id in ids
    assert post_11_id in ids
    assert ids.index(post_11_id) < ids.index(post_10_id)


def test_feed_malformed_cursor_returns_400(client: TestClient):
    res = client.get("/feed?cursor=not-a-valid-cursor")
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "requestId" in data


def test_feed_legacy_page_param_rejected(client: TestClient):
    res = client.get("/feed?page=1")
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "page" in data["error"]["message"] or "page" in str(data["error"]["details"])


def test_feed_unknown_query_param_rejected(client: TestClient):
    res = client.get("/feed?foo=bar")
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_feed_duplicate_query_param_rejected(client: TestClient):
    res = client.get("/feed?limit=10&limit=20")
    assert res.status_code == 400
    data = res.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_feed_wire_camel_case(client: TestClient):
    res = client.get("/feed?limit=1")
    assert res.status_code == 200
    data = res.json()
    assert "nextCursor" in data
    assert "hasMore" in data
    assert "items" in data
    item = data["items"][0]
    assert "createdAt" in item
    assert "likeCount" in item
    assert "replyCount" in item
    assert "likedByViewer" in item
    assert "replyToId" in item
    assert "repostOfId" in item
    # Ensure old prototype keys do not leak
    assert "next_cursor" not in data
    assert "has_more" not in data
    assert "like_count" not in item
    assert "total_posts" not in data
