# Data Dictionary — Stage B Relational Schema

This document details the complete data dictionary for the PostgreSQL relational schema of the **Social Feed** application.

---

## 1. Entity: `users`
Represents registered human actors and authors in the system.

| Column | Logical Meaning | PostgreSQL Type | Nullable | Default | Constraints & Keys | Example Value |
|---|---|---|---|---|---|---|
| `id` | Unique public identifier for the user | `UUID` | No | None | `PRIMARY KEY` | `'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'` |
| `handle` | Unique username for profile routing & mentions | `VARCHAR(30)` | No | None | `UNIQUE`, `CHECK (handle = lower(handle) AND length(trim(handle)) >= 1 AND handle ~ '^[a-z0-9_]+$')` | `'asha'` |
| `display_name` | Human-readable user name for presentation | `VARCHAR(50)` | No | None | `CHECK (length(trim(display_name)) >= 1)` | `'Asha Patel'` |
| `bio` | User biography or self-description | `TEXT` | Yes | `NULL` | None | `'Software engineer & amateur photographer 📷✨'` |
| `avatar_small_url` | 150×150 thumbnail image URL | `TEXT` | Yes | `NULL` | `CHECK (avatar_small_url IS NULL OR length(trim(avatar_small_url)) > 0)` | `'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80'` |
| `avatar_large_url` | 600×600 high-res avatar image URL | `TEXT` | Yes | `NULL` | `CHECK (avatar_large_url IS NULL OR length(trim(avatar_large_url)) > 0)` | `'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&q=80'` |
| `created_at` | Account creation timestamp | `TIMESTAMPTZ(3)` | No | `CURRENT_TIMESTAMP` | Millisecond precision UTC | `'2026-08-15 08:00:00.000+00'` |

---

## 2. Entity: `posts`
Represents all posts, including original publications, direct replies, and repost references.

| Column | Logical Meaning | PostgreSQL Type | Nullable | Default | Constraints & Keys | Example Value |
|---|---|---|---|---|---|---|
| `id` | Unique public identifier for the post | `UUID` | No | None | `PRIMARY KEY` | `'11111111-1111-4111-8111-111111111101'` |
| `author_id` | User who authored or created this post/action | `UUID` | No | None | `FOREIGN KEY REFERENCES users(id) ON DELETE RESTRICT` | `'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02'` |
| `kind` | Discriminator indicating post type | `VARCHAR(10)` | No | None | `CHECK (kind IN ('original', 'reply', 'repost'))` | `'original'` |
| `text` | Trimmed Unicode content (1–280 code points) | `VARCHAR(280)` | Yes | `NULL` | `CHECK (text IS NULL OR length(trim(text)) BETWEEN 1 AND 280)` | `'Morning mist rising over pine forests 🌲⛰️'` |
| `reply_to_id` | Foreign key referencing parent original post | `UUID` | Yes | `NULL` | `FOREIGN KEY REFERENCES posts(id) ON DELETE RESTRICT` | `'11111111-1111-4111-8111-111111111101'` (for reply) |
| `repost_of_id` | Foreign key referencing reposted original post | `UUID` | Yes | `NULL` | `FOREIGN KEY REFERENCES posts(id) ON DELETE RESTRICT` | `'11111111-1111-4111-8111-111111111101'` (for repost) |
| `created_at` | UTC timestamp of post creation | `TIMESTAMPTZ(3)` | No | `CURRENT_TIMESTAMP` | Millisecond precision UTC | `'2026-09-01 10:30:00.000+00'` |

### Table-Level Constraints on `posts`:
1. **Kind / Attribute Consistency Constraint:**
   ```sql
   CHECK (
     (kind = 'original' AND text IS NOT NULL AND reply_to_id IS NULL AND repost_of_id IS NULL) OR
     (kind = 'reply'    AND text IS NOT NULL AND reply_to_id IS NOT NULL AND repost_of_id IS NULL) OR
     (kind = 'repost'   AND text IS NULL     AND reply_to_id IS NULL AND repost_of_id IS NOT NULL)
   )
   ```
2. **Duplicate Repost Prevention Constraint:**
   ```sql
   UNIQUE (author_id, repost_of_id)
   ```
   *(Ensures a user can repost a particular original post at most once).*

