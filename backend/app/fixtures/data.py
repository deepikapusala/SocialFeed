"""
Deterministic In-Memory Fixtures (Stage A).

Satisfies all PRD 00 & PRD 02 fixture requirements:
- Exactly 6 users (including demo user 'asha' and zero-media user)
- Exactly 30 original posts (including timestamp tie and zero-reaction cases)
- Exactly 12 replies (all referencing valid originals)
- Exactly 4 reposts (all referencing valid originals, text=None, media=[])
- Exactly 10 media rows (with dimensions, alt text, variants, positions 0..3)
- Exactly 15 likes (no duplicates)
- Exactly 8 follow edges (directional, no self-follows, no duplicates)
"""

from datetime import datetime, timezone
from typing import Dict, Any, List


# ---------------------------------------------------------------------------
# 1. USERS (6 Users)
# ---------------------------------------------------------------------------
FIXTURE_USERS: List[Dict[str, Any]] = [
    {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "handle": "asha",
        "displayName": "Asha Patel",
        "bio": "Software engineer & amateur landscape photographer 📷✨",
        "avatar": {
            "smallUrl": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80",
            "largeUrl": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&q=80",
        },
    },
    {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02",
        "handle": "yosemite_wanderer",
        "displayName": "Marcus Thorne",
        "bio": "Exploring national parks, alpine lakes, and pine forests 🌲⛰️",
        "avatar": {
            "smallUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&q=80",
            "largeUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=80",
        },
    }, 
    {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03",
        "handle": "atelier_canvas",
        "displayName": "Elena Rostova",
        "bio": "Contemporary oil painter & studio artist. Textures and color palette studies 🎨",
        "avatar": {
            "smallUrl": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&q=80",
            "largeUrl": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=80",
        },
    },
    {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04",
        "handle": "street_lens",
        "displayName": "David Kim",
        "bio": "Urban geometry, night lights, and street shadows 🏙️🚶",
        "avatar": {
            "smallUrl": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&q=80",
            "largeUrl": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&q=80",
        },
    },
    {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05",
        "handle": "urban_geometry",
        "displayName": "Clara Vance",
        "bio": "Architectural forms, minimal facades, and concrete shadows 🏛️📐",
        "avatar": {
            "smallUrl": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&q=80",
            "largeUrl": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&q=80",
        },
    },
    {
        "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06",
        "handle": "zero_media_user",
        "displayName": "Jordan Lee",
        "bio": "New to the platform. Dedicated edge-case user with 0 posts & 0 media.",
        "avatar": None,
    },
]


# ---------------------------------------------------------------------------
# 2. MEDIA (10 Media Rows)
# ---------------------------------------------------------------------------
FIXTURE_MEDIA: List[Dict[str, Any]] = [
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01",
        "postId": "11111111-1111-4111-8111-111111111101",
        "altText": "Morning mist rising over pine forests",
        "width": 1200,
        "height": 800,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 30, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb02",
        "postId": "11111111-1111-4111-8111-111111111101",
        "altText": "Sunlight piercing through redwood canopy",
        "width": 1200,
        "height": 800,
        "position": 1,
        "smallUrl": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 30, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb03",
        "postId": "11111111-1111-4111-8111-111111111102",
        "altText": "Textured oil painting on raw linen canvas",
        "width": 1080,
        "height": 1080,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=1080&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 29, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb04",
        "postId": "11111111-1111-4111-8111-111111111103",
        "altText": "Golden hour shadows across city avenues",
        "width": 1080,
        "height": 1350,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1080&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 28, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb05",
        "postId": "11111111-1111-4111-8111-111111111104",
        "altText": "Curving concrete facade and geometric architecture",
        "width": 1080,
        "height": 1350,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1080&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 27, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb06",
        "postId": "11111111-1111-4111-8111-111111111105",
        "altText": "Fresh handmade pasta with olive oil",
        "width": 1080,
        "height": 1080,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1080&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 26, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb07",
        "postId": "11111111-1111-4111-8111-111111111106",
        "altText": "Slow drip coffee and latte art",
        "width": 1080,
        "height": 1350,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1080&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 25, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb08",
        "postId": "11111111-1111-4111-8111-111111111107",
        "altText": "Turquoise ocean waters and rolling tides",
        "width": 1200,
        "height": 800,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 24, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb09",
        "postId": "11111111-1111-4111-8111-111111111108",
        "altText": "Autumn/Winter minimalist fashion look",
        "width": 1080,
        "height": 1350,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1080&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 23, 0, tzinfo=timezone.utc),
    },
    {
        "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb10",
        "postId": "11111111-1111-4111-8111-111111111109",
        "altText": "Stargazing under the Milky Way night sky",
        "width": 1200,
        "height": 800,
        "position": 0,
        "smallUrl": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=400&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1200&q=80",
        "createdAt": datetime(2026, 9, 1, 10, 22, 0, tzinfo=timezone.utc),
    },
]


