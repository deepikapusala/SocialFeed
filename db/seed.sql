-- ============================================================================
-- Social Feed Deterministic Seed Dataset (Stage B)
-- Target Engine: PostgreSQL 16+
-- Exact Parity with Stage A In-Memory Fixtures
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. USERS (Exactly 6 Users)
-- ----------------------------------------------------------------------------
INSERT INTO users (id, handle, display_name, bio, avatar_small_url, avatar_large_url, created_at)
VALUES
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'asha', 'Asha Patel',
     'Software engineer & amateur landscape photographer 📷✨',
     'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80',
     'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&q=80',
     '2026-08-01 08:00:00.000+00'),

    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'yosemite_wanderer', 'Marcus Thorne',
     'Exploring national parks, alpine lakes, and pine forests 🌲⛰️',
     'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&q=80',
     'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=80',
     '2026-08-02 09:00:00.000+00'),

    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'atelier_canvas', 'Elena Rostova',
     'Contemporary oil painter & studio artist. Textures and color palette studies 🎨',
     'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&q=80',
     'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=80',
     '2026-08-03 10:00:00.000+00'),

    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'street_lens', 'David Kim',
     'Urban geometry, night lights, and street shadows 🏙️🚶',
     'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&q=80',
     'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&q=80',
     '2026-08-04 11:00:00.000+00'),

    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'urban_geometry', 'Clara Vance',
     'Architectural forms, minimal facades, and concrete shadows 🏛️📐',
     'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&q=80',
     'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&q=80',
     '2026-08-05 12:00:00.000+00'),

    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa06', 'zero_media_user', 'Jordan Lee',
     'New to the platform. Dedicated edge-case user with 0 posts & 0 media.',
     NULL, NULL,
     '2026-08-06 13:00:00.000+00')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. ORIGINAL POSTS (Exactly 30 Originals)
-- Note on Timestamp Tie: Posts 10 and 11 share '2026-09-01 10:20:00.000+00'
-- ----------------------------------------------------------------------------
INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at)
VALUES
    ('11111111-1111-4111-8111-111111111101', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original',
     'Original post #1 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #1', NULL, NULL, '2026-09-01 10:30:00.000+00'),

    ('11111111-1111-4111-8111-111111111102', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'original',
     'Original post #2 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #2', NULL, NULL, '2026-09-01 10:29:00.000+00'),

    ('11111111-1111-4111-8111-111111111103', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'original',
     'Original post #3 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #3', NULL, NULL, '2026-09-01 10:28:00.000+00'),

    ('11111111-1111-4111-8111-111111111104', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'original',
     'Original post #4 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #4', NULL, NULL, '2026-09-01 10:27:00.000+00'),

    ('11111111-1111-4111-8111-111111111105', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'original',
     'Original post #5 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #5', NULL, NULL, '2026-09-01 10:26:00.000+00'),

    ('11111111-1111-4111-8111-111111111106', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original',
     'Original post #6 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #6', NULL, NULL, '2026-09-01 10:25:00.000+00'),

    ('11111111-1111-4111-8111-111111111107', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'original',
     'Original post #7 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #7', NULL, NULL, '2026-09-01 10:24:00.000+00'),

    ('11111111-1111-4111-8111-111111111108', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'original',
     'Original post #8 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #8', NULL, NULL, '2026-09-01 10:23:00.000+00'),

    ('11111111-1111-4111-8111-111111111109', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'original',
     'Original post #9 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #9', NULL, NULL, '2026-09-01 10:22:00.000+00'),

    ('11111111-1111-4111-8111-111111111110', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'original',
     'Original post #10 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #10', NULL, NULL, '2026-09-01 10:20:00.000+00'),

    ('11111111-1111-4111-8111-111111111111', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original',
     'Original post #11 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #11', NULL, NULL, '2026-09-01 10:20:00.000+00'),

    ('11111111-1111-4111-8111-111111111112', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'original',
     'Original post #12 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #12', NULL, NULL, '2026-09-01 10:18:00.000+00'),

    ('11111111-1111-4111-8111-111111111113', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'original',
     'Original post #13 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #13', NULL, NULL, '2026-09-01 10:17:00.000+00'),

    ('11111111-1111-4111-8111-111111111114', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'original',
     'Original post #14 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #14', NULL, NULL, '2026-09-01 10:16:00.000+00'),

    ('11111111-1111-4111-8111-111111111115', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'original',
     'Original post #15 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #15', NULL, NULL, '2026-09-01 10:15:00.000+00'),

    ('11111111-1111-4111-8111-111111111116', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original',
     'Original post #16 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #16', NULL, NULL, '2026-09-01 10:14:00.000+00'),

    ('11111111-1111-4111-8111-111111111117', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'original',
     'Original post #17 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #17', NULL, NULL, '2026-09-01 10:13:00.000+00'),

    ('11111111-1111-4111-8111-111111111118', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'original',
     'Original post #18 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #18', NULL, NULL, '2026-09-01 10:12:00.000+00'),

    ('11111111-1111-4111-8111-111111111119', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'original',
     'Original post #19 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #19', NULL, NULL, '2026-09-01 10:11:00.000+00'),

    ('11111111-1111-4111-8111-111111111120', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'original',
     'Original post #20 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #20', NULL, NULL, '2026-09-01 10:10:00.000+00'),

    ('11111111-1111-4111-8111-111111111121', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original',
     'Original post #21 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #21', NULL, NULL, '2026-09-01 10:09:00.000+00'),

    ('11111111-1111-4111-8111-111111111122', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'original',
     'Original post #22 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #22', NULL, NULL, '2026-09-01 10:08:00.000+00'),

    ('11111111-1111-4111-8111-111111111123', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'original',
     'Original post #23 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #23', NULL, NULL, '2026-09-01 10:07:00.000+00'),

    ('11111111-1111-4111-8111-111111111124', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'original',
     'Original post #24 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #24', NULL, NULL, '2026-09-01 10:06:00.000+00'),

    ('11111111-1111-4111-8111-111111111125', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'original',
     'Original post #25 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #25', NULL, NULL, '2026-09-01 10:05:00.000+00'),

    ('11111111-1111-4111-8111-111111111126', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original',
     'Original post #26 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #26', NULL, NULL, '2026-09-01 10:04:00.000+00'),

    ('11111111-1111-4111-8111-111111111127', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'original',
     'Original post #27 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #27', NULL, NULL, '2026-09-01 10:03:00.000+00'),

    ('11111111-1111-4111-8111-111111111128', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'original',
     'Original post #28 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #28', NULL, NULL, '2026-09-01 10:02:00.000+00'),

    ('11111111-1111-4111-8111-111111111129', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'original',
     'Original post #29 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #29', NULL, NULL, '2026-09-01 10:01:00.000+00'),

    ('11111111-1111-4111-8111-111111111130', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'original',
     'Original post #30 caption. Beautiful photo exploration in nature, art, and urban spaces #explore #30', NULL, NULL, '2026-09-01 10:00:00.000+00')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. DIRECT REPLIES (Exactly 12 Direct Replies)
