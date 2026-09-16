# Relational Design Decisions, Constraints & Normalization — Stage B

This document records the complete architectural, constraint enforcement, and normalization evidence for the **Social Feed** relational model (Stage B Step 2). It establishes the exact division of responsibilities between **Database Enforcements**, **Service Enforcements**, and **Both**.

---

## 1. Selected Physical Model vs. Alternative Models

### Selected Model: Single Unified `posts` Table with Discriminator
All social publications and interaction items are stored in a single table `posts` with a discriminator column `kind` (`'original'`, `'reply'`, `'repost'`) and self-referencing foreign keys `reply_to_id` and `repost_of_id`.

```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    kind VARCHAR(10) NOT NULL CHECK (kind IN ('original', 'reply', 'repost')),
    text VARCHAR(280),
    reply_to_id UUID REFERENCES posts(id) ON DELETE RESTRICT,
    repost_of_id UUID REFERENCES posts(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Alternative Model Considered: Concrete Table Inheritance (Separate Tables)
- **Architecture:** Three distinct tables: `original_posts`, `replies` (referencing `original_posts(id)`), and `reposts` (referencing `original_posts(id)` and `users(id)`).
- **Advantages:**
  - Strict foreign key typing: `replies.reply_to_id` and `reposts.repost_of_id` would point specifically to `original_posts(id)`, guaranteeing at the database schema level that target posts are originals without service-level kind checks.
  - No conditional column nullability (e.g. `text` is NOT NULL on `original_posts` and `replies`, and absent on `reposts`).
- **Disadvantages:**
  - **Polymorphic Foreign Keys for Reactions:** The `post_likes` table would need either three separate nullable foreign keys (`original_post_id`, `reply_id`, `repost_id`), multiple distinct like tables, or generic object IDs, which fragments schema integrity and violates 3NF.
  - **Query Fragmentation:** Fetching single post details (`GET /posts/{id}`) or user activity timelines would require complex `UNION ALL` queries across three tables.
  - **Feed Pagination Complexity:** Building unified feeds or searching content across posts would require cross-table joins and merged cursor sorts.
- **Why the Unified Model Was Chosen:**
  The unified `posts` table provides clean foreign key targets for reactions (`post_likes.post_id REFERENCES posts(id)`), single-table detail lookups (`GET /posts/{id}`), uniform pagination, and direct alignment with the shared API wire contract.

---

## 2. Unique Normalized User Handle

### Rule Definition
- User handles must be unique, non-empty, lowercase, 1–30 characters, and match alphanumeric/underscore format (`^[a-z0-9_]+$`).
- Duplicate handles (including case-insensitive collisions) must be strictly rejected.

### Division of Enforcement
- **DATABASE-ENFORCED:**
  - Unique index: `UNIQUE (handle)`.
  - Format constraint: `CHECK (handle = lower(handle) AND length(trim(handle)) >= 1 AND handle ~ '^[a-z0-9_]+$')`.
- **SERVICE-ENFORCED:**
  - Application services normalize incoming handles to lowercase and trim surrounding whitespace prior to SQL execution.

### Examples
- **Valid:** `'asha'`, `'yosemite_wanderer'`, `'user_123'`
- **Invalid Format (DB Rejection):** `'Asha'` (uppercase), `'user name'` (spaces), `'@handle'` (invalid character), `''` (empty)
- **Duplicate Collision (DB Rejection):** Inserting `'asha'` when `'asha'` already exists raises `unique_violation` (PostgreSQL error `23505`).

---

## 3. Foreign Key & Referential Integrity

### Foreign Key Inventory
| Foreign Key Column | Target Table & Column | `ON DELETE` Action | Relational Purpose |
|---|---|---|---|
| `posts.author_id` | `users(id)` | `RESTRICT` | Every post must have an active, existing author. |
| `posts.reply_to_id` | `posts(id)` | `RESTRICT` | Direct replies must reference an existing parent post. |
| `posts.repost_of_id` | `posts(id)` | `RESTRICT` | Reposts must reference an existing original post. |
| `post_media.post_id` | `posts(id)` | `CASCADE` | Media attachments belong to the parent post; deleted with parent. |
| `post_likes.user_id` | `users(id)` | `CASCADE` | Reactions are tied to an active user; cleaned up if user is deleted. |
| `post_likes.post_id` | `posts(id)` | `CASCADE` | Reactions belong to an active post; cleaned up if post is deleted. |
| `follows.follower_id` | `users(id)` | `CASCADE` | Outgoing follow edges originate from an active user. |
| `follows.following_id` | `users(id)` | `CASCADE` | Incoming follow edges target an active user. |

### What Foreign Keys Guarantee vs. What They Do NOT Guarantee
- **What Foreign Keys Guarantee (DATABASE):**
  - **Referential Existence:** The referenced row strictly exists at the time of insertion/update.
  - **Orphan Prevention:** Prevents creating posts, likes, media, or follows referencing non-existent IDs.
- **What Foreign Keys Do NOT Guarantee (Requires SERVICE Enforcement):**
  - **Target Kind:** An FK on `posts.reply_to_id` or `posts.repost_of_id` ensures the target post exists, but **cannot** verify that the target has `kind = 'original'` rather than `'reply'` or `'repost'`.
  - **Single-Level Depth:** An FK cannot prevent replies-to-replies (e.g. referencing another reply).
  - **Sibling Collection Size:** An FK on `post_media.post_id` cannot limit the total count of media rows for a post to at most 4.

---

## 4. Like Uniqueness & Reaction Integrity

### Rule Definition
- A user can like a given original post or reply at most once.
- Liking a repost row is rejected.
- Repeated like/unlike operations must be idempotent and retry-safe.

### Division of Enforcement
- **DATABASE-ENFORCED:**
  - Composite Primary Key: `PRIMARY KEY (user_id, post_id)` on `post_likes`.
  - Prevents duplicate reaction rows even under high-concurrency race conditions.
- **SERVICE-ENFORCED:**
  - Service verifies that the target post is an `'original'` or `'reply'`, rejecting likes on `'repost'` rows with `422 Unprocessable Entity`.
  - Reconciles idempotent retries: repeated likes maintain `likedByViewer: true` without raising errors to the client.

### Authoritative Counts vs. Stored Counters
- Total likes (`likeCount`) are computed dynamically via indexed SQL aggregate query:
  ```sql
  SELECT COUNT(*) FROM post_likes WHERE post_id = $1;
  ```
- Viewer reaction status (`likedByViewer`) is computed via:
  ```sql
  SELECT EXISTS(SELECT 1 FROM post_likes WHERE post_id = $1 AND user_id = $viewer_id);
  ```
- **Rationale:** Storing a scalar `like_count` column on `posts` risks count drift under concurrent writes, retries, and transaction rollbacks. Relational aggregation ensures authoritative counts.

---

## 5. Follow Graph & Self-Follow Prevention

### Rule Definition
- Follows are directional (`follower_id` follows `following_id`).
- Duplicate follow edges between the same pair are rejected.
- Self-follows (`follower_id = following_id`) are strictly prohibited.

### Division of Enforcement
- **DATABASE-ENFORCED:**
  - Composite Primary Key: `PRIMARY KEY (follower_id, following_id)`.
  - Self-Follow Constraint: `CHECK (follower_id <> following_id)`.
- **SERVICE-ENFORCED:**
  - Application checks prevent attempting self-follow at the API layer.

### Examples
- **Valid:** User A follows User B `(UUID_A, UUID_B)`.
- **Directional Pair:** User B follows User A `(UUID_B, UUID_A)` is a distinct, valid row.
- **Duplicate Attempt (DB Rejection):** Inserting `(UUID_A, UUID_B)` twice triggers `unique_violation` (error `23505`).
- **Self-Follow Attempt (DB Rejection):** Inserting `(UUID_A, UUID_A)` triggers `check_violation` (error `23514`).

---

## 6. Post Text & Length Rules

### Rule Definition
- Post text must be trimmed of leading/trailing whitespace and contain 1 to 280 Unicode code points.
- Originals and replies require text; reposts must have `text IS NULL`.

### Division of Enforcement
- **SERVICE-ENFORCED:**
  - Whitespace trimming: The service trims incoming raw strings (`text.strip()`).
  - Code point length validation: Pydantic schemas validate `1 <= len(trimmed_text) <= 280`.
- **DATABASE-ENFORCED:**
  - Stored Value Integrity: `CHECK (text IS NULL OR length(trim(text)) BETWEEN 1 AND 280)`.
  - Ensures no empty whitespace-only strings (`''` or `'   '`) or strings exceeding 280 characters can be inserted directly via SQL.

---

## 7. Post Kind & Column Combinations

### Permitted Column Matrix
| `kind` | `text` | `reply_to_id` | `repost_of_id` | Owned `post_media` Allowed? |
|---|---|---|---|---|
| `'original'` | **NOT NULL** (1–280 chars) | **NULL** | **NULL** | Yes (0 to 4 rows) |
| `'reply'` | **NOT NULL** (1–280 chars) | **NOT NULL** (references parent) | **NULL** | No (0 rows) |
| `'repost'` | **NULL** (no new text) | **NULL** | **NOT NULL** (references original) | No (0 rows) |

### Table-Level CHECK Constraint on `posts`
```sql
CHECK (
  (kind = 'original' AND text IS NOT NULL AND reply_to_id IS NULL AND repost_of_id IS NULL) OR
  (kind = 'reply'    AND text IS NOT NULL AND reply_to_id IS NOT NULL AND repost_of_id IS NULL) OR
  (kind = 'repost'   AND text IS NULL     AND reply_to_id IS NULL AND repost_of_id IS NOT NULL)
)
```

---

## 8. Reply and Repost Target Validation Strategy

### Problem Statement
A foreign key constraint `posts.reply_to_id REFERENCES posts(id)` guarantees that the referenced parent post exists. However, standard SQL foreign keys cannot inspect attributes on the referenced row to verify that `target.kind = 'original'`.

### Enforcement Strategy (SERVICE-ENFORCED)
1. **Target Kind Check:**
   - When creating a reply or repost, the application service executes a lookup on the target `post_id`.
   - If `target.kind != 'original'`, the request is rejected with `422 Unprocessable Entity`.
2. **Single-Level Reply Depth:**
   - Replies targeting another reply (`target.kind == 'reply'`) are rejected.
3. **Repost of Repost Rejection:**
   - Reposts targeting another repost (`target.kind == 'repost'`) are rejected.
4. **Summary:**
   - Target **existence** is **DATABASE-ENFORCED** via Foreign Key.
   - Target **eligibility/kind** is **SERVICE-ENFORCED** via transactional validation.

---

## 9. Duplicate Repost Prevention

### Rule Definition
A user can repost a particular original post at most once.

### Enforcement Mechanism (DATABASE-ENFORCED)
```sql
UNIQUE (author_id, repost_of_id)
```
- **Behavior:**
  - For `original` and `reply` posts, `repost_of_id` is `NULL`. In PostgreSQL, standard unique constraints treat multiple `NULL` values as distinct, so multiple originals/replies by the same author do not conflict.
  - For `repost` posts, `(author_id, repost_of_id)` contains non-null UUID pairs. Attempting to insert a duplicate repost for the same author and target original triggers a unique constraint violation (`23505`), returning `409 Conflict`.

---

## 10. Post Media Constraints & Ordering

### Rule Inventory
1. **Belongs Only to Originals:** Media items belong strictly to original posts. (Enforced by service on insert; foreign key cascade on parent delete).
2. **Display Ordering (`position`):** `position SMALLINT` defines carousel display order.
   - `CHECK (position >= 0 AND position <= 3)` restricts positions to values 0, 1, 2, or 3.
   - `UNIQUE (post_id, position)` prevents multiple images from occupying the same slot.
3. **Maximum 4 Media Items per Original (Honest Relational Boundary):**
   - **Database Constraint:** `position BETWEEN 0 AND 3` together with `UNIQUE (post_id, position)` ensures at most 4 distinct media items can ever be attached to a post.
   - **Service Validation:** The service validates that batch upload payloads contain at most 4 items before executing inserts.
   - *Note:* A standard SQL table-level `CHECK` constraint on `post_media` cannot count sibling rows. Combining bounded position checks with service batch validation solves this completely.
4. **Asset Metadata Integrity:**
   - `CHECK (width > 0 AND height > 0)`: Enforces positive pixel dimensions.
   - `CHECK (length(trim(alt_text)) >= 1)`: Enforces non-empty accessibility descriptions.
   - `CHECK (length(trim(small_url)) > 0 AND length(trim(large_url)) > 0)`: Enforces non-empty asset URLs.

---

## 11. Authoritative Derived Counts

All counts displayed across feed and profile screens are computed dynamically from relational tables:

| Metric | API Field | Relational Source Query |
|---|---|---|
| **Post Likes** | `likeCount` | `SELECT COUNT(*) FROM post_likes WHERE post_id = $1` |
| **Post Direct Replies** | `replyCount` | `SELECT COUNT(*) FROM posts WHERE reply_to_id = $1` |
| **User Originals** | `postCount` | `SELECT COUNT(*) FROM posts WHERE author_id = $1 AND kind = 'original'` |
| **User Followers** | `followerCount` | `SELECT COUNT(*) FROM follows WHERE following_id = $1` |
| **User Following** | `followingCount` | `SELECT COUNT(*) FROM follows WHERE follower_id = $1` |

---

## 12. Normalization Proof (1NF, 2NF, 3NF)

### First Normal Form (1NF)
- **Condition:** All column values are atomic; no repeating groups, arrays, or comma-separated lists.
- **Verification:**
  - Likes are stored in `post_likes` association rows, not in a JSON array or comma-separated string on `posts`.
  - Followers are stored in `follows` association rows, not as an array on `users`.
  - Media attachments are stored as discrete rows in `post_media`.

### Second Normal Form (2NF)
- **Condition:** Must be in 1NF and all non-key attributes are fully dependent on the primary key (no partial key dependencies).
- **Verification:**
  - In `post_likes(user_id, post_id)`: The only non-key attribute is `created_at`, which represents the timestamp of the specific user-post interaction and depends on the entire composite key `(user_id, post_id)`.
  - In `follows(follower_id, following_id)`: `created_at` represents when the specific relationship was formed and depends on the entire composite key.

### Third Normal Form (3NF)
- **Condition:** Must be in 2NF and contain no transitive dependencies (non-key attributes depend solely on the primary key, not on other non-key attributes).
- **Verification:**
  - `posts` references `author_id`. Author metadata (`handle`, `display_name`, `avatar_small_url`, `avatar_large_url`) is stored strictly in `users` and **never copied** onto `posts`. Updating a user's handle or avatar updates exactly one row in `users`.
  - Reposts store only `repost_of_id`. Reposts **never duplicate** the original post's text, author, or media rows.
  - Counts (`likeCount`, `replyCount`, `followerCount`) are derived dynamically and not stored as redundant scalar columns.

---

## 13. `ON DELETE` Policies & Referential Behavior

| Foreign Key | Policy | Behavior on Deletion of Referenced Row |
|---|---|---|
| `posts.author_id` → `users.id` | **`RESTRICT`** | Rejects deleting a user if they have authored active posts. Prevents orphan posts. |
| `posts.reply_to_id` → `posts.id` | **`RESTRICT`** | Rejects deleting an original post if direct replies exist, preserving discussion thread history. |
| `posts.repost_of_id` → `posts.id` | **`RESTRICT`** | Rejects deleting an original post while repost references exist. |
| `post_media.post_id` → `posts.id` | **`CASCADE`** | Deleting an original post automatically removes all associated media attachments. |
| `post_likes.user_id` → `users.id` | **`CASCADE`** | Deleting a user account cleans up all reactions they submitted. |
| `post_likes.post_id` → `posts.id` | **`CASCADE`** | Deleting a post cleans up all likes attached to it. |
| `follows.follower_id` → `users.id` | **`CASCADE`** | Deleting a user cleans up all outgoing follow edges. |
| `follows.following_id` → `users.id` | **`CASCADE`** | Deleting a user cleans up all incoming follow edges targeting them. |

---

## 14. Constraint & Enforcement Matrix

| Product Rule | Database Enforcement | Service Enforcement | Classification | Evidence / Verification Method |
|---|---|---|---|---|
| **Unique normalized handle** | `UNIQUE (handle)`, `CHECK (handle = lower(handle) AND handle ~ '^[a-z0-9_]+$')` | Lowercases and trims input | **BOTH** | Duplicate insert throws `23505`; uppercase insert throws `23514`. |
| **Non-empty display name** | `CHECK (length(trim(display_name)) >= 1)` | Validates `1 <= len(name) <= 50` | **BOTH** | Whitespace-only insert throws `23514`. |
| **Referential existence (authors, parents)** | `FOREIGN KEY` constraints on all FK columns | Pre-validates UUID formats | **BOTH** | Non-existent author/parent throws `23503`. |
| **Like uniqueness per user/post** | `PRIMARY KEY (user_id, post_id)` | Idempotent duplicate recovery | **BOTH** | Duplicate like throws `23505`; service returns authoritative state. |
| **Follow pair uniqueness** | `PRIMARY KEY (follower_id, following_id)` | Checks prior follow status | **BOTH** | Duplicate follow insert throws `23505`. |
| **No self-follow** | `CHECK (follower_id <> following_id)` | Rejects `follower == following` with 400 | **BOTH** | Self-follow insert throws `23514`. |
| **Post text bounds (1–280 code points)** | `CHECK (length(trim(text)) BETWEEN 1 AND 280)` | Trims text; validates Unicode code points | **BOTH** | Text > 280 chars or empty string throws `23514`. |
| **Post kind & attribute consistency** | Table-level `CHECK` matching kind to text/references | Pydantic model validation per kind | **BOTH** | Invalid kind or missing reference throws `23514`. |
| **No duplicate repost by same author** | `UNIQUE (author_id, repost_of_id)` | Checks existing repost status | **BOTH** | Duplicate repost throws `23505` (`409 Conflict`). |
| **Reply target must be original** | Foreign key guarantees row existence | Service verifies `target.kind == 'original'` | **SERVICE** | Reply to reply/repost rejected with `422 Unprocessable Entity`. |
| **Repost target must be original** | Foreign key guarantees row existence | Service verifies `target.kind == 'original'` | **SERVICE** | Repost of reply/repost rejected with `422 Unprocessable Entity`. |
| **Media belongs only to originals** | Parent cascade ownership | Service validates `post.kind == 'original'` | **SERVICE** | Attaching media to reply/repost rejected with `422`. |
| **Media positions 0–3** | `CHECK (position >= 0 AND position <= 3)` | Sets zero-based index | **DATABASE** | Position `< 0` or `> 3` throws `23514`. |
| **Media position uniqueness per post** | `UNIQUE (post_id, position)` | Arranges sequential 0..N positions | **DATABASE** | Overlapping position on same post throws `23505`. |
| **Max 4 media items per post** | Constrained by positions 0..3 & uniqueness | Validates `len(media) <= 4` on upload | **BOTH** | Attempting 5th media slot fails via position bounds / validation. |
| **Positive image dimensions** | `CHECK (width > 0 AND height > 0)` | Validates image metadata | **DATABASE** | `width <= 0` throws `23514`. |
| **Non-empty media URLs & alt text** | `CHECK (length(trim(...)) > 0)` on URLs and alt text | Schema validation | **DATABASE** | Empty URL or alt text throws `23514`. |
| **Authoritative reaction/follower counts** | Computed via `COUNT(...)` | Reads aggregate queries | **DATABASE** | Queries derived directly from association tables; no count drift. |

---

## 15. Constraint Test Plan (Design-Level Test Specification)

Below is the design-level test specification for SQL and Service constraint validation (to be executed during Stage B Step 3/4):

### Database-Level Negative Test Cases (Direct SQL)
1. **Duplicate Handle Rejection:**
   - *Action:* Insert user with `handle = 'asha'` when `'asha'` already exists.
   - *Expected Result:* Rejection with `23505 (unique_violation)`.
2. **Orphan Author Rejection:**
   - *Action:* Insert post with `author_id = '99999999-9999-4999-8999-999999999999'` (non-existent).
   - *Expected Result:* Rejection with `23503 (foreign_key_violation)`.
3. **Orphan Media Rejection:**
   - *Action:* Insert media with `post_id = '99999999-9999-4999-8999-999999999999'` (non-existent).
   - *Expected Result:* Rejection with `23503 (foreign_key_violation)`.
4. **Orphan Like Rejection:**
   - *Action:* Insert like referencing non-existent `user_id` or non-existent `post_id`.
   - *Expected Result:* Rejection with `23503 (foreign_key_violation)`.
5. **Orphan Follow Rejection:**
   - *Action:* Insert follow referencing non-existent `follower_id` or `following_id`.
   - *Expected Result:* Rejection with `23503 (foreign_key_violation)`.
6. **Duplicate Like Rejection:**
   - *Action:* Insert identical `(user_id, post_id)` pair into `post_likes` twice.
   - *Expected Result:* Rejection with `23505 (unique_violation)`.
7. **Duplicate Follow Rejection:**
   - *Action:* Insert identical `(follower_id, following_id)` pair into `follows` twice.
   - *Expected Result:* Rejection with `23505 (unique_violation)`.
8. **Self-Follow Rejection:**
   - *Action:* Insert follow where `follower_id = following_id`.
   - *Expected Result:* Rejection with `23514 (check_violation)`.
9. **Duplicate Repost Rejection:**
   - *Action:* Author A reposts Original Post B a second time.
   - *Expected Result:* Rejection with `23505 (unique_violation)`.
10. **Invalid Post Kind Combination:**
    - *Action:* Insert post with `kind = 'original'` and non-null `reply_to_id`, or `kind = 'repost'` with non-null `text`.
    - *Expected Result:* Rejection with `23514 (check_violation)`.
11. **Invalid Media Position:**
    - *Action:* Insert media with `position = 4` or `position = -1`.
    - *Expected Result:* Rejection with `23514 (check_violation)`.
12. **Duplicate Media Position:**
    - *Action:* Insert two media rows for the same `post_id` both with `position = 0`.
    - *Expected Result:* Rejection with `23505 (unique_violation)`.
13. **Invalid Image Dimensions:**
    - *Action:* Insert media with `width = 0` or `height = -100`.
    - *Expected Result:* Rejection with `23514 (check_violation)`.
14. **Invalid Stored Text Length:**
    - *Action:* Insert post with `text = ''` (empty) or `text` > 280 chars.
    - *Expected Result:* Rejection with `23514 (check_violation)`.

### Service-Level Test Cases (Application Logic)
1. **Reply to Non-Original:** Attempting to create a reply referencing a reply or repost is rejected with `422 Unprocessable Entity`.
2. **Repost of Non-Original:** Attempting to create a repost referencing a reply or repost is rejected with `422 Unprocessable Entity`.
3. **Media Upload Cap:** Attempting to attach > 4 images to a post in a single request is rejected with `422 Unprocessable Entity`.
4. **Like on Repost Row:** Attempting to like a repost row is rejected with `422 Unprocessable Entity`.
