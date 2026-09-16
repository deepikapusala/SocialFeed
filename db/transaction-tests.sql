-- ============================================================================
-- Social Feed Transaction & Rollback Demonstration (Stage B — Step 5)
-- Target Database: PostgreSQL 16+ (instagram_modeling)
-- Reference: docs/03_Shared_Database_Modeling_PRD.md (Deliverable 5)
-- ============================================================================

-- ============================================================================
-- TEST: Atomic Rollback of Uncommitted Temporary Write
-- Purpose: Proves transaction isolation and rollback guarantee (ACID Atomicity).
--          Ensures no partial write or uncommitted state survives ROLLBACK.
-- ============================================================================

-- 1. Verify that the test record does NOT exist before the test
SELECT count(*) AS count_before
FROM posts
WHERE id = '99999999-9999-4999-8999-999999999999';
-- Expected: 0

-- 2. Begin Transaction Block
BEGIN;

-- 3. Insert isolated test record inside transaction
INSERT INTO posts (
    id,
    author_id,
    kind,
    text,
    created_at
) VALUES (
    '99999999-9999-4999-8999-999999999999',
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
    'original',
    'Temporary transaction rollback test post',
    '2026-09-14 12:00:00.000+00'
);

-- 4. Verify the record is visible inside the active transaction
SELECT id, author_id, kind, text
FROM posts
WHERE id = '99999999-9999-4999-8999-999999999999';
-- Expected: 1 row returned

-- 5. Rollback the transaction
ROLLBACK;

-- 6. Verify that the test record is completely absent after rollback
SELECT count(*) AS count_after_rollback
FROM posts
WHERE id = '99999999-9999-4999-8999-999999999999';
-- Expected: 0 (Atomicity preserved; deterministic seed remains unmodified)