# ---------------------------------------------------------------------------
# 3. ORIGINAL POSTS (30 Originals)
# ---------------------------------------------------------------------------
# Note on Timestamp Tie:
# Post 10 ("...1110") and Post 11 ("...1111") deliberately share
# the exact timestamp: 2026-09-01T10:20:00.000Z.
# In descending order (createdAt DESC, id DESC), Post 11 comes first, Post 10 second.
# With limit=10, Page 1 ends on Post 11, and Page 2 begins on Post 10.
# ---------------------------------------------------------------------------
def _generate_originals() -> List[Dict[str, Any]]:
    authors = [
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02",
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03",
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04",
        "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05",
    ]

    posts = []
    # Base timestamps counting down from 10:30 down to 10:01
    for i in range(1, 31):
        post_id = f"11111111-1111-4111-8111-1111111111{i:02d}"
        author_id = authors[(i - 1) % len(authors)]

        # Deliberate tie: i=10 and i=11 share 10:20:00.000Z
        if i in (10, 11):
            created_at = datetime(2026, 9, 1, 10, 20, 0, 0, tzinfo=timezone.utc)
        elif i < 10:
            created_at = datetime(2026, 9, 1, 10, 30 - (i - 1), 0, 0, tzinfo=timezone.utc)
        else:
            # i > 11: offset by 1 minute to preserve monotonic order
            created_at = datetime(2026, 9, 1, 10, 30 - i, 0, 0, tzinfo=timezone.utc)

        posts.append({
            "id": post_id,
            "authorId": author_id,
            "kind": "original",
            "text": f"Original post #{i} caption. Beautiful photo exploration in nature, art, and urban spaces #explore #{i}",
            "createdAt": created_at,
            "replyToId": None,
            "repostOfId": None,
        })
    return posts


FIXTURE_ORIGINALS: List[Dict[str, Any]] = _generate_originals()


# ---------------------------------------------------------------------------
# 4. REPLIES (12 Direct Replies to Originals)
# ---------------------------------------------------------------------------
FIXTURE_REPLIES: List[Dict[str, Any]] = [
    {
        "id": f"22222222-2222-4222-8222-2222222222{i:02d}",
        "authorId": FIXTURE_USERS[(i % 5)]["id"],
        "kind": "reply",
        "text": f"Insightful comment and reply #{i} to the original photo post!",
        "createdAt": datetime(2026, 9, 1, 11, i, 0, 0, tzinfo=timezone.utc),
        "replyToId": f"11111111-1111-4111-8111-1111111111{(i % 6) + 1:02d}",
        "repostOfId": None,
    }
    for i in range(1, 13)
]


# ---------------------------------------------------------------------------
# 5. REPOSTS (4 Reposts of Originals)
# ---------------------------------------------------------------------------
FIXTURE_REPOSTS: List[Dict[str, Any]] = [
    {
        "id": f"33333333-3333-4333-8333-3333333333{i:02d}",
        "authorId": FIXTURE_USERS[i]["id"],
        "kind": "repost",
        "text": None,
        "createdAt": datetime(2026, 9, 1, 12, i, 0, 0, tzinfo=timezone.utc),
        "replyToId": None,
        "repostOfId": f"11111111-1111-4111-8111-1111111111{i:02d}",
    }
    for i in range(1, 5)
]


