-- ============================================================================
-- Social Feed Parameterized SQL Use Cases (Stage B)
-- Target Database: PostgreSQL 16+
-- Reference: docs/03_Shared_Database_Modeling_PRD.md (Deliverable 4)
-- ============================================================================

-- ============================================================================
-- 1. HOME FEED (Core Public Feed of Original Posts)
-- Purpose: Returns newest original posts across all users with author info,
--          accurate reaction/reply counts, and viewer reaction state.
-- Ordering: (created_at DESC, id DESC) total ordering.
-- Keyset Pagination: (p.created_at, p.id) < ($1, $2). Fetches limit + 1.
-- Parameters:
--   $1: cursor_created_at TIMESTAMPTZ(3) (NULL for Page 1)
--   $2: cursor_id         UUID           (NULL for Page 1)
--   $3: limit_count       INTEGER        (Page size, e.g. 10)
--   $4: viewer_id         UUID           (Current viewer UUID)
-- ============================================================================
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


-- ============================================================================
-- 2. POST DETAIL
-- Purpose: Returns complete details for a single post by UUID, including author,
--          accurate reaction/reply counts, viewer state, and referenced content.
-- Parameters:
--   $1: post_id   UUID (Post UUID to retrieve)
--   $2: viewer_id UUID (Current viewer UUID)
-- ============================================================================
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


-- ============================================================================
-- 3. DIRECT REPLIES
-- Purpose: Returns chronological direct replies for a given original post ID.
--          Does not return replies to replies (single-level hierarchy).
-- Parameters:
--   $1: parent_post_id    UUID
--   $2: cursor_created_at TIMESTAMPTZ(3) (NULL for Page 1)
--   $3: cursor_id         UUID           (NULL for Page 1)
--   $4: limit_count       INTEGER
--   $5: viewer_id         UUID
-- ============================================================================
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


-- ============================================================================
-- 4. PROFILE MEDIA
-- Purpose: Returns ordered image attachments for a user's original posts.
-- Parameters:
--   $1: user_id           UUID
--   $2: cursor_created_at TIMESTAMPTZ(3) (NULL for Page 1)
--   $3: cursor_id         UUID           (NULL for Page 1)
--   $4: limit_count       INTEGER
-- ============================================================================
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


-- ============================================================================
-- 5. PROFILE STATS
-- Purpose: Returns authoritative profile statistics without count inflation.
-- Parameters:
--   $1: user_id UUID
-- ============================================================================
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


-- ============================================================================
-- 6. LIKE TOTALS (Batch Reaction Aggregation)
-- Purpose: Computes like counts for an arbitrary batch of post IDs.
-- Parameters:
--   $1: post_ids UUID[] (Array of post UUIDs)
-- ============================================================================
PREPARE get_like_totals (uuid[]) AS
SELECT
    target.post_id,
    COUNT(pl.user_id) AS like_count
FROM unnest($1) AS target(post_id)
LEFT JOIN post_likes pl ON pl.post_id = target.post_id
GROUP BY target.post_id;


-- ============================================================================
-- 7. VIEWER STATE (Batch Viewer Reaction Check)
-- Purpose: Determines whether a viewer has liked each post in a batch.
-- Parameters:
--   $1: viewer_id UUID
--   $2: post_ids  UUID[]
-- ============================================================================
PREPARE get_viewer_state (uuid, uuid[]) AS
SELECT
    target.post_id,
    (pl.user_id IS NOT NULL) AS liked_by_viewer
FROM unnest($2) AS target(post_id)
LEFT JOIN post_likes pl ON pl.post_id = target.post_id AND pl.user_id = $1;


-- ============================================================================
-- 8. FOLLOWING FEED EXERCISE
-- Purpose: Returns original posts authored by users followed by the viewer.
-- Parameters:
--   $1: viewer_id         UUID
--   $2: cursor_created_at TIMESTAMPTZ(3) (NULL for Page 1)
--   $3: cursor_id         UUID           (NULL for Page 1)
--   $4: limit_count       INTEGER
-- ============================================================================
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


-- ============================================================================
-- 9. SEARCH (Case-Insensitive Substring Match on Originals)
-- Purpose: Case-insensitive literal substring search on original post text.
--          Escapes SQL wildcard characters ('%' and '_') to treat input literally.
-- Parameters:
--   $1: search_term       TEXT
--   $2: cursor_created_at TIMESTAMPTZ(3) (NULL for Page 1)
--   $3: cursor_id         UUID           (NULL for Page 1)
--   $4: limit_count       INTEGER
--   $5: viewer_id         UUID
-- ============================================================================
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


-- ============================================================================
-- 10. REPOST LOOKUP
-- Purpose: Checks if an author has reposted an original and retrieves details.
-- Parameters:
--   $1: author_id        UUID
--   $2: original_post_id UUID
-- ============================================================================
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
