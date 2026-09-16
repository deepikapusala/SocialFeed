# Seed Manifest — Stage B Deterministic Fixture Dataset

This document details the deterministic seed dataset defined in [`db/seed.sql`](file:///f:/Instagram/db/seed.sql). It records exact row counts, key entities, pagination boundary fixtures, reaction distributions, and verification queries.

---

## 1. Summary of Expected Row Counts

| Table | Logical Subset | Exact Seed Count | Cumulative Rows |
|---|---|---|---|
| **`users`** | Total Registered Accounts | **6** | 6 |
| **`posts`** | Originals (`kind = 'original'`) | **30** | 30 |
| | Direct Replies (`kind = 'reply'`) | **12** | 42 |
| | Reposts (`kind = 'repost'`) | **4** | **46** |
| **`post_media`** | Image Attachments (Originals only) | **10** | 10 |
| **`post_likes`** | Reactions (Originals & Replies) | **15** | 15 |
| **`follows`** | Directional Follow Edges | **8** | 8 |

---

## 2. Seeded Users Directory

| User ID | Handle | Display Name | Role / Fixture Note |
|---|---|---|---|
| `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa` | `asha` | Asha Patel | **Development Demo Identity (`DEMO_USER_ID`)**. Authors 6 originals, likes 4 posts, follows 3 users. |
| `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02` | `yosemite_wanderer` | Marcus Thorne | Outdoor landscape photographer. Authors 6 originals, 3 replies, 1 repost. |
| `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03` | `atelier_canvas` | Elena Rostova | Contemporary oil painter. Authors 6 originals, 3 replies, 1 repost. |
| `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04` | `street_lens` | David Kim | Urban geometry & night photographer. Authors 6 originals, 2 replies, 1 repost. |
| `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05` | `urban_geometry` | Clara Vance | Architectural shadows & forms. Authors 6 originals, 2 replies, 1 repost. |
| `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06` | `zero_media_user` | Jordan Lee | **Edge-case user**. Dedicated 0-post, 0-media, 0-reaction account. |

---

## 3. Deliberate Pagination & Edge-Case Fixtures

### A. Timestamp Tie Boundary (Posts 10 & 11)
- **Post 10 (`11111111-1111-4111-8111-111111111110`)** and **Post 11 (`11111111-1111-4111-8111-111111111111`)** share the exact timestamp:
  `2026-09-01 10:20:00.000+00`
- Under descending total ordering `(created_at DESC, id DESC)`:
  1. Post 11 is sorted before Post 10 (because ID `...1111` > `...1110`).
  2. With default `limit=10`, **Page 1** returns posts 1 through 11 (ending on Post 11).
  3. **Page 2** continuation begins on Post 10 using cursor encoded from `(2026-09-01T10:20:00.000Z, ...1111)`.
  4. Both tied rows are returned deterministically without duplicate emissions or omissions.

### B. Multi-Image Carousel Post (Post 1)
- **Post 1 (`11111111-1111-4111-8111-111111111101`)** owns **2 media rows**:
  - `bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01` (`position = 0`, 1200×800)
  - `bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb02` (`position = 1`, 1200×800)
- Exercises multi-image carousel display and `UNIQUE (post_id, position)`.

### C. Zero-Reaction Post (Post 30)
- **Post 30 (`11111111-1111-4111-8111-111111111130`)** has **0 likes** and **0 replies**.
- Exercises `LEFT JOIN` and aggregate query behavior for non-zero vs zero-count posts.

---

## 4. Reaction & Follow Distributions

### Authoritative Like Counts
- **Post 1 (`...1101`)**: **3 likes** (`asha`, `yosemite_wanderer`, `atelier_canvas`).
- **Post 2 (`...1102`)**: **3 likes** (`asha`, `street_lens`, `urban_geometry`).
- **Post 3 (`...1103`)**: **1 like** (`asha`).
- **Post 4 (`...1104`)**: **1 like** (`asha`).
- **Post 5 (`...1105`)**: **1 like** (`yosemite_wanderer`).
- **Post 6 (`...1106`)**: **1 like** (`atelier_canvas`).
- **Post 7 (`...1107`)**: **1 like** (`street_lens`).
- **Post 8 (`...1108`)**: **1 like** (`urban_geometry`).
- **Reply 1 (`...2201`)**: **2 likes** (`asha`, `yosemite_wanderer`).
- **Reply 2 (`...2202`)**: **1 like** (`atelier_canvas`).

### Authoritative Follow Graph
- **`asha` following (3)**: `yosemite_wanderer`, `atelier_canvas`, `street_lens`.
- **`asha` followers (2)**: `yosemite_wanderer`, `atelier_canvas`.

---

## 5. How to Execute & Verify Against an Isolated Database

> **Safety Notice:** Never execute against existing production or `student` databases. Always use a dedicated isolated modeling database (e.g. `instagram_modeling`).

### Execution via `psql`
```bash
# 1. Create dedicated isolated modeling database
createdb -U postgres instagram_modeling

# 2. Execute schema DDL
psql -U postgres -d instagram_modeling -f db/schema.sql

# 3. Execute deterministic seed
psql -U postgres -d instagram_modeling -f db/seed.sql
```

### Verification Query Suite
```sql
-- 1. Verify Entity Row Counts
SELECT 'users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'posts_total', COUNT(*) FROM posts
UNION ALL
SELECT 'posts_originals', COUNT(*) FROM posts WHERE kind = 'original'
UNION ALL
SELECT 'posts_replies', COUNT(*) FROM posts WHERE kind = 'reply'
UNION ALL
SELECT 'posts_reposts', COUNT(*) FROM posts WHERE kind = 'repost'
UNION ALL
SELECT 'post_media', COUNT(*) FROM post_media
UNION ALL
SELECT 'post_likes', COUNT(*) FROM post_likes
UNION ALL
SELECT 'follows', COUNT(*) FROM follows;

-- Expected Output:
-- table_name       | count
-- -----------------+-------
-- users            |     6
-- posts_total      |    46
-- posts_originals  |    30
-- posts_replies    |    12
-- posts_reposts    |     4
-- post_media       |    10
-- post_likes       |    15
-- follows          |     8
```
