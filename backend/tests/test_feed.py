# test_feed.py
# Tests and a live demonstration of the generator-based feed paginator.
# Run this file directly:  python test_feed.py

import types  # Used to check that paginate_posts returns a real generator

from feed import paginate_posts


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def build_posts(n):
    """Create a simple list of n fake posts for testing."""
    return [{"id": i, "username": f"user{i}", "caption": f"Post {i}"} for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# Test Case 1: 30 posts, batch_size=10    3 batches of 10
# ---------------------------------------------------------------------------

def test_30_posts():
    print("=" * 50)
    print("Test Case 1: 30 posts, batch_size=10")
    print("=" * 50)

    sample_posts = build_posts(30)
    batches = list(paginate_posts(sample_posts, batch_size=10))

    assert len(batches) == 3,           f"Expected 3 batches, got {len(batches)}"
    assert len(batches[0]) == 10,       f"Expected batch 1 to have 10 posts, got {len(batches[0])}"
    assert len(batches[1]) == 10,       f"Expected batch 2 to have 10 posts, got {len(batches[1])}"
    assert len(batches[2]) == 10,       f"Expected batch 3 to have 10 posts, got {len(batches[2])}"

    print(f"  Total batches : {len(batches)}")
    print(f"  Batch 1 size  : {len(batches[0])} posts")
    print(f"  Batch 2 size  : {len(batches[1])} posts")
    print(f"  Batch 3 size  : {len(batches[2])} posts")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test Case 2: 25 posts, batch_size=10    10 + 10 + 5
# ---------------------------------------------------------------------------

def test_25_posts():
    print("=" * 50)
    print("Test Case 2: 25 posts, batch_size=10")
    print("=" * 50)

    sample_posts = build_posts(25)
    batches = list(paginate_posts(sample_posts, batch_size=10))

    assert len(batches) == 3,           f"Expected 3 batches, got {len(batches)}"
    assert len(batches[0]) == 10,       f"Expected batch 1 to have 10 posts, got {len(batches[0])}"
    assert len(batches[1]) == 10,       f"Expected batch 2 to have 10 posts, got {len(batches[1])}"
    assert len(batches[2]) == 5,        f"Expected batch 3 to have 5 posts, got {len(batches[2])}"

    print(f"  Total batches : {len(batches)}")
    print(f"  Batch 1 size  : {len(batches[0])} posts")
    print(f"  Batch 2 size  : {len(batches[1])} posts")
    print(f"  Batch 3 size  : {len(batches[2])} posts   final smaller batch")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test Case 3: 7 posts, batch_size=10    1 batch of 7
# ---------------------------------------------------------------------------

def test_fewer_than_batch_size():
    print("=" * 50)
    print("Test Case 3: 7 posts, batch_size=10")
    print("=" * 50)

    sample_posts = build_posts(7)
    batches = list(paginate_posts(sample_posts, batch_size=10))

    assert len(batches) == 1,           f"Expected 1 batch, got {len(batches)}"
    assert len(batches[0]) == 7,        f"Expected batch 1 to have 7 posts, got {len(batches[0])}"

    print(f"  Total batches : {len(batches)}")
    print(f"  Batch 1 size  : {len(batches[0])} posts")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Test Case 4: Confirm paginate_posts returns a real generator, not a list
# ---------------------------------------------------------------------------

def test_is_generator():
    print("=" * 50)
    print("Test Case 4: paginate_posts() must return a generator")
    print("=" * 50)

    sample_posts = build_posts(15)

    # Call the function but do NOT convert it to a list yet.
    result = paginate_posts(sample_posts, batch_size=10)

    # A generator is an instance of types.GeneratorType.
    assert isinstance(result, types.GeneratorType), (
        f"Expected a generator, but got {type(result)}"
    )

    print(f"  Type of result : {type(result)}")
    print("  It is a real Python generator (uses yield, not return).")
    print("  PASSED\n")


# ---------------------------------------------------------------------------
# Live Demonstration
# ---------------------------------------------------------------------------

def demo():
    print("=" * 50)
    print("LIVE DEMONSTRATION: paginate_posts on real data")
    print("=" * 50)

    # Import the real sample data from data.py
    from data import posts as real_posts

    print(f"  Total posts in data.py : {len(real_posts)}")
    print()

    # Iterate over the generator  each loop gives us one batch
    for batch_number, batch in enumerate(paginate_posts(real_posts, batch_size=10), start=1):
        print(f"  Batch {batch_number}: {len(batch)} posts")
        for post in batch:
            print(f"    id={post['id']:>2}  @{post['username']:<20}  \"{post['caption']}\"")
        print()

    print("  Demonstration complete.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_30_posts()
    test_25_posts()
    test_fewer_than_batch_size()
    test_is_generator()
    demo()
    print("All tests passed.")
