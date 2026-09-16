"""
Fixture Manifest and Relationship Verification (Stage A).
"""

from datetime import datetime, timezone
from typing import Dict, Any
import uuid

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


EXPECTED_COUNTS: Dict[str, int] = {
    "users": 6,
    "originals": 30,
    "replies": 12,
    "reposts": 4,
    "media": 10,
    "likes": 15,
    "follows": 8,
}

DEMO_USER_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
TIED_POST_ID_A = "11111111-1111-4111-8111-111111111110"
TIED_POST_ID_B = "11111111-1111-4111-8111-111111111111"
TIED_TIMESTAMP = datetime(2026, 9, 1, 10, 20, 0, 0, tzinfo=timezone.utc)
ZERO_REACTION_POST_ID = "11111111-1111-4111-8111-111111111130"


def verify_fixtures_integrity() -> Dict[str, bool]:
    """
    Validates all structural, relational, and cardinality rules across the fixture dataset.
    Raises AssertionError if any fixture contract requirement is violated.
    """
    # 1. Verify Entity Counts
    assert len(FIXTURE_USERS) == EXPECTED_COUNTS["users"], f"Expected {EXPECTED_COUNTS['users']} users, got {len(FIXTURE_USERS)}"
    assert len(FIXTURE_ORIGINALS) == EXPECTED_COUNTS["originals"], f"Expected {EXPECTED_COUNTS['originals']} originals, got {len(FIXTURE_ORIGINALS)}"
    assert len(FIXTURE_REPLIES) == EXPECTED_COUNTS["replies"], f"Expected {EXPECTED_COUNTS['replies']} replies, got {len(FIXTURE_REPLIES)}"
    assert len(FIXTURE_REPOSTS) == EXPECTED_COUNTS["reposts"], f"Expected {EXPECTED_COUNTS['reposts']} reposts, got {len(FIXTURE_REPOSTS)}"
    assert len(FIXTURE_MEDIA) == EXPECTED_COUNTS["media"], f"Expected {EXPECTED_COUNTS['media']} media rows, got {len(FIXTURE_MEDIA)}"
    assert len(FIXTURE_LIKES) == EXPECTED_COUNTS["likes"], f"Expected {EXPECTED_COUNTS['likes']} likes, got {len(FIXTURE_LIKES)}"
    assert len(FIXTURE_FOLLOWS) == EXPECTED_COUNTS["follows"], f"Expected {EXPECTED_COUNTS['follows']} follows, got {len(FIXTURE_FOLLOWS)}"

    user_ids = {u["id"] for u in FIXTURE_USERS}
    user_handles = {u["handle"] for u in FIXTURE_USERS}
    original_ids = {p["id"] for p in FIXTURE_ORIGINALS}
    all_post_ids = {p["id"] for p in ALL_FIXTURE_POSTS}

    # 2. Verify Unique Users & Handles
    assert len(user_ids) == len(FIXTURE_USERS), "Duplicate user IDs found"
    assert len(user_handles) == len(FIXTURE_USERS), "Duplicate user handles found"
    for u in FIXTURE_USERS:
        uuid.UUID(u["id"])
        assert u["handle"] == u["handle"].lower(), f"User handle '{u['handle']}' must be lowercase"

    # 3. Verify Unique Post IDs
    assert len(all_post_ids) == len(ALL_FIXTURE_POSTS), "Duplicate post IDs found across fixtures"
    for p in ALL_FIXTURE_POSTS:
        uuid.UUID(p["id"])
        assert p["authorId"] in user_ids, f"Post {p['id']} authorId {p['authorId']} not in users"

    # 4. Verify Reply Relationships
    for r in FIXTURE_REPLIES:
        assert r["kind"] == "reply"
        assert r["replyToId"] in original_ids, f"Reply {r['id']} references non-original {r['replyToId']}"
        assert r["repostOfId"] is None
        assert r["text"] and len(r["text"]) > 0

    # 5. Verify Repost Relationships
    repost_pairs = set()
    for rp in FIXTURE_REPOSTS:
        assert rp["kind"] == "repost"
        assert rp["repostOfId"] in original_ids, f"Repost {rp['id']} references non-original {rp['repostOfId']}"
        assert rp["replyToId"] is None
        assert rp["text"] is None
        pair = (rp["authorId"], rp["repostOfId"])
        assert pair not in repost_pairs, f"Duplicate repost by same user for original: {pair}"
        repost_pairs.add(pair)

    # 6. Verify Media Relationships
    media_positions_per_post: Dict[str, set] = {}
    for m in FIXTURE_MEDIA:
        uuid.UUID(m["id"])
        assert m["postId"] in original_ids, f"Media {m['id']} belongs to non-original {m['postId']}"
        assert 0 <= m["position"] <= 3, f"Media position {m['position']} out of range 0..3"
        assert m["width"] > 0 and m["height"] > 0
        assert m["smallUrl"] and m["largeUrl"] and m["altText"]

        pos_set = media_positions_per_post.setdefault(m["postId"], set())
        assert m["position"] not in pos_set, f"Duplicate media position {m['position']} in post {m['postId']}"
        pos_set.add(m["position"])

    # 7. Verify Likes (No duplicates, valid targets)
    like_pairs = set()
    for lk in FIXTURE_LIKES:
        uuid.UUID(lk["id"])
        assert lk["userId"] in user_ids, f"Like {lk['id']} has invalid userId {lk['userId']}"
        assert lk["postId"] in all_post_ids, f"Like {lk['id']} has invalid postId {lk['postId']}"
        pair = (lk["userId"], lk["postId"])
        assert pair not in like_pairs, f"Duplicate like found for user-post pair: {pair}"
        like_pairs.add(pair)

    # 8. Verify Follows (No self-follow, no duplicate pairs)
    follow_pairs = set()
    for fl in FIXTURE_FOLLOWS:
        assert fl["followerId"] in user_ids, f"Follower {fl['followerId']} not in users"
        assert fl["followingId"] in user_ids, f"Following {fl['followingId']} not in users"
        assert fl["followerId"] != fl["followingId"], f"Self-follow detected for {fl['followerId']}"
        pair = (fl["followerId"], fl["followingId"])
        assert pair not in follow_pairs, f"Duplicate follow pair found: {pair}"
        follow_pairs.add(pair)

    # 9. Verify Timestamp Tie
    post_a = next(p for p in FIXTURE_ORIGINALS if p["id"] == TIED_POST_ID_A)
    post_b = next(p for p in FIXTURE_ORIGINALS if p["id"] == TIED_POST_ID_B)
    assert post_a["createdAt"] == post_b["createdAt"] == TIED_TIMESTAMP, "Timestamp tie not satisfied"
    assert post_a["id"] != post_b["id"], "Tied posts must have distinct IDs"

    # 10. Verify Zero-Reaction Post Exists
    zero_post_likes = [lk for lk in FIXTURE_LIKES if lk["postId"] == ZERO_REACTION_POST_ID]
    zero_post_replies = [r for r in FIXTURE_REPLIES if r["replyToId"] == ZERO_REACTION_POST_ID]
    assert len(zero_post_likes) == 0, f"Expected 0 likes for {ZERO_REACTION_POST_ID}, got {len(zero_post_likes)}"
    assert len(zero_post_replies) == 0, f"Expected 0 replies for {ZERO_REACTION_POST_ID}, got {len(zero_post_replies)}"

    return {
        "counts_verified": True,
        "users_verified": True,
        "posts_verified": True,
        "replies_verified": True,
        "reposts_verified": True,
        "media_verified": True,
        "likes_verified": True,
        "follows_verified": True,
        "timestamp_tie_verified": True,
        "zero_reactions_verified": True,
    }
