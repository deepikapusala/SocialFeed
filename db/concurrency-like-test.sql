-- ============================================================================
-- Social Feed Concurrent Duplicate-Like Test Script (Stage B — Step 5)
-- Target Database: PostgreSQL 16+ (instagram_modeling)
-- Reference: docs/03_Shared_Database_Modeling_PRD.md (Deliverable 5)
-- ============================================================================

-- Fixture Pair:
--   user_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06' (zero_media_user)
--   post_id: '11111111-1111-4111-8111-111111111130' (Post 30 - 0 likes seeded)

-- ----------------------------------------------------------------------------
-- STEP 0: Initial State Check
-- ----------------------------------------------------------------------------
SELECT COUNT(*) AS initial_like_count
FROM post_likes
WHERE user_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06'
  AND post_id = '11111111-1111-4111-8111-111111111130';
-- Expected: 0

-- ----------------------------------------------------------------------------
-- CONCURRENT SESSION SIMULATION
-- ----------------------------------------------------------------------------

-- [SESSION 1] Starts transaction and inserts the like edge
BEGIN;
INSERT INTO post_likes (user_id, post_id, created_at)
VALUES (
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06',
    '11111111-1111-4111-8111-111111111130',
    '2026-09-14 12:00:00.000+00'
);

-- [SESSION 2] Concurrently attempts to insert the identical like edge
-- In a real concurrent session, Session 2 executes:
-- BEGIN;
-- INSERT INTO post_likes (user_id, post_id, created_at)
-- VALUES (
--     'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06',
--     '11111111-1111-4111-8111-111111111130',
--     '2026-09-14 12:00:00.000+00'
-- );
-- Outcome: Session 2 blocks until Session 1 commits.

-- [SESSION 1] Commits successfully
COMMIT;

-- [SESSION 2] Immediately unblocks and fails with:
-- ERROR: duplicate key value violates unique constraint "post_likes_pkey"
-- DETAIL: Key (user_id, post_id)=(aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06, 11111111-1111-4111-8111-111111111130) already exists.
-- ROLLBACK;

-- ----------------------------------------------------------------------------
-- STEP 3: Verification & Cleanup
-- ----------------------------------------------------------------------------
-- Verify exactly 1 like row exists in total
SELECT COUNT(*) AS final_like_count
FROM post_likes
WHERE user_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06'
  AND post_id = '11111111-1111-4111-8111-111111111130';
-- Expected: 1

-- Clean up the test row to preserve deterministic seed integrity
DELETE FROM post_likes
WHERE user_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06'
  AND post_id = '11111111-1111-4111-8111-111111111130';
