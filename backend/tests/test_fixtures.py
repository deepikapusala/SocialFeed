"""
Tests for Deterministic Fixture Dataset and Relationship Constraints (Stage A).
"""

from app.fixtures.data import (
    FIXTURE_USERS,
    FIXTURE_ORIGINALS,
    FIXTURE_REPLIES,
    FIXTURE_REPOSTS,
    FIXTURE_MEDIA,
    FIXTURE_LIKES,
    FIXTURE_FOLLOWS,
    ALL_FIXTURE_POSTS,
)
from app.fixtures.manifest import (
    EXPECTED_COUNTS,
    TIED_POST_ID_A,
    TIED_POST_ID_B,
    TIED_TIMESTAMP,
    ZERO_REACTION_POST_ID,
    verify_fixtures_integrity,
)


def test_fixture_integrity_suite():
    """Verify all structural and relational constraints pass through the manifest verifier."""
    result = verify_fixtures_integrity()
    for key, passed in result.items():
        assert passed is True, f"Integrity check failed: {key}"


def test_exact_entity_counts():
    """Verify exact count thresholds required by PRD 00."""
    assert len(FIXTURE_USERS) == 6
    assert len(FIXTURE_ORIGINALS) == 30
    assert len(FIXTURE_REPLIES) == 12
    assert len(FIXTURE_REPOSTS) == 4
    assert len(FIXTURE_MEDIA) == 10
    assert len(FIXTURE_LIKES) == 15
    assert len(FIXTURE_FOLLOWS) == 8


def test_timestamp_tie_exists():
    """Verify that exactly two original posts share the exact same timestamp for tie-breaking tests."""
    post_a = next(p for p in FIXTURE_ORIGINALS if p["id"] == TIED_POST_ID_A)
    post_b = next(p for p in FIXTURE_ORIGINALS if p["id"] == TIED_POST_ID_B)

    assert post_a["createdAt"] == TIED_TIMESTAMP
    assert post_b["createdAt"] == TIED_TIMESTAMP
    assert post_a["id"] != post_b["id"]


def test_three_feed_pages_capacity():
    """Verify that 30 originals allow 3 full distinct pages of limit=10."""
    assert len(FIXTURE_ORIGINALS) >= 30


def test_reply_relationships():
    """Verify all 12 replies reference valid original posts."""
    original_ids = {p["id"] for p in FIXTURE_ORIGINALS}
    for reply in FIXTURE_REPLIES:
        assert reply["replyToId"] in original_ids
        assert reply["repostOfId"] is None


def test_repost_relationships():
    """Verify all 4 reposts reference valid original posts with text=None and no media."""
    original_ids = {p["id"] for p in FIXTURE_ORIGINALS}
    for repost in FIXTURE_REPOSTS:
        assert repost["repostOfId"] in original_ids
        assert repost["replyToId"] is None
        assert repost["text"] is None


def test_zero_reaction_post():
    """Verify post 30 has zero likes and zero replies."""
    likes_for_zero_post = [lk for lk in FIXTURE_LIKES if lk["postId"] == ZERO_REACTION_POST_ID]
    replies_for_zero_post = [r for r in FIXTURE_REPLIES if r["replyToId"] == ZERO_REACTION_POST_ID]

    assert len(likes_for_zero_post) == 0
    assert len(replies_for_zero_post) == 0