-- ----------------------------------------------------------------------------
INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at)
VALUES
    ('22222222-2222-4222-8222-222222222201', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'reply',
     'Insightful comment and reply #1 to the original photo post!', '11111111-1111-4111-8111-111111111102', NULL, '2026-09-01 11:01:00.000+00'),

    ('22222222-2222-4222-8222-222222222202', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'reply',
     'Insightful comment and reply #2 to the original photo post!', '11111111-1111-4111-8111-111111111103', NULL, '2026-09-01 11:02:00.000+00'),

    ('22222222-2222-4222-8222-222222222203', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'reply',
     'Insightful comment and reply #3 to the original photo post!', '11111111-1111-4111-8111-111111111104', NULL, '2026-09-01 11:03:00.000+00'),

    ('22222222-2222-4222-8222-222222222204', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'reply',
     'Insightful comment and reply #4 to the original photo post!', '11111111-1111-4111-8111-111111111105', NULL, '2026-09-01 11:04:00.000+00'),

    ('22222222-2222-4222-8222-222222222205', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'reply',
     'Insightful comment and reply #5 to the original photo post!', '11111111-1111-4111-8111-111111111106', NULL, '2026-09-01 11:05:00.000+00'),

    ('22222222-2222-4222-8222-222222222206', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'reply',
     'Insightful comment and reply #6 to the original photo post!', '11111111-1111-4111-8111-111111111101', NULL, '2026-09-01 11:06:00.000+00'),

    ('22222222-2222-4222-8222-222222222207', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'reply',
     'Insightful comment and reply #7 to the original photo post!', '11111111-1111-4111-8111-111111111102', NULL, '2026-09-01 11:07:00.000+00'),

    ('22222222-2222-4222-8222-222222222208', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'reply',
     'Insightful comment and reply #8 to the original photo post!', '11111111-1111-4111-8111-111111111103', NULL, '2026-09-01 11:08:00.000+00'),

    ('22222222-2222-4222-8222-222222222209', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'reply',
     'Insightful comment and reply #9 to the original photo post!', '11111111-1111-4111-8111-111111111104', NULL, '2026-09-01 11:09:00.000+00'),

    ('22222222-2222-4222-8222-222222222210', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'reply',
     'Insightful comment and reply #10 to the original photo post!', '11111111-1111-4111-8111-111111111105', NULL, '2026-09-01 11:10:00.000+00'),

    ('22222222-2222-4222-8222-222222222211', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'reply',
     'Insightful comment and reply #11 to the original photo post!', '11111111-1111-4111-8111-111111111106', NULL, '2026-09-01 11:11:00.000+00'),

    ('22222222-2222-4222-8222-222222222212', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'reply',
     'Insightful comment and reply #12 to the original photo post!', '11111111-1111-4111-8111-111111111101', NULL, '2026-09-01 11:12:00.000+00')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. REPOSTS (Exactly 4 Reposts)
