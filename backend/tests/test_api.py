# test_api.py
# Point 14 — Tests for the FastAPI /feed endpoint.
# Run with:  python test_api.py
#
# FastAPI's TestClient lets us make HTTP requests to our app
# without actually starting a real server. This makes tests
# fast and easy to run anywhere.

from fastapi.testclient import TestClient
from main import app, ALL_POSTS


# Create the test client once and reuse it for every test.
client = TestClient(app)


# ---------------------------------------------------------------------------
# Test 1: cursor=0, limit=10 returns the first 10 posts
# ---------------------------------------------------------------------------

def test_first_batch():
    print("=" * 55)
    print("Test 1: GET /feed?cursor=0&limit=10  (first batch)")
    print("=" * 55)

    response = client.get("/feed?cursor=0&limit=10")

    assert response.status_code == 200, (
        f"Expected HTTP 200, got {response.status_code}"
    )

    data = response.json()

    assert data["count"]       == 10,   f"Expected 10 posts, got {data['count']}"
    assert data["next_cursor"] == 10,   f"Expected next_cursor=10, got {data['next_cursor']}"
    assert data["has_more"]    is True, f"Expected has_more=True"
    assert data["posts"][0]["id"] == 1, f"First post id should be 1"
    assert data["posts"][9]["id"] == 10, f"Last post in batch should be id=10"

    print(f"  HTTP status    : {response.status_code}")
    print(f"  Posts returned : {data['count']}")
    print(f"  next_cursor    : {data['next_cursor']}")
    print(f"  has_more       : {data['has_more']}")
    print(f"  First post     : id={data['posts'][0]['id']}, @{data['posts'][0]['username']}")
    print(f"  Last post      : id={data['posts'][9]['id']}, @{data['posts'][9]['username']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 2: cursor=10, limit=10 returns the next 10 posts
# ---------------------------------------------------------------------------

def test_second_batch():
    print("=" * 55)
    print("Test 2: GET /feed?cursor=10&limit=10  (second batch)")
    print("=" * 55)

    response = client.get("/feed?cursor=10&limit=10")
    data = response.json()

    assert response.status_code == 200
    assert data["count"]        == 10
    assert data["next_cursor"]  == 20
    assert data["has_more"]     is True
    assert data["posts"][0]["id"] == 11, "Second batch should start at id=11"
    assert data["posts"][9]["id"] == 20, "Second batch should end at id=20"

    print(f"  HTTP status    : {response.status_code}")
    print(f"  Posts returned : {data['count']}")
    print(f"  next_cursor    : {data['next_cursor']}")
    print(f"  has_more       : {data['has_more']}")
    print(f"  First post     : id={data['posts'][0]['id']}, @{data['posts'][0]['username']}")
    print(f"  Last post      : id={data['posts'][9]['id']}, @{data['posts'][9]['username']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 3: Final batch — has_more=false, next_cursor=null
# ---------------------------------------------------------------------------

def test_final_batch():
    print("=" * 55)
    print("Test 3: GET /feed?cursor=20&limit=10  (final batch)")
    print("=" * 55)

    response = client.get("/feed?cursor=20&limit=10")
    data = response.json()

    assert response.status_code == 200
    assert data["count"]        == 10
    assert data["has_more"]     is False,  "Last batch: has_more should be False"
    assert data["next_cursor"]  is None,   "Last batch: next_cursor should be null"
    assert data["posts"][0]["id"] == 21,   "Final batch should start at id=21"
    assert data["posts"][9]["id"] == 30,   "Final batch should end at id=30"

    print(f"  HTTP status    : {response.status_code}")
    print(f"  Posts returned : {data['count']}")
    print(f"  next_cursor    : {data['next_cursor']}  (null = no more pages)")
    print(f"  has_more       : {data['has_more']}")
    print(f"  First post     : id={data['posts'][0]['id']}, @{data['posts'][0]['username']}")
    print(f"  Last post      : id={data['posts'][9]['id']}, @{data['posts'][9]['username']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 4: cursor past the end returns empty posts list
# ---------------------------------------------------------------------------

def test_cursor_beyond_end():
    print("=" * 55)
    print("Test 4: GET /feed?cursor=100  (cursor past end of data)")
    print("=" * 55)

    response = client.get("/feed?cursor=100&limit=10")
    data = response.json()

    assert response.status_code == 200
    assert data["count"]       == 0,    "No posts should be returned past the end"
    assert data["has_more"]    is False, "has_more should be False past the end"
    assert data["next_cursor"] is None,  "next_cursor should be None past the end"
    assert data["posts"]       == [],    "posts list should be empty"

    print(f"  HTTP status    : {response.status_code}")
    print(f"  Posts returned : {data['count']} (empty list)")
    print(f"  has_more       : {data['has_more']}")
    print(f"  next_cursor    : {data['next_cursor']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 5: Negative cursor returns HTTP 400
# ---------------------------------------------------------------------------

def test_negative_cursor():
    print("=" * 55)
    print("Test 5: GET /feed?cursor=-1  (invalid cursor)")
    print("=" * 55)

    response = client.get("/feed?cursor=-1&limit=10")

    assert response.status_code == 400, (
        f"Expected HTTP 400, got {response.status_code}"
    )

    data = response.json()
    assert "cursor" in data["detail"].lower(), (
        f"Error message should mention 'cursor', got: {data['detail']}"
    )

    print(f"  HTTP status    : {response.status_code}  (Bad Request)")
    print(f"  Error detail   : {data['detail']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 6: limit=0 returns HTTP 400
# ---------------------------------------------------------------------------

def test_zero_limit():
    print("=" * 55)
    print("Test 6: GET /feed?limit=0  (invalid limit)")
    print("=" * 55)

    response = client.get("/feed?cursor=0&limit=0")

    assert response.status_code == 400, (
        f"Expected HTTP 400, got {response.status_code}"
    )

    data = response.json()
    assert "limit" in data["detail"].lower(), (
        f"Error message should mention 'limit', got: {data['detail']}"
    )

    print(f"  HTTP status    : {response.status_code}  (Bad Request)")
    print(f"  Error detail   : {data['detail']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 7: limit=51 returns HTTP 400 (exceeds max of 50)
# ---------------------------------------------------------------------------

def test_limit_too_large():
    print("=" * 55)
    print("Test 7: GET /feed?limit=51  (limit exceeds maximum)")
    print("=" * 55)

    response = client.get("/feed?cursor=0&limit=51")

    assert response.status_code == 400, (
        f"Expected HTTP 400, got {response.status_code}"
    )

    print(f"  HTTP status    : {response.status_code}  (Bad Request)")
    print(f"  Error detail   : {response.json()['detail']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 8: Default parameters work (no cursor or limit in URL)
# ---------------------------------------------------------------------------

def test_default_parameters():
    print("=" * 55)
    print("Test 8: GET /feed  (no params, uses defaults cursor=0 limit=10)")
    print("=" * 55)

    response = client.get("/feed")
    data = response.json()

    assert response.status_code == 200
    assert data["count"]        == 10
    assert data["next_cursor"]  == 10
    assert data["has_more"]     is True

    print(f"  HTTP status    : {response.status_code}")
    print(f"  Posts returned : {data['count']}")
    print(f"  next_cursor    : {data['next_cursor']}")
    print(f"  has_more       : {data['has_more']}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 9: Full pagination walk — consume all 30 posts page by page
# ---------------------------------------------------------------------------

def test_full_pagination_walk():
    print("=" * 55)
    print("Test 9: Walk through all pages until has_more=False")
    print("=" * 55)

    cursor     = 0
    page       = 1
    total_seen = 0

    while True:
        response = client.get(f"/feed?cursor={cursor}&limit=10")
        assert response.status_code == 200

        data   = response.json()
        batch  = data["posts"]
        total_seen += len(batch)

        print(f"  Page {page}: {len(batch)} posts "
              f"(ids {batch[0]['id']}–{batch[-1]['id']}) "
              f"| next_cursor={data['next_cursor']} | has_more={data['has_more']}")

        if not data["has_more"]:
            break

        cursor = data["next_cursor"]
        page  += 1

    assert total_seen == len(ALL_POSTS), (
        f"Expected {len(ALL_POSTS)} total posts, walked {total_seen}"
    )

    print(f"\n  Total posts seen across all pages : {total_seen}")
    print(f"  Total posts in data.py            : {len(ALL_POSTS)}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test 10: Response JSON contains all expected keys
# ---------------------------------------------------------------------------

def test_response_shape():
    print("=" * 55)
    print("Test 10: Response JSON has the expected keys")
    print("=" * 55)

    response = client.get("/feed?cursor=0&limit=5")
    data = response.json()

    required_keys = {"posts", "next_cursor", "has_more", "count", "total_posts"}
    missing = required_keys - data.keys()
    assert not missing, f"Missing keys in response: {missing}"

    # Each post should have id, username, caption
    post = data["posts"][0]
    for field in ("id", "username", "caption"):
        assert field in post, f"Post is missing field: {field}"

    print(f"  Response keys  : {sorted(data.keys())}")
    print(f"  Post fields    : {sorted(post.keys())}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n--- POINT 14: FastAPI /feed endpoint tests ---\n")

    test_first_batch()
    test_second_batch()
    test_final_batch()
    test_cursor_beyond_end()
    test_negative_cursor()
    test_zero_limit()
    test_limit_too_large()
    test_default_parameters()
    test_full_pagination_walk()
    test_response_shape()

    print("All tests passed.")
