# Parameterized SQL Use Cases (Stage B — Step 4)

This document specifies and explains the ten canonical parameterized SQL use cases implemented in [`db/queries.sql`](file:///f:/Instagram/db/queries.sql) for the **Social Feed** relational model.

---

## 1. Overview & Parameter Conventions

In compliance with the **API Contract** ([`docs/00_Assignment_Brief_and_API_Contract.md`](file:///f:/Instagram/docs/00_Assignment_Brief_and_API_Contract.md)) and **Shared Database Modeling PRD** ([`docs/03_Shared_Database_Modeling_PRD.md`](file:///f:/Instagram/docs/03_Shared_Database_Modeling_PRD.md)), all database queries adhere to the following architecture:

1. **Parameter Binding Safety**: All dynamic values are bound via PostgreSQL positional parameters (`$1`, `$2`, etc.) or prepared statements (`PREPARE`). No user inputs are concatenated directly into SQL text.
2. **Explicit Data Types**: All parameters use explicit PostgreSQL types (`UUID`, `TIMESTAMPTZ`, `INTEGER`, `TEXT`, `UUID[]`).
3. **Deterministic Total Ordering**: Feed and listing queries order results by `(created_at DESC, id DESC)`. Because timestamps can collide across posts (e.g. Posts 10 & 11), the unique `id` (UUIDv4) provides an absolute, deterministic tie-breaker.
4. **Keyset / Cursor Pagination**: All paginated queries evaluate strictly smaller row tuples `(created_at, id) < ($cursor_created_at, $cursor_id)` without using `OFFSET`.
5. **Count & Aggregation Isolation**: Aggregations (like counts, reply counts, repost counts, follow counts) are computed using dedicated subqueries or grouped target CTEs rather than multi-table `JOIN` operations that multiply rows.

---

## 2. The 10 Parameterized SQL Use Cases

```
                                      SQL USE CASES DIRECTORY
┌──────────────────────────────┬─────────────────────────────────────────────────────────────┬──────────────────────────────┐
│ Query Name                   │ Purpose                                                     │ Pagination / Strategy        │
├──────────────────────────────┼─────────────────────────────────────────────────────────────┼──────────────────────────────┤
│ 1. get_home_feed             │ Global reverse-chronological feed of original posts         │ Keyset (created_at, id)      │
│ 2. get_post_detail           │ Detail view of a single post by UUID                        │ Point Lookup + Subqueries    │
│ 3. get_direct_replies        │ Chronological direct replies to an original post            │ Keyset (created_at, id)      │
│ 4. get_profile_media         │ Paginated image attachments for a user's original posts     │ Keyset (pm.created_at, pm.id)│
│ 5. get_profile_stats         │ Aggregated author metrics without row multiplication        │ Point Lookup + Scalar Counts │
│ 6. get_like_totals           │ Authoritative like counts for a batch of post UUIDs         │ UNNEST($1::uuid[]) + LEFT JOIN│
│ 7. get_viewer_state          │ Batch viewer reaction status check                          │ UNNEST($2::uuid[]) + LEFT JOIN│
│ 8. get_following_feed        │ Reverse-chronological originals from followed users         │ JOIN follows + Keyset Cursor │
│ 9. search_posts              │ Case-insensitive literal substring search on originals      │ ILIKE + Wildcard Escape      │
│ 10. get_repost_lookup        │ Check if a user reposted an original + retrieve metadata    │ Author & Original Reference  │
└──────────────────────────────┴─────────────────────────────────────────────────────────────┴──────────────────────────────┘
```

---

### Use Case 1: Home Feed (`get_home_feed`)

#### Purpose
Fetches the public global feed of original posts in reverse-chronological order, enriched with author profiles, accurate reaction counts, reply counts, and the current viewer's reaction state.

#### SQL Statement
```sql
PREPARE get_home_feed (timestamptz, uuid, integer, uuid) AS
SELECT
    p.id,
    p.kind,
    p.text,
    p.created_at,
    u.id AS author_id,
    u.handle AS author_handle,
    u.display_name AS author_display_name,
    u.avatar_small_url AS author_avatar_small_url,
    u.avatar_large_url AS author_avatar_large_url,
    (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
    (SELECT COUNT(*) FROM posts r WHERE r.reply_to_id = p.id) AS reply_count,
    EXISTS(SELECT 1 FROM post_likes pl WHERE pl.post_id = p.id AND pl.user_id = $4) AS liked_by_viewer
FROM posts p
JOIN users u ON u.id = p.author_id
WHERE p.kind = 'original'
  AND (
      $1::timestamptz IS NULL
      OR (p.created_at, p.id) < ($1, $2)
  )
ORDER BY p.created_at DESC, p.id DESC
LIMIT $3 + 1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `cursor_created_at` | `TIMESTAMPTZ` | Timestamp from previous page's last item (`NULL` for page 1) |
| `$2` | `cursor_id` | `UUID` | UUID from previous page's last item (`NULL` for page 1) |
| `$3` | `limit_count` | `INTEGER` | Requested page size (e.g., `10`) |
| `$4` | `viewer_id` | `UUID` | UUID of the requesting viewer to compute `liked_by_viewer` |

#### Pagination & Row Boundary
- Fetches `limit + 1` rows. If `rows.length > limit`, `hasMore = true`, the extra row is omitted from the response, and `nextCursor` is generated from the `$3`-th row.

---

### Use Case 2: Post Detail (`get_post_detail`)

#### Purpose
Retrieves comprehensive details for any single post (original, reply, or repost) including author information, like counts, reply counts, viewer reaction status, and target post metadata for reposts.

#### SQL Statement
```sql
PREPARE get_post_detail (uuid, uuid) AS
SELECT
    p.id,
    p.kind,
    p.text,
    p.created_at,
    p.reply_to_id,
    p.repost_of_id,
    u.id AS author_id,
    u.handle AS author_handle,
    u.display_name AS author_display_name,
    u.avatar_small_url AS author_avatar_small_url,
    u.avatar_large_url AS author_avatar_large_url,
    (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
    (SELECT COUNT(*) FROM posts r WHERE r.reply_to_id = p.id) AS reply_count,
    EXISTS(SELECT 1 FROM post_likes pl WHERE pl.post_id = p.id AND pl.user_id = $2) AS liked_by_viewer,
    ref_u.handle AS referenced_author_handle,
    ref_p.text AS referenced_text
FROM posts p
JOIN users u ON u.id = p.author_id
LEFT JOIN posts ref_p ON ref_p.id = p.repost_of_id
LEFT JOIN users ref_u ON ref_u.id = ref_p.author_id
WHERE p.id = $1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `post_id` | `UUID` | The target post UUID |
| `$2` | `viewer_id` | `UUID` | UUID of the requesting viewer |

---

### Use Case 3: Direct Replies (`get_direct_replies`)

#### Purpose
Returns the chronological stream of direct replies attached to a specified original post. Rejects replies-to-replies (enforcing the single-level hierarchy contract).

#### SQL Statement
```sql
PREPARE get_direct_replies (uuid, timestamptz, uuid, integer, uuid) AS
SELECT
    r.id,
    r.kind,
    r.text,
    r.created_at,
    r.reply_to_id,
    u.id AS author_id,
    u.handle AS author_handle,
    u.display_name AS author_display_name,
    u.avatar_small_url AS author_avatar_small_url,
    u.avatar_large_url AS author_avatar_large_url,
    (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = r.id) AS like_count,
    EXISTS(SELECT 1 FROM post_likes pl WHERE pl.post_id = r.id AND pl.user_id = $5) AS liked_by_viewer
FROM posts r
JOIN users u ON u.id = r.author_id
WHERE r.kind = 'reply'
  AND r.reply_to_id = $1
  AND (
      $2::timestamptz IS NULL
      OR (r.created_at, r.id) < ($2, $3)
  )
ORDER BY r.created_at DESC, r.id DESC
LIMIT $4 + 1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `parent_post_id` | `UUID` | UUID of the parent original post |
| `$2` | `cursor_created_at` | `TIMESTAMPTZ` | Timestamp cursor (`NULL` for page 1) |
| `$3` | `cursor_id` | `UUID` | UUID cursor (`NULL` for page 1) |
| `$4` | `limit_count` | `INTEGER` | Page size limit |
| `$5` | `viewer_id` | `UUID` | Current viewer UUID |

---

### Use Case 4: Profile Media (`get_profile_media`)

#### Purpose
Fetches paginated image attachment records belonging exclusively to a user's original posts, ordered by newest media first.

#### SQL Statement
```sql
PREPARE get_profile_media (uuid, timestamptz, uuid, integer) AS
SELECT
    pm.id,
    pm.post_id,
    pm.position,
    pm.alt_text,
    pm.width,
    pm.height,
    pm.small_url,
    pm.large_url,
    pm.created_at
FROM post_media pm
JOIN posts p ON p.id = pm.post_id
WHERE p.author_id = $1
  AND p.kind = 'original'
  AND (
      $2::timestamptz IS NULL
      OR (pm.created_at, pm.id) < ($2, $3)
  )
ORDER BY pm.created_at DESC, pm.id DESC
LIMIT $4 + 1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `user_id` | `UUID` | Author UUID whose media is being queried |
| `$2` | `cursor_created_at` | `TIMESTAMPTZ` | Media timestamp cursor (`NULL` for page 1) |
| `$3` | `cursor_id` | `UUID` | Media UUID cursor (`NULL` for page 1) |
| `$4` | `limit_count` | `INTEGER` | Page size limit |

---

### Use Case 5: Profile Stats (`get_profile_stats`)

#### Purpose
Returns author profile information and authoritative counts (originals, replies, reposts, total posts, followers, following) using separate scalar subqueries to eliminate Cartesian product count inflation.

#### SQL Statement
```sql
PREPARE get_profile_stats (uuid) AS
SELECT
    u.id,
    u.handle,
    u.display_name,
    u.bio,
    u.avatar_small_url,
    u.avatar_large_url,
    u.created_at,
    (SELECT COUNT(*) FROM posts p WHERE p.author_id = u.id AND p.kind = 'original') AS post_count,
    (SELECT COUNT(*) FROM posts p WHERE p.author_id = u.id AND p.kind = 'reply') AS reply_count,
    (SELECT COUNT(*) FROM posts p WHERE p.author_id = u.id AND p.kind = 'repost') AS repost_count,
    (SELECT COUNT(*) FROM posts p WHERE p.author_id = u.id) AS total_posts,
    (SELECT COUNT(*) FROM follows f WHERE f.following_id = u.id) AS follower_count,
    (SELECT COUNT(*) FROM follows f WHERE f.follower_id = u.id) AS following_count
FROM users u
WHERE u.id = $1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `user_id` | `UUID` | Target user UUID |

---

### Use Case 6: Like Totals (`get_like_totals`)

#### Purpose
Calculates exact like counts for an arbitrary batch of post UUIDs (e.g. from an in-memory list or feed page) in a single round-trip without multiplying rows.

#### SQL Statement
```sql
PREPARE get_like_totals (uuid[]) AS
SELECT
    target.post_id,
    COUNT(pl.user_id) AS like_count
FROM unnest($1) AS target(post_id)
LEFT JOIN post_likes pl ON pl.post_id = target.post_id
GROUP BY target.post_id;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `post_ids` | `UUID[]` | Array of target post UUIDs |

---

### Use Case 7: Viewer State (`get_viewer_state`)

#### Purpose
Computes the viewer's reaction state (`liked_by_viewer`) for a batch of post UUIDs in a single query.

#### SQL Statement
```sql
PREPARE get_viewer_state (uuid, uuid[]) AS
SELECT
    target.post_id,
    (pl.user_id IS NOT NULL) AS liked_by_viewer
FROM unnest($2) AS target(post_id)
LEFT JOIN post_likes pl ON pl.post_id = target.post_id AND pl.user_id = $1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `viewer_id` | `UUID` | Viewer UUID |
| `$2` | `post_ids` | `UUID[]` | Array of target post UUIDs |

---

### Use Case 8: Following Feed (`get_following_feed`)

#### Purpose
Demonstrates an interest-graph feed returning original posts created exclusively by accounts that the viewer follows.

#### Difference from Home Feed:
- **Home Feed** (`get_home_feed`): Global public stream containing original posts from all users across the platform.
- **Following Feed** (`get_following_feed`): Scoped strictly to accounts the viewer has an active follow edge to (`JOIN follows f ON f.following_id = p.author_id AND f.follower_id = $1`). Excludes posts from non-followed accounts.

#### SQL Statement
```sql
PREPARE get_following_feed (uuid, timestamptz, uuid, integer) AS
SELECT
    p.id,
    p.kind,
    p.text,
    p.created_at,
    u.id AS author_id,
    u.handle AS author_handle,
    u.display_name AS author_display_name,
    u.avatar_small_url AS author_avatar_small_url,
    u.avatar_large_url AS author_avatar_large_url,
    (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
    (SELECT COUNT(*) FROM posts r WHERE r.reply_to_id = p.id) AS reply_count,
    EXISTS(SELECT 1 FROM post_likes pl WHERE pl.post_id = p.id AND pl.user_id = $1) AS liked_by_viewer
FROM posts p
JOIN follows f ON f.following_id = p.author_id AND f.follower_id = $1
JOIN users u ON u.id = p.author_id
WHERE p.kind = 'original'
  AND (
      $2::timestamptz IS NULL
      OR (p.created_at, p.id) < ($2, $3)
  )
ORDER BY p.created_at DESC, p.id DESC
LIMIT $4 + 1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `viewer_id` | `UUID` | Viewer UUID |
| `$2` | `cursor_created_at` | `TIMESTAMPTZ` | Timestamp cursor (`NULL` for page 1) |
| `$3` | `cursor_id` | `UUID` | UUID cursor (`NULL` for page 1) |
| `$4` | `limit_count` | `INTEGER` | Page size limit |

---

### Use Case 9: Search (`search_posts`)

#### Purpose
Performs case-insensitive literal substring search against original post text. Escapes SQL wildcard characters (`%` and `_`) to ensure literal search matching as mandated by the API Contract.

#### SQL Statement
```sql
PREPARE search_posts (text, timestamptz, uuid, integer, uuid) AS
SELECT
    p.id,
    p.kind,
    p.text,
    p.created_at,
    u.id AS author_id,
    u.handle AS author_handle,
    u.display_name AS author_display_name,
    u.avatar_small_url AS author_avatar_small_url,
    u.avatar_large_url AS author_avatar_large_url,
    (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
    (SELECT COUNT(*) FROM posts r WHERE r.reply_to_id = p.id) AS reply_count,
    EXISTS(SELECT 1 FROM post_likes pl WHERE pl.post_id = p.id AND pl.user_id = $5) AS liked_by_viewer
FROM posts p
JOIN users u ON u.id = p.author_id
WHERE p.kind = 'original'
  AND p.text ILIKE '%' || replace(replace(trim($1), '_', '\_'), '%', '\%') || '%'
  AND (
      $2::timestamptz IS NULL
      OR (p.created_at, p.id) < ($2, $3)
  )
ORDER BY p.created_at DESC, p.id DESC
LIMIT $4 + 1;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `search_term` | `TEXT` | Literal search substring (trimmed, length 2–80) |
| `$2` | `cursor_created_at` | `TIMESTAMPTZ` | Timestamp cursor (`NULL` for page 1) |
| `$3` | `cursor_id` | `UUID` | UUID cursor (`NULL` for page 1) |
| `$4` | `limit_count` | `INTEGER` | Page size limit |
| `$5` | `viewer_id` | `UUID` | Current viewer UUID |

---

### Use Case 10: Repost Lookup (`get_repost_lookup`)

#### Purpose
Verifies if an author has reposted a specific original post and retrieves the repost metadata along with the original post text and original author handle without storing duplicate text.

#### SQL Statement
```sql
PREPARE get_repost_lookup (uuid, uuid) AS
SELECT
    p.id AS repost_id,
    p.author_id,
    p.repost_of_id,
    p.created_at AS reposted_at,
    orig.id AS original_id,
    orig.text AS original_text,
    orig_u.handle AS original_author_handle
FROM posts p
JOIN posts orig ON orig.id = p.repost_of_id
JOIN users orig_u ON orig_u.id = orig.author_id
WHERE p.kind = 'repost'
  AND p.author_id = $1
  AND p.repost_of_id = $2;
```

#### Parameters
| Param | Name | Type | Description |
|---|---|---|---|
| `$1` | `author_id` | `UUID` | Author UUID of the potential repost |
| `$2` | `original_post_id` | `UUID` | UUID of the original post |

---

## 3. Deep Dive: Pagination Mechanics

### Why `OFFSET` is Avoided
1. **Performance Degradation**: `OFFSET N` requires scanning and discarding $N$ rows, causing $O(N)$ execution cost on deep pagination.
2. **Page Drift / Inconsistency**: Inserting a new post while a user is browsing shifts row offsets, causing items to be duplicated or skipped on page transition.

### The Keyset Tuple Comparison
PostgreSQL natively supports row-wise tuple comparisons:
```sql
(p.created_at, p.id) < ($cursor_created_at, $cursor_id)
```
This expands logically to:
```sql
(p.created_at < $cursor_created_at)
OR (p.created_at = $cursor_created_at AND p.id < $cursor_id)
```
When two posts share the exact millisecond timestamp (such as seeded Posts 10 & 11 at `2026-09-01T10:20:00.000Z`), the unique UUID acts as a tie-breaker. Post 11 (`...1111` > `...1110`) appears on Page 1; its cursor continuation correctly points to Post 10 without skipping or repeating either item.

---

## 4. Deep Dive: Count & Join Safety

### The Cartesian Product Inflation Bug
In naive SQL designs, developers join one-to-many tables directly:
```sql
-- ANTI-PATTERN (DANGEROUS):
SELECT p.id, COUNT(pl.user_id), COUNT(r.id), COUNT(pm.id)
FROM posts p
LEFT JOIN post_likes pl ON pl.post_id = p.id
LEFT JOIN posts r ON r.reply_to_id = p.id
LEFT JOIN post_media pm ON pm.post_id = p.id
GROUP BY p.id;
```
If a post has 3 likes, 2 replies, and 2 images, the query produces $3 \times 2 \times 2 = 12$ joined rows. `COUNT(pl.user_id)` would report **12 likes instead of 3**!

### Our Resolution
We use isolated scalar subqueries:
```sql
(SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
(SELECT COUNT(*) FROM posts r WHERE r.reply_to_id = p.id) AS reply_count
```
Each count is evaluated independently against its foreign key index, ensuring $100\%$ accurate metrics even for posts with multiple images, likes, and replies, and returning `0` for unreacted posts.

---

## 5. Seed Validation Results Summary

The query suite was validated against the deterministic seed dataset (`db/seed.sql`):

| Test Scenario | Fixture Target | Query Executed | Expected & Verified Outcome |
|---|---|---|---|
| **Feed Page 1 & 2 Boundary** | Posts 10 & 11 (Tied `10:20:00.000Z`) | `get_home_feed` (Page 1 & 2) | Page 1 ends on Post 11 (`...1111`). Page 2 starts on Post 10 (`...1110`). Zero duplicates, zero skips. |
| **Zero-Reaction Post** | Post 30 (`...1130`) | `get_post_detail` | `like_count = 0`, `reply_count = 0`, `liked_by_viewer = false`. |
| **Multi-Image Post** | Post 1 (`...1101`) | `get_post_detail` & `get_like_totals` | Exact `like_count = 3` without multiplication from 2 media rows. |
| **Zero-Media User** | `zero_media_user` (`...aa06`) | `get_profile_stats` & `get_profile_media` | Stats return `post_count = 0, follower_count = 0, following_count = 0`. Media returns 0 rows. |
| **Search Wildcard Escaping** | Literal `_` and `%` | `search_posts` | Correctly escapes wildcards, matches literal substring, returns deterministic page results. |
| **Repost Invariant Check** | `yosemite_wanderer` on Post 1 | `get_repost_lookup` | Retrieves existing repost row with original text and author handle. |
