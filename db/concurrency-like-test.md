# Concurrent Duplicate-Like Test (Stage B — Step 5)

This document describes the concurrency test protocol for concurrent duplicate likes on [`post_likes`](file:///f:/Instagram/db/schema.sql) in the **Social Feed** schema.

---

## 1. Objective

Demonstrate that when two client sessions concurrently attempt to like the same post (`user_id`, `post_id`), PostgreSQL's primary key constraint (`post_likes_pkey`) and row-level locking prevent race conditions, ensuring that:
1. Exactly one transaction successfully inserts the like edge.
2. The concurrent transaction is rejected with a unique constraint violation (`23505: unique_violation`).
3. The database state remains consistent with exactly one like record.

---

## 2. Test Fixture Setup

- **User**: `zero_media_user` (`aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06`)
- **Target Post**: Post 30 (`11111111-1111-4111-8111-111111111130`) (seeded with 0 likes)

---

## 3. Two-Session Concurrency Protocol

```
    SESSION A (Connection 1)                      SESSION B (Connection 2)
              │                                             │
      1. BEGIN;                                     2. BEGIN;
              │                                             │
      3. INSERT INTO post_likes                     │
         (user_id, post_id, created_at)             │
         VALUES (...06, ...30, NOW());              │
         [OK - row inserted in Tx A]                │
              │                                             │
              │                                     4. INSERT INTO post_likes
              │                                        (user_id, post_id, created_at)
              │                                        VALUES (...06, ...30, NOW());
              │                                        [BLOCKS: Waiting on Tx A lock]
              │                                             │
      5. COMMIT;                                            │
         [Tx A Committed]                                   │
              │                                             ▼
              │                                     6. [UNBLOCKS with ERROR]:
              │                                        ERROR: duplicate key value violates
              │                                        unique constraint "post_likes_pkey"
              │                                        DETAIL: Key (user_id, post_id)=
              │                                        (...06, ...30) already exists.
              │                                             │
              │                                     7. ROLLBACK;
              ▼                                             ▼
                               8. VERIFICATION:
                SELECT COUNT(*) FROM post_likes WHERE ...;
                               [Result = 1]
```

---

## 4. Execution Step Details

### Session A
```sql
BEGIN;
INSERT INTO post_likes (user_id, post_id, created_at)
VALUES (
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06',
    '11111111-1111-4111-8111-111111111130',
    '2026-09-14 12:00:00.000+00'
);
```
*Status: Row inserted in transaction A buffer, row lock held on `post_likes_pkey` entry.*

### Session B
```sql
BEGIN;
INSERT INTO post_likes (user_id, post_id, created_at)
VALUES (
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06',
    '11111111-1111-4111-8111-111111111130',
    '2026-09-14 12:00:00.000+00'
);
```
*Status: PostgreSQL index lock detects the uncommitted entry on `post_likes_pkey` and places Session B into a wait state (`LockWait`).*

### Session A
```sql
COMMIT;
```
*Status: Transaction A commits to the WAL and table.*

### Session B
*Status: Session B unblocks immediately and encounters:*
```
ERROR: duplicate key value violates unique constraint "post_likes_pkey"
DETAIL: Key (user_id, post_id)=(aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06, 11111111-1111-4111-8111-111111111130) already exists.
```
Session B terminates with `ROLLBACK`.

---

## 5. Post-Test Verification & Seed Isolation

```sql
SELECT COUNT(*) FROM post_likes
WHERE user_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06'
  AND post_id = '11111111-1111-4111-8111-111111111130';
-- Result: 1 (Exactly 1 like created)
```

The test row is then deleted to maintain deterministic seed count parity (15 total likes).