-- ----------------------------------------------------------------------------
INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at)
VALUES
    ('33333333-3333-4333-8333-333333333301', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'repost',
     NULL, NULL, '11111111-1111-4111-8111-111111111101', '2026-09-01 12:01:00.000+00'),

    ('33333333-3333-4333-8333-333333333302', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'repost',
     NULL, NULL, '11111111-1111-4111-8111-111111111102', '2026-09-01 12:02:00.000+00'),

    ('33333333-3333-4333-8333-333333333303', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'repost',
     NULL, NULL, '11111111-1111-4111-8111-111111111103', '2026-09-01 12:03:00.000+00'),

    ('33333333-3333-4333-8333-333333333304', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'repost',
     NULL, NULL, '11111111-1111-4111-8111-111111111104', '2026-09-01 12:04:00.000+00')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. POST MEDIA (Exactly 10 Media Rows for Originals)
-- ----------------------------------------------------------------------------
INSERT INTO post_media (id, post_id, position, alt_text, width, height, small_url, large_url, created_at)
VALUES
    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01', '11111111-1111-4111-8111-111111111101', 0,
     'Morning mist rising over pine forests', 1200, 800,
     'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&q=80',
     'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&q=80',
     '2026-09-01 10:30:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb02', '11111111-1111-4111-8111-111111111101', 1,
     'Sunlight piercing through redwood canopy', 1200, 800,
     'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&q=80',
     'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&q=80',
     '2026-09-01 10:30:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb03', '11111111-1111-4111-8111-111111111102', 0,
     'Textured oil painting on raw linen canvas', 1080, 1080,
     'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=400&q=80',
     'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=1080&q=80',
     '2026-09-01 10:29:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb04', '11111111-1111-4111-8111-111111111103', 0,
     'Golden hour shadows across city avenues', 1080, 1350,
     'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=400&q=80',
     'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1080&q=80',
     '2026-09-01 10:28:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb05', '11111111-1111-4111-8111-111111111104', 0,
     'Curving concrete facade and geometric architecture', 1080, 1350,
     'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80',
     'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1080&q=80',
     '2026-09-01 10:27:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb06', '11111111-1111-4111-8111-111111111105', 0,
     'Fresh handmade pasta with olive oil', 1080, 1080,
     'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80',
     'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1080&q=80',
     '2026-09-01 10:26:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb07', '11111111-1111-4111-8111-111111111106', 0,
     'Slow drip coffee and latte art', 1080, 1350,
     'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&q=80',
     'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1080&q=80',
     '2026-09-01 10:25:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb08', '11111111-1111-4111-8111-111111111107', 0,
     'Turquoise ocean waters and rolling tides', 1200, 800,
     'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80',
     'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=80',
     '2026-09-01 10:24:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb09', '11111111-1111-4111-8111-111111111108', 0,
     'Autumn/Winter minimalist fashion look', 1080, 1350,
     'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80',
     'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1080&q=80',
     '2026-09-01 10:23:00.000+00'),

    ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb10', '11111111-1111-4111-8111-111111111109', 0,
     'Stargazing under the Milky Way night sky', 1200, 800,
     'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=400&q=80',
     'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1200&q=80',
     '2026-09-01 10:22:00.000+00')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. POST LIKES (Exactly 15 Likes on Originals / Replies)
-- ----------------------------------------------------------------------------
INSERT INTO post_likes (user_id, post_id, created_at)
VALUES
    -- Demo user ("asha") likes
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-1111-4111-8111-111111111101', '2026-09-01 10:35:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-1111-4111-8111-111111111102', '2026-09-01 10:36:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-1111-4111-8111-111111111103', '2026-09-01 10:37:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-1111-4111-8111-111111111104', '2026-09-01 10:38:00.000+00'),

    -- Other users' likes on originals
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', '11111111-1111-4111-8111-111111111101', '2026-09-01 10:39:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', '11111111-1111-4111-8111-111111111101', '2026-09-01 10:40:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', '11111111-1111-4111-8111-111111111102', '2026-09-01 10:41:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', '11111111-1111-4111-8111-111111111102', '2026-09-01 10:42:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', '11111111-1111-4111-8111-111111111105', '2026-09-01 10:43:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', '11111111-1111-4111-8111-111111111106', '2026-09-01 10:44:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', '11111111-1111-4111-8111-111111111107', '2026-09-01 10:45:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', '11111111-1111-4111-8111-111111111108', '2026-09-01 10:46:00.000+00'),

    -- Likes on replies
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '22222222-2222-4222-8222-222222222201', '2026-09-01 11:15:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', '22222222-2222-4222-8222-222222222201', '2026-09-01 11:16:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', '22222222-2222-4222-8222-222222222202', '2026-09-01 11:17:00.000+00')
ON CONFLICT (user_id, post_id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. FOLLOWS (Exactly 8 Follow Edges)
-- ----------------------------------------------------------------------------
INSERT INTO follows (follower_id, following_id, created_at)
VALUES
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', '2026-08-10 10:00:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', '2026-08-10 10:01:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', '2026-08-10 10:02:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '2026-08-11 11:00:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '2026-08-12 12:00:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', '2026-08-13 13:00:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02', '2026-08-14 14:00:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa05', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03', '2026-08-14 14:01:00.000+00')
ON CONFLICT (follower_id, following_id) DO NOTHING;