---

## 3. Entity: `post_media`
Represents ordered image attachments associated with original posts.

| Column | Logical Meaning | PostgreSQL Type | Nullable | Default | Constraints & Keys | Example Value |
|---|---|---|---|---|---|---|
| `id` | Unique public identifier for the media item | `UUID` | No | None | `PRIMARY KEY` | `'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01'` |
| `post_id` | Foreign key referencing the parent original post | `UUID` | No | None | `FOREIGN KEY REFERENCES posts(id) ON DELETE CASCADE` | `'11111111-1111-4111-8111-111111111101'` |
| `position` | Zero-based display order within carousel (0–3) | `SMALLINT` | No | None | `CHECK (position >= 0 AND position <= 3)` | `0` |
| `alt_text` | Accessibility description for screen readers | `TEXT` | No | None | `CHECK (length(trim(alt_text)) >= 1)` | `'Morning mist rising over pine forests'` |
| `width` | Intrinsic pixel width of original asset | `INTEGER` | No | None | `CHECK (width > 0)` | `1200` |
| `height` | Intrinsic pixel height of original asset | `INTEGER` | No | None | `CHECK (height > 0)` | `800` |
| `small_url` | 400px width responsive variant URL | `TEXT` | No | None | `CHECK (length(trim(small_url)) >= 1)` | `'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&q=80'` |
| `large_url` | 1200px width responsive variant URL | `TEXT` | No | None | `CHECK (length(trim(large_url)) >= 1)` | `'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&q=80'` |
| `created_at` | Media upload/creation UTC timestamp | `TIMESTAMPTZ(3)` | No | `CURRENT_TIMESTAMP` | Millisecond precision UTC (used in profile media cursor) | `'2026-09-01 10:30:00.000+00'` |

### Table-Level Constraints on `post_media`:
1. **Unique Position per Post:**
   ```sql
   UNIQUE (post_id, position)
   ```
   *(Prevents duplicate display slots within the same post carousel).*

---

## 4. Entity: `post_likes`
Association relation modeling a user's reaction to an original post or reply.

| Column | Logical Meaning | PostgreSQL Type | Nullable | Default | Constraints & Keys | Example Value |
|---|---|---|---|---|---|---|
| `user_id` | Foreign key referencing the liking user | `UUID` | No | None | `PRIMARY KEY (user_id, post_id)`, `FK REFERENCES users(id) ON DELETE CASCADE` | `'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'` |
| `post_id` | Foreign key referencing the liked post | `UUID` | No | None | `PRIMARY KEY (user_id, post_id)`, `FK REFERENCES posts(id) ON DELETE CASCADE` | `'11111111-1111-4111-8111-111111111101'` |
| `created_at` | Timestamp when like occurred | `TIMESTAMPTZ(3)` | No | `CURRENT_TIMESTAMP` | Millisecond precision UTC | `'2026-09-01 11:00:00.000+00'` |

*(Note: The composite primary key `(user_id, post_id)` strictly enforces that a user can like a post at most once).*

---

## 5. Entity: `follows`
Association relation modeling directional follow edges between users.

| Column | Logical Meaning | PostgreSQL Type | Nullable | Default | Constraints & Keys | Example Value |
|---|---|---|---|---|---|---|
| `follower_id` | Foreign key referencing the user who follows | `UUID` | No | None | `PRIMARY KEY (follower_id, following_id)`, `FK REFERENCES users(id) ON DELETE CASCADE` | `'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'` |
| `following_id` | Foreign key referencing the followed user | `UUID` | No | None | `PRIMARY KEY (follower_id, following_id)`, `FK REFERENCES users(id) ON DELETE CASCADE` | `'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02'` |
| `created_at` | Timestamp when follow edge was established | `TIMESTAMPTZ(3)` | No | `CURRENT_TIMESTAMP` | Millisecond precision UTC | `'2026-08-20 09:00:00.000+00'` |

### Table-Level Constraints on `follows`:
1. **Self-Follow Prohibition Constraint:**
   ```sql
   CHECK (follower_id <> following_id)
   ```
   *(Prevents users from following their own account).*
2. **Duplicate Pair Prohibition:**
   Enforced naturally by the composite primary key `PRIMARY KEY (follower_id, following_id)`.
