-- ============================================================================
-- Social Feed Schema Definition (Stage B)
-- Target Engine: PostgreSQL 16+
-- Reference: docs/erd.md, docs/data-dictionary.md, docs/decisions.md
-- ============================================================================

-- Drop tables in reverse dependency order for clean, idempotent execution
DROP TABLE IF EXISTS follows CASCADE;
DROP TABLE IF EXISTS post_likes CASCADE;
DROP TABLE IF EXISTS post_media CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ----------------------------------------------------------------------------
-- 1. USERS
-- Represents registered social accounts and authors.
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY,
    handle VARCHAR(30) NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    bio TEXT,
    avatar_small_url TEXT,
    avatar_large_url TEXT,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Normalized handle uniqueness (case-sensitive unique index backed by lowercase check)
    CONSTRAINT users_handle_unique UNIQUE (handle),
    CONSTRAINT users_handle_format_check CHECK (
        handle = lower(handle) AND
        length(trim(handle)) >= 1 AND
        handle ~ '^[a-z0-9_]+$'
    ),
    CONSTRAINT users_display_name_check CHECK (length(trim(display_name)) >= 1),
    CONSTRAINT users_avatar_small_url_check CHECK (avatar_small_url IS NULL OR length(trim(avatar_small_url)) > 0),
    CONSTRAINT users_avatar_large_url_check CHECK (avatar_large_url IS NULL OR length(trim(avatar_large_url)) > 0)
);

-- ----------------------------------------------------------------------------
-- 2. POSTS
-- Unified table representing original posts, direct replies, and reposts.
-- Content reuse: reposts store no new text or media, only repost_of_id.
-- ----------------------------------------------------------------------------
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    kind VARCHAR(10) NOT NULL,
    text VARCHAR(280),
    reply_to_id UUID REFERENCES posts(id) ON DELETE RESTRICT,
    repost_of_id UUID REFERENCES posts(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Valid post kinds
    CONSTRAINT posts_kind_check CHECK (kind IN ('original', 'reply', 'repost')),

    -- Stored text length constraints (1–280 Unicode code points when present)
    CONSTRAINT posts_text_length_check CHECK (text IS NULL OR length(trim(text)) BETWEEN 1 AND 280),

    -- Table-level structural invariants per post kind:
    -- • original: requires text, no parent references
    -- • reply:    requires text, requires reply_to_id, no repost_of_id
    -- • repost:   requires text to be NULL, requires repost_of_id, no reply_to_id
    CONSTRAINT posts_kind_attributes_check CHECK (
        (kind = 'original' AND text IS NOT NULL AND reply_to_id IS NULL AND repost_of_id IS NULL) OR
        (kind = 'reply'    AND text IS NOT NULL AND reply_to_id IS NOT NULL AND repost_of_id IS NULL) OR
        (kind = 'repost'   AND text IS NULL     AND reply_to_id IS NULL AND repost_of_id IS NOT NULL)
    ),

    -- A user can repost a particular original post at most once
    CONSTRAINT posts_author_repost_unique UNIQUE (author_id, repost_of_id)
);

-- ----------------------------------------------------------------------------
-- 3. POST_MEDIA
-- Ordered carousel media attachments belonging to original posts (0..4).
-- ----------------------------------------------------------------------------
CREATE TABLE post_media (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    position SMALLINT NOT NULL,
    alt_text TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    small_url TEXT NOT NULL,
    large_url TEXT NOT NULL,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Ordered carousel slot bounds (0, 1, 2, 3)
    CONSTRAINT post_media_position_check CHECK (position >= 0 AND position <= 3),

    -- Ensures no overlapping image positions within the same post
    CONSTRAINT post_media_post_position_unique UNIQUE (post_id, position),

    -- Intrinsic dimensions and URL invariants
    CONSTRAINT post_media_dimensions_check CHECK (width > 0 AND height > 0),
    CONSTRAINT post_media_alt_text_check CHECK (length(trim(alt_text)) >= 1),
    CONSTRAINT post_media_small_url_check CHECK (length(trim(small_url)) >= 1),
    CONSTRAINT post_media_large_url_check CHECK (length(trim(large_url)) >= 1)
);

-- ----------------------------------------------------------------------------
-- 4. POST_LIKES
-- Association table for user reactions to posts.
-- Single like per user/post enforced by composite primary key.
-- ----------------------------------------------------------------------------
CREATE TABLE post_likes (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, post_id)
);

-- ----------------------------------------------------------------------------
-- 5. FOLLOWS
-- Directional follow graph association table.
-- Self-follows prohibited by CHECK constraint.
-- ----------------------------------------------------------------------------
CREATE TABLE follows (
    follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (follower_id, following_id),
    CONSTRAINT follows_no_self_follow_check CHECK (follower_id <> following_id)
);
