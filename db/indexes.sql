-- ============================================================================
-- Social Feed Additional Workload Indexes (Stage B — Step 5)
-- Target Database: PostgreSQL 16+ (instagram_modeling)
-- Reference: docs/03_Shared_Database_Modeling_PRD.md (Deliverable 5)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Home Feed Keyset Pagination Index
-- Query: get_home_feed (Use Case 1)
-- Predicate: WHERE p.kind = 'original' AND (p.created_at, p.id) < ($1, $2)
-- Ordering: ORDER BY p.created_at DESC, p.id DESC
-- Rationale: A partial B-tree index on original posts perfectly matches the
--            keyset cursor tuple comparison and descending sort order.
--            Excludes replies and reposts to keep the index compact and memory-resident.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_posts_feed_keyset
    ON posts (created_at DESC, id DESC)
    WHERE kind = 'original';


-- ----------------------------------------------------------------------------
-- 2. Direct Replies Keyset Lookup Index
-- Query: get_direct_replies (Use Case 3)
-- Predicate: WHERE r.kind = 'reply' AND r.reply_to_id = $1 AND (r.created_at, r.id) < ($2, $3)
-- Ordering: ORDER BY r.created_at DESC, r.id DESC
-- Rationale: Foreign key index on reply_to_id with composite ordering for
--            instant chronological retrieval of direct replies without in-memory sorting.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_posts_direct_replies
    ON posts (reply_to_id, created_at DESC, id DESC)
    WHERE kind = 'reply';


-- ----------------------------------------------------------------------------
-- 3. Author Originals / Profile Keyset Index
-- Query: get_profile_media (Use Case 4), get_profile_stats (Use Case 5)
-- Predicate: WHERE p.author_id = $1 AND p.kind = 'original'
-- Ordering: ORDER BY p.created_at DESC, p.id DESC
-- Rationale: Accelerates author-specific original post filtering and profile
--            metric calculations without scanning the full posts table.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_posts_author_originals
    ON posts (author_id, created_at DESC, id DESC)
    WHERE kind = 'original';


-- ----------------------------------------------------------------------------
-- 4. Reverse Follow Edge Index (Followers Lookup)
-- Query: get_profile_stats (Use Case 5)
-- Predicate: WHERE f.following_id = u.id (follower_count calculation)
-- Rationale: The primary key `follows_pkey` is on (follower_id, following_id).
--            Lookup by `following_id` alone cannot use the leading PK column efficiently.
--            This index allows fast index-only scans to calculate follower counts.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_follows_following_id
    ON follows (following_id);


-- ----------------------------------------------------------------------------
-- 5. Post Likes Reverse Lookup Index
-- Query: get_like_totals (Use Case 6), get_post_detail (Use Case 2), get_home_feed (Use Case 1)
-- Predicate: WHERE pl.post_id = target.post_id (batch like aggregation & count subqueries)
-- Rationale: The primary key `post_likes_pkey` is on (user_id, post_id).
--            Aggregating likes by `post_id` cannot use the leading user_id column.
--            This index provides fast index-only scans for post like counts.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_post_likes_post_id
    ON post_likes (post_id);
