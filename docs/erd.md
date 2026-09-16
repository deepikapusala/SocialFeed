# Entity-Relationship Diagram (ERD) — Stage B

This document presents the conceptual and logical Entity-Relationship Diagram for the **Social Feed** application. It maps the five core entities required by the shared contract and PRD 03: **User**, **Post**, **PostMedia**, **Like**, and **Follow**.

---

## 1. Mermaid Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ POSTS : "authors"
    USERS ||--o{ POST_LIKES : "submits"
    USERS ||--o{ FOLLOWS : "acts as follower"
    USERS ||--o{ FOLLOWS : "acts as following"
    
    POSTS ||--o{ POST_MEDIA : "owns (0..4, originals only)"
    POSTS ||--o{ POST_LIKES : "receives"
    
    POSTS ||--o{ POSTS : "direct replies (reply_to_id)"
    POSTS ||--o{ POSTS : "repost references (repost_of_id)"

    USERS {
        uuid id PK "Public UUID"
        varchar handle UK "Normalized unique lowercase handle (1-30 chars)"
        varchar display_name "User display name (1-50 chars)"
        text bio "Optional biography / profile text"
        text avatar_small_url "Optional small avatar URL variant (150x150)"
        text avatar_large_url "Optional large avatar URL variant (600x600)"
        timestamptz created_at "Account creation UTC timestamp (ms precision)"
    }

    POSTS {
        uuid id PK "Public UUID"
        uuid author_id FK "References users(id)"
        varchar kind "Post discriminator: 'original' | 'reply' | 'repost'"
        varchar text "Trimmed Unicode text (1-280 chars; NULL for repost)"
        uuid reply_to_id FK "References posts(id) [NULL for original/repost]"
        uuid repost_of_id FK "References posts(id) [NULL for original/reply]"
        timestamptz created_at "Post publication UTC timestamp (ms precision)"
    }

    POST_MEDIA {
        uuid id PK "Public UUID"
        uuid post_id FK "References posts(id) [originals only]"
        smallint position "Zero-based display order (0, 1, 2, 3)"
        text alt_text "Accessible image description"
        integer width "Original pixel width (> 0)"
        integer height "Original pixel height (> 0)"
        text small_url "Low-resolution thumbnail URL"
        text large_url "High-resolution display URL"
        timestamptz created_at "Media creation UTC timestamp (ms precision)"
    }

    POST_LIKES {
        uuid user_id PK, FK "References users(id)"
        uuid post_id PK, FK "References posts(id)"
        timestamptz created_at "Reaction timestamp (ms precision)"
    }

    FOLLOWS {
        uuid follower_id PK, FK "References users(id)"
        uuid following_id PK, FK "References users(id)"
        timestamptz created_at "Follow relationship creation timestamp"
    }
```

---

## 2. Cardinality & Relationship Breakdown

| Relationship | Entities Involved | Cardinality & Optionality | Description / Relational Invariants |
|---|---|---|---|
| **Authoring** | `users` → `posts` | **1 to 0..*** (One-to-Many) | A user can author zero or many posts. Every post must have exactly one author (`author_id NOT NULL`). |
| **Direct Replies** | `posts` (parent) → `posts` (child reply) | **1 to 0..*** (One-to-Many self-reference) | An original post can receive zero or many replies. A reply references exactly one parent original via `reply_to_id`. Replies-to-replies are rejected. |
| **Repost References** | `posts` (parent) → `posts` (child repost) | **1 to 0..*** (One-to-Many self-reference) | An original post can be reposted zero or many times. A repost references exactly one parent original via `repost_of_id`. A user can repost a given original at most once (`UNIQUE (author_id, repost_of_id)`). |
| **Post Media** | `posts` → `post_media` | **1 to 0..4** (One-to-Many) | An original post can have 0 to 4 media items. Media rows belong only to original posts. Display order within a post is defined by `position` (0..3). `(post_id, position)` is unique. |
| **Post Likes** | `users` ↔ `posts` via `post_likes` | **0..* to 0..*** (Many-to-Many) | A user can like zero or many posts; a post can be liked by zero or many users. A user can like a given post at most once. Enforced via composite primary key `(user_id, post_id)`. |
| **Follow Graph** | `users` ↔ `users` via `follows` | **0..* to 0..*** (Directional Many-to-Many self-association) | A user (follower) can follow zero or many users (following). Directional (`A follows B` does not imply `B follows A`). Self-follows (`follower_id = following_id`) are prohibited. Enforced via composite primary key `(follower_id, following_id)`. |

---

## 3. Key Relational Highlights

1. **Unified Post Representation:**
   - Single `posts` table with discriminator `kind` (`'original'`, `'reply'`, `'repost'`).
   - Content reuse without data duplication: Reposts store no text or media, only the foreign key pointer `repost_of_id`.
2. **Deterministic Cursor Navigation:**
   - Both `posts` and `post_media` feature immutable UTC millisecond timestamps (`timestamptz(3)`) paired with unique `id` UUIDs.
   - Paginating queries utilize the strictly descending tuple predicate `(created_at, id) < (cursor_time, cursor_id)`.
3. **No Cached Counts as Source of Truth:**
   - Like counts, reply counts, follower counts, following counts, and post counts are computed authoritatively through relational aggregation (`COUNT(...)`) or subqueries.
