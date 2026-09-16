-- ============================================================================
-- Social Feed Constraint Validation Test Suite (Stage B)
-- Target Engine: PostgreSQL 16+
-- Reference: docs/decisions.md (Section 15)
--
-- DESIGN RULE:
-- Each test executes within an isolated PL/pgSQL block with explicit exception
-- handling. Expected constraint violations (23505, 23503, 23514) are caught,
-- verified, and rolled back safely so no permanent invalid rows survive.
-- ============================================================================

\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    passed_count INTEGER := 0;
    failed_count INTEGER := 0;
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'STARTING STAGE B DATABASE CONSTRAINT VALIDATION TESTS';
    RAISE NOTICE '============================================================';

    -- ------------------------------------------------------------------------
    -- Test 1: Duplicate Handle Rejection (users_handle_unique)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO users (id, handle, display_name, created_at)
        VALUES ('99999999-9999-4999-8999-999999999901', 'asha', 'Duplicate Asha', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 1 FAILED: Duplicate handle was unexpectedly accepted';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Test 1 PASSED: Duplicate handle rejected with unique_violation (23505)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 2: Orphan Author Rejection (posts.author_id FK)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO posts (id, author_id, kind, text, created_at)
        VALUES ('99999999-9999-4999-8999-999999999902', '00000000-0000-4000-8000-000000000000', 'original', 'Test text', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 2 FAILED: Orphan author was unexpectedly accepted';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Test 2 PASSED: Orphan author rejected with foreign_key_violation (23503)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 3: Orphan Media Rejection (post_media.post_id FK)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO post_media (id, post_id, position, alt_text, width, height, small_url, large_url, created_at)
        VALUES ('99999999-9999-4999-8999-999999999903', '00000000-0000-4000-8000-000000000000', 0, 'Alt', 800, 600, 'http://s', 'http://l', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 3 FAILED: Orphan media was unexpectedly accepted';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Test 3 PASSED: Orphan media rejected with foreign_key_violation (23503)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 4: Orphan Like Rejection (post_likes.user_id / post_id FK)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO post_likes (user_id, post_id, created_at)
        VALUES ('00000000-0000-4000-8000-000000000000', '11111111-1111-4111-8111-111111111101', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 4 FAILED: Orphan like was unexpectedly accepted';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Test 4 PASSED: Orphan like rejected with foreign_key_violation (23503)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 5: Orphan Follow Rejection (follows.follower_id / following_id FK)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO follows (follower_id, following_id, created_at)
        VALUES ('00000000-0000-4000-8000-000000000000', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 5 FAILED: Orphan follow was unexpectedly accepted';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Test 5 PASSED: Orphan follow rejected with foreign_key_violation (23503)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 6: Duplicate Like Rejection (post_likes PRIMARY KEY)
    -- ------------------------------------------------------------------------
    BEGIN
        -- 'asha' already likes post #1 in seed.sql
        INSERT INTO post_likes (user_id, post_id, created_at)
        VALUES ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-1111-4111-8111-111111111101', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 6 FAILED: Duplicate like was unexpectedly accepted';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Test 6 PASSED: Duplicate like rejected with unique_violation (23505)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 7: Duplicate Follow Rejection (follows PRIMARY KEY)
    -- ------------------------------------------------------------------------
    BEGIN
        -- 'asha' already follows 'yosemite_wanderer' in seed.sql
        INSERT INTO follows (follower_id, following_id, created_at)
        VALUES ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 7 FAILED: Duplicate follow was unexpectedly accepted';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Test 7 PASSED: Duplicate follow rejected with unique_violation (23505)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 8: Self-Follow Rejection (follows_no_self_follow_check)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO follows (follower_id, following_id, created_at)
        VALUES ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 8 FAILED: Self-follow was unexpectedly accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Test 8 PASSED: Self-follow rejected with check_violation (23514)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 9: Duplicate Repost Rejection (posts_author_repost_unique)
    -- ------------------------------------------------------------------------
    BEGIN
        -- 'yosemite_wanderer' already reposted post #1 in seed.sql
        INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at)
        VALUES ('99999999-9999-4999-8999-999999999909', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'repost', NULL, NULL, '11111111-1111-4111-8111-111111111101', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 9 FAILED: Duplicate repost was unexpectedly accepted';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Test 9 PASSED: Duplicate repost rejected with unique_violation (23505)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 10: Invalid Post Kind Combination (posts_kind_attributes_check)
    -- ------------------------------------------------------------------------
    BEGIN
        -- Original post with an invalid reply_to_id reference
        INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at)
        VALUES ('99999999-9999-4999-8999-999999999910', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Illegal original', '11111111-1111-4111-8111-111111111101', NULL, CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 10 FAILED: Invalid post kind attributes accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Test 10 PASSED: Invalid post kind attributes rejected with check_violation (23514)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 11: Invalid Media Position (post_media_position_check)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO post_media (id, post_id, position, alt_text, width, height, small_url, large_url, created_at)
        VALUES ('99999999-9999-4999-8999-999999999911', '11111111-1111-4111-8111-111111111101', 4, 'Invalid slot 4', 800, 600, 'http://s', 'http://l', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 11 FAILED: Media position 4 was unexpectedly accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Test 11 PASSED: Media position 4 rejected with check_violation (23514)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 12: Duplicate Media Position on Same Post (post_media_post_position_unique)
    -- ------------------------------------------------------------------------
    BEGIN
        -- Post #1 already has media at position 0
        INSERT INTO post_media (id, post_id, position, alt_text, width, height, small_url, large_url, created_at)
        VALUES ('99999999-9999-4999-8999-999999999912', '11111111-1111-4111-8111-111111111101', 0, 'Duplicate slot 0', 800, 600, 'http://s', 'http://l', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 12 FAILED: Duplicate media position was unexpectedly accepted';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Test 12 PASSED: Duplicate media position rejected with unique_violation (23505)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 13: Invalid Image Dimensions (post_media_dimensions_check)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO post_media (id, post_id, position, alt_text, width, height, small_url, large_url, created_at)
        VALUES ('99999999-9999-4999-8999-999999999913', '11111111-1111-4111-8111-111111111101', 2, 'Zero width', 0, 600, 'http://s', 'http://l', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 13 FAILED: Zero width dimension was unexpectedly accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Test 13 PASSED: Zero width dimension rejected with check_violation (23514)';
            passed_count := passed_count + 1;
    END;

    -- ------------------------------------------------------------------------
    -- Test 14: Invalid Stored Text Length (posts_text_length_check)
    -- ------------------------------------------------------------------------
    BEGIN
        INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at)
        VALUES ('99999999-9999-4999-8999-999999999914', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', '   ', NULL, NULL, CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Test 14 FAILED: Whitespace-only empty text was unexpectedly accepted';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Test 14 PASSED: Empty/whitespace text rejected with check_violation (23514)';
            passed_count := passed_count + 1;
    END;

    RAISE NOTICE '============================================================';
    RAISE NOTICE 'ALL 14 DATABASE CONSTRAINT TESTS PASSED (%/14)', passed_count;
    RAISE NOTICE '============================================================';
END $$;

-- ----------------------------------------------------------------------------
-- NOTE ON SERVICE-ONLY RULES (Intentionally NOT Tested via Database DDL Checks)
-- ----------------------------------------------------------------------------
-- 1. Reply target must be an original post (422 Unprocessable Entity).
-- 2. Repost target must be an original post (422 Unprocessable Entity).
-- 3. Media items belong only to original posts (422 Unprocessable Entity).
-- 4. Likes on repost rows are rejected (422 Unprocessable Entity).
-- 5. Maximum 4 media upload batch size (422 Unprocessable Entity).
--
-- These rules require looking at referenced rows across relations or counting
-- input collections, and are enforced by the application service layer.
-- ----------------------------------------------------------------------------

ROLLBACK;
