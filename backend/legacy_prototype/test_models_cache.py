# legacy_prototype/test_models_cache.py
# Tests for Point 12 (Post, Comment, Like models) and Point 13 (@cache_feed decorator).
# Run from within legacy_prototype:  python test_models_cache.py

import time
from .models import Post, Comment, Like
from .feed   import cache_feed, get_feed
from .data   import posts as raw_posts

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
    print("  PASSED\n")

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
    print("  PASSED\n")

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

def test_post_eq():
    print("=" * 55)
    print("Test: Post.__eq__")
    print("=" * 55)

    p1 = Post(1, "user_a", "Caption A")
    p2 = Post(1, "user_b", "Caption B")
    p3 = Post(2, "user_a", "Caption A")

    assert p1 == p2, "Same post_id should be equal"
    assert p1 != p3, "Different post_id should not be equal"
    assert p1 != 42,  "Post != non-Post type"

    print("  PASSED\n")

def test_post_len():
    print("=" * 55)
    print("Test: Post.__len__")
    print("=" * 55)

    p = Post(post_id=3, username="maya_portraits", caption="Golden hour")

    assert len(p) == 0, f"Expected len=0, got {len(p)}"

    p.add_comment(Comment(1, "alice", "Love it!"))
    p.add_comment(Comment(2, "bob",   "Stunning!"))
    assert len(p) == 2, f"Expected len=2, got {len(p)}"

    p.add_like(Like(1, "carol"))
    p.add_like(Like(2, "dave"))
    p.add_like(Like(3, "eve"))
    assert len(p) == 5, f"Expected len=5, got {len(p)}"

    print("  PASSED\n")

def test_cache_hit_and_miss():
    print("=" * 55)
    print("Test: cache_feed — first call miss, second call hit")
    print("=" * 55)

    call_count = {"n": 0}

    @cache_feed(ttl=30)
    def fetch_feed(posts):
        call_count["n"] += 1
        return list(posts)

    sample = tuple(raw_posts[:5])

    result1 = fetch_feed(sample)
    assert call_count["n"] == 1, "Real function should have run once"

    result2 = fetch_feed(sample)
    assert call_count["n"] == 1, "Real function should NOT run a second time"

    assert result1 == result2, "Cached result should match original result"
    print("  PASSED\n")

def test_cache_expiry():
    print("=" * 55)
    print("Test: cache_feed — cache expires after TTL")
    print("=" * 55)

    call_count = {"n": 0}

    @cache_feed(ttl=1)
    def fetch_feed_short_ttl(posts):
        call_count["n"] += 1
        return list(posts)

    sample = tuple(raw_posts[:5])

    fetch_feed_short_ttl(sample)
    assert call_count["n"] == 1

    fetch_feed_short_ttl(sample)
    assert call_count["n"] == 1

    time.sleep(1.1)

    fetch_feed_short_ttl(sample)
    assert call_count["n"] == 2, f"Expected 2 real calls after expiry, got {call_count['n']}"
    print("  PASSED\n")

def test_wraps_preserves_metadata():
    print("=" * 55)
    print("Test: @wraps preserves function name and docstring")
    print("=" * 55)

    assert get_feed.__name__ == "get_feed"
    print("  PASSED\n")

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

    print("All tests passed.")
