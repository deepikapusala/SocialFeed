# test_models_cache.py
# Tests for Point 12 (Post, Comment, Like models)
#      and Point 13 (@cache_feed decorator).
# Run with:  python test_models_cache.py

import time
from models import Post, Comment, Like
from feed   import cache_feed, get_feed
from data   import posts as raw_posts


# ===========================================================================
# POINT 12 TESTS — Data modeling
# ===========================================================================

# ---------------------------------------------------------------------------
# Test: Comment.__repr__ shows readable output
# ---------------------------------------------------------------------------
def test_comment_repr():
    print("=" * 55)
    print("Test: Comment.__repr__")
    print("=" * 55)

    c = Comment(comment_id=1, username="alex", text="Beautiful shot!")
    result = repr(c)

    assert "1"                in result, "comment_id missing from repr"
    assert "alex"             in result, "username missing from repr"
    assert "Beautiful shot!"  in result, "text missing from repr"

    print(f"  repr(comment) = {c}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: Comment.__eq__ compares by comment_id
# ---------------------------------------------------------------------------
def test_comment_eq():
    print("=" * 55)
    print("Test: Comment.__eq__")
    print("=" * 55)

    c1 = Comment(1, "alice", "Wow!")
    c2 = Comment(1, "bob",   "Different text but same id")
    c3 = Comment(2, "alice", "Wow!")

    assert c1 == c2, "Same comment_id should be equal"
    assert c1 != c3, "Different comment_id should not be equal"
    assert c1 != "not a comment", "Comment != non-Comment type"

    print(f"  c1 = {c1}")
    print(f"  c2 = {c2}")
    print(f"  c3 = {c3}")
    print(f"  c1 == c2 (same id=1)  : {c1 == c2}")
    print(f"  c1 != c3 (diff id)    : {c1 != c3}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: Like.__repr__ and Like.__eq__
# ---------------------------------------------------------------------------
def test_like():
    print("=" * 55)
    print("Test: Like.__repr__ and Like.__eq__")
    print("=" * 55)

    l1 = Like(like_id=10, username="maya")
    l2 = Like(like_id=10, username="different_user")
    l3 = Like(like_id=99, username="maya")

    assert "10"   in repr(l1), "like_id missing from repr"
    assert "maya" in repr(l1), "username missing from repr"
    assert l1 == l2, "Same like_id should be equal"
    assert l1 != l3, "Different like_id should not be equal"

    print(f"  l1 = {l1}")
    print(f"  l2 = {l2}")
    print(f"  l1 == l2 (same id=10) : {l1 == l2}")
    print(f"  l1 != l3 (diff id)    : {l1 != l3}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: Post.__repr__
# ---------------------------------------------------------------------------
def test_post_repr():
    print("=" * 55)
    print("Test: Post.__repr__")
    print("=" * 55)

    p = Post(post_id=5, username="ocean_pulse", caption="Big waves at sunset")
    result = repr(p)

    assert "5"                   in result, "post_id missing from repr"
    assert "ocean_pulse"         in result, "username missing from repr"
    assert "Big waves at sunset" in result, "caption missing from repr"

    print(f"  repr(post) = {p}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: Post.__eq__ compares by post_id
# ---------------------------------------------------------------------------
def test_post_eq():
    print("=" * 55)
    print("Test: Post.__eq__")
    print("=" * 55)

    p1 = Post(1, "user_a", "Caption A")
    p2 = Post(1, "user_b", "Caption B")   # same id, different content
    p3 = Post(2, "user_a", "Caption A")   # different id

    assert p1 == p2, "Same post_id should be equal"
    assert p1 != p3, "Different post_id should not be equal"
    assert p1 != 42,  "Post != non-Post type"

    print(f"  p1 = {p1}")
    print(f"  p2 = {p2}")
    print(f"  p3 = {p3}")
    print(f"  p1 == p2 (same id=1) : {p1 == p2}")
    print(f"  p1 != p3 (diff id)   : {p1 != p3}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: Post.__len__ counts comments + likes
# ---------------------------------------------------------------------------
def test_post_len():
    print("=" * 55)
    print("Test: Post.__len__")
    print("=" * 55)

    p = Post(post_id=3, username="maya_portraits", caption="Golden hour")

    # New post has no comments or likes
    assert len(p) == 0, f"Expected len=0, got {len(p)}"
    print(f"  Fresh post    : len(post) = {len(p)}  (0 comments + 0 likes)")

    # Add 2 comments
    p.add_comment(Comment(1, "alice", "Love it!"))
    p.add_comment(Comment(2, "bob",   "Stunning!"))
    assert len(p) == 2, f"Expected len=2, got {len(p)}"
    print(f"  After 2 comments: len(post) = {len(p)}")

    # Add 3 likes
    p.add_like(Like(1, "carol"))
    p.add_like(Like(2, "dave"))
    p.add_like(Like(3, "eve"))
    assert len(p) == 5, f"Expected len=5, got {len(p)}"
    print(f"  After 3 likes   : len(post) = {len(p)}  (2 comments + 3 likes)")

    print(f"  Full post repr  : {p}")
    print("  PASSED\n")


# ===========================================================================
# POINT 13 TESTS — @cache_feed decorator
# ===========================================================================

# ---------------------------------------------------------------------------
# Test: First call is a cache miss, second call is a cache hit
# ---------------------------------------------------------------------------
def test_cache_hit_and_miss():
    print("=" * 55)
    print("Test: cache_feed — first call miss, second call hit")
    print("=" * 55)

    # Create a fresh decorated function for this test so the cache starts empty.
    # We use a call counter to check whether the real function actually ran.
    call_count = {"n": 0}

    @cache_feed(ttl=30)
    def fetch_feed(posts):
        call_count["n"] += 1   # increments only when the real function runs
        return list(posts)

    sample = tuple(raw_posts[:5])   # a small tuple of 5 posts

    # First call — cache is empty, so the real function must run.
    result1 = fetch_feed(sample)
    assert call_count["n"] == 1, "Real function should have run once"

    # Second call — cache is still valid (no time has passed), so
    # the real function must NOT run again.
    result2 = fetch_feed(sample)
    assert call_count["n"] == 1, "Real function should NOT run a second time"

    # Both calls should return the same data.
    assert result1 == result2, "Cached result should match original result"

    print(f"  After call 1: real function ran {call_count['n']} time(s)  (cache MISS)")
    print(f"  After call 2: real function ran {call_count['n']} time(s)  (cache HIT)")
    print(f"  Both results identical: {result1 == result2}")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: Cache expires after ttl seconds
# ---------------------------------------------------------------------------
def test_cache_expiry():
    print("=" * 55)
    print("Test: cache_feed — cache expires after TTL")
    print("=" * 55)

    call_count = {"n": 0}

    # Use ttl=1 so we don't have to wait 30 seconds during the test.
    @cache_feed(ttl=1)
    def fetch_feed_short_ttl(posts):
        call_count["n"] += 1
        return list(posts)

    sample = tuple(raw_posts[:5])

    # Call 1 — cache miss
    fetch_feed_short_ttl(sample)
    assert call_count["n"] == 1

    # Call 2 — cache hit (cache is still fresh)
    fetch_feed_short_ttl(sample)
    assert call_count["n"] == 1
    print(f"  After 2 quick calls: real function ran {call_count['n']} time(s)")

    # Wait for the TTL to expire
    print("  Waiting 1.1 seconds for cache to expire...")
    time.sleep(1.1)

    # Call 3 — cache expired, so the real function must run again
    fetch_feed_short_ttl(sample)
    assert call_count["n"] == 2, f"Expected 2 real calls after expiry, got {call_count['n']}"
    print(f"  After TTL expiry  : real function ran {call_count['n']} time(s)  (cache MISS again)")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: @wraps preserves the original function name and docstring
# ---------------------------------------------------------------------------
def test_wraps_preserves_metadata():
    print("=" * 55)
    print("Test: @wraps preserves function name and docstring")
    print("=" * 55)

    # get_feed is decorated with @cache_feed(ttl=30) in feed.py
    assert get_feed.__name__ == "get_feed", (
        f"Expected __name__='get_feed', got '{get_feed.__name__}'"
    )
    assert get_feed.__doc__ is not None, "__doc__ should not be None"

    print(f"  get_feed.__name__ = '{get_feed.__name__}'")
    print(f"  get_feed.__doc__  = (first line) '{get_feed.__doc__.strip().splitlines()[0]}'")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test: get_feed returns all posts correctly
# ---------------------------------------------------------------------------
def test_get_feed_returns_all_posts():
    print("=" * 55)
    print("Test: get_feed returns the full list of posts")
    print("=" * 55)

    # get_feed expects a tuple; convert raw_posts list to a tuple
    result = get_feed(tuple(raw_posts))

    assert isinstance(result, list),          "get_feed should return a list"
    assert len(result) == len(raw_posts),     f"Expected {len(raw_posts)} posts, got {len(result)}"
    assert result[0]["id"] == 1,              "First post id should be 1"
    assert result[-1]["id"] == 30,            "Last post id should be 30"

    print(f"  Total posts returned : {len(result)}")
    print(f"  First post           : id={result[0]['id']}, @{result[0]['username']}")
    print(f"  Last post            : id={result[-1]['id']}, @{result[-1]['username']}")
    print("  PASSED\n")


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    print("\n--- POINT 12: Data Models ---\n")
    test_comment_repr()
    test_comment_eq()
    test_like()
    test_post_repr()
    test_post_eq()
    test_post_len()

    print("\n--- POINT 13: @cache_feed decorator ---\n")
    test_cache_hit_and_miss()
    test_cache_expiry()
    test_wraps_preserves_metadata()
    test_get_feed_returns_all_posts()

    print("All tests passed.")