# ---------------------------------------------------------------------------
# 6. LIKES (15 Likes on Originals / Replies)
# ---------------------------------------------------------------------------
FIXTURE_LIKES: List[Dict[str, Any]] = [
    # Demo user ("asha") likes
    {"id": "44444444-4444-4444-8444-444444444401", "userId": FIXTURE_USERS[0]["id"], "postId": FIXTURE_ORIGINALS[0]["id"]},
    {"id": "44444444-4444-4444-8444-444444444402", "userId": FIXTURE_USERS[0]["id"], "postId": FIXTURE_ORIGINALS[1]["id"]},
    {"id": "44444444-4444-4444-8444-444444444403", "userId": FIXTURE_USERS[0]["id"], "postId": FIXTURE_ORIGINALS[2]["id"]},
    {"id": "44444444-4444-4444-8444-444444444404", "userId": FIXTURE_USERS[0]["id"], "postId": FIXTURE_ORIGINALS[3]["id"]},
    # Other users' likes on originals
    {"id": "44444444-4444-4444-8444-444444444405", "userId": FIXTURE_USERS[1]["id"], "postId": FIXTURE_ORIGINALS[0]["id"]},
    {"id": "44444444-4444-4444-8444-444444444406", "userId": FIXTURE_USERS[2]["id"], "postId": FIXTURE_ORIGINALS[0]["id"]},
    {"id": "44444444-4444-4444-8444-444444444407", "userId": FIXTURE_USERS[3]["id"], "postId": FIXTURE_ORIGINALS[1]["id"]},
    {"id": "44444444-4444-4444-8444-444444444408", "userId": FIXTURE_USERS[4]["id"], "postId": FIXTURE_ORIGINALS[1]["id"]},
    {"id": "44444444-4444-4444-8444-444444444409", "userId": FIXTURE_USERS[1]["id"], "postId": FIXTURE_ORIGINALS[4]["id"]},
    {"id": "44444444-4444-4444-8444-444444444410", "userId": FIXTURE_USERS[2]["id"], "postId": FIXTURE_ORIGINALS[5]["id"]},
    {"id": "44444444-4444-4444-8444-444444444411", "userId": FIXTURE_USERS[3]["id"], "postId": FIXTURE_ORIGINALS[6]["id"]},
    {"id": "44444444-4444-4444-8444-444444444412", "userId": FIXTURE_USERS[4]["id"], "postId": FIXTURE_ORIGINALS[7]["id"]},
    # Likes on replies
    {"id": "44444444-4444-4444-8444-444444444413", "userId": FIXTURE_USERS[0]["id"], "postId": FIXTURE_REPLIES[0]["id"]},
    {"id": "44444444-4444-4444-8444-444444444414", "userId": FIXTURE_USERS[1]["id"], "postId": FIXTURE_REPLIES[0]["id"]},
    {"id": "44444444-4444-4444-8444-444444444415", "userId": FIXTURE_USERS[2]["id"], "postId": FIXTURE_REPLIES[1]["id"]},
]


# ---------------------------------------------------------------------------
# 7. FOLLOWS (8 Follow Edges)
# ---------------------------------------------------------------------------
FIXTURE_FOLLOWS: List[Dict[str, Any]] = [
    {"followerId": FIXTURE_USERS[0]["id"], "followingId": FIXTURE_USERS[1]["id"]},
    {"followerId": FIXTURE_USERS[0]["id"], "followingId": FIXTURE_USERS[2]["id"]},
    {"followerId": FIXTURE_USERS[0]["id"], "followingId": FIXTURE_USERS[3]["id"]},
    {"followerId": FIXTURE_USERS[1]["id"], "followingId": FIXTURE_USERS[0]["id"]},
    {"followerId": FIXTURE_USERS[2]["id"], "followingId": FIXTURE_USERS[0]["id"]},
    {"followerId": FIXTURE_USERS[3]["id"], "followingId": FIXTURE_USERS[4]["id"]},
    {"followerId": FIXTURE_USERS[4]["id"], "followingId": FIXTURE_USERS[1]["id"]},
    {"followerId": FIXTURE_USERS[4]["id"], "followingId": FIXTURE_USERS[2]["id"]},
]


# Combined list of all post types (originals + replies + reposts)
ALL_FIXTURE_POSTS: List[Dict[str, Any]] = FIXTURE_ORIGINALS + FIXTURE_REPLIES + FIXTURE_REPOSTS
