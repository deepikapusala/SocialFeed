-- ============================================================================
-- Social Feed Deterministic Seed Dataset
-- Target Engine: PostgreSQL 16+
-- Exclusively seeds the 5 Core Profiles and their 60 Curated Posts
-- (Deepika, Sneha, Asha Patel, Anirudh, and Virat)
-- ============================================================================

-- Clean up existing tables in safe dependency order
DELETE FROM follows;
DELETE FROM post_likes;
DELETE FROM post_media;
DELETE FROM posts;
DELETE FROM notifications;
DELETE FROM sessions;
DELETE FROM users;

-- ----------------------------------------------------------------------------
-- 1. USERS (Strictly the 5 Core Profiles)
-- ----------------------------------------------------------------------------
INSERT INTO users (id, handle, display_name, bio, avatar_small_url, avatar_large_url, password_hash, is_active, created_at)
VALUES
    ('158469c3-4a2d-4bc6-bf96-5a7638847875', 'deepu', 'Deepika',
     'Artisanal recipes & gourmet food photography ✨🍝',
     'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
     'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
     '$argon2id$v=19$m=65536,t=3,p=4$fv5AaIEi8B3ufEWHKeQ3lA$bPo1F0VMpyKyKRB9Z9RgZ147t71+4Y7xgj8TRFOdHcI',
     TRUE, '2026-08-01 08:00:00.000+00'),

    ('bd4c55d9-31f3-42e9-a210-e1355a77101f', 'sneha', 'Sneha',
     'Botanical aesthetics & garden flora 🌿🌸',
     'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80',
     'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80',
     '$argon2id$v=19$m=65536,t=3,p=4$fv5AaIEi8B3ufEWHKeQ3lA$bPo1F0VMpyKyKRB9Z9RgZ147t71+4Y7xgj8TRFOdHcI',
     TRUE, '2026-08-01 08:05:00.000+00'),

    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'asha', 'Asha Patel',
     'Book lover, stationery & study aesthetic 📖📚',
     'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80',
     'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80',
     '$argon2id$v=19$m=65536,t=3,p=4$fv5AaIEi8B3ufEWHKeQ3lA$bPo1F0VMpyKyKRB9Z9RgZ147t71+4Y7xgj8TRFOdHcI',
     TRUE, '2026-08-01 08:10:00.000+00'),

    ('250070da-0c2b-4a91-8d1a-180a9a2d1781', 'ani', 'Anirudh',
     'Acoustic jams, audio production & beats 🎧🎸',
     'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
     'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
     '$argon2id$v=19$m=65536,t=3,p=4$fv5AaIEi8B3ufEWHKeQ3lA$bPo1F0VMpyKyKRB9Z9RgZ147t71+4Y7xgj8TRFOdHcI',
     TRUE, '2026-08-01 08:15:00.000+00'),

    ('26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'virat', 'Virat',
     'Match day passion, fitness & willow cricket 🏏⚡',
     'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80',
     'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80',
     '$argon2id$v=19$m=65536,t=3,p=4$fv5AaIEi8B3ufEWHKeQ3lA$bPo1F0VMpyKyKRB9Z9RgZ147t71+4Y7xgj8TRFOdHcI',
     TRUE, '2026-08-01 08:20:00.000+00')
ON CONFLICT (id) DO UPDATE SET
    handle = EXCLUDED.handle,
    display_name = EXCLUDED.display_name,
    bio = EXCLUDED.bio,
    avatar_small_url = EXCLUDED.avatar_small_url,
    avatar_large_url = EXCLUDED.avatar_large_url,
    password_hash = EXCLUDED.password_hash,
    is_active = EXCLUDED.is_active;

-- ----------------------------------------------------------------------------
-- 2. ORIGINAL POSTS (12 Posts per Creator = 60 Original Posts)
-- ----------------------------------------------------------------------------
INSERT INTO posts (id, author_id, kind, text, reply_to_id, repost_of_id, created_at, updated_at)
VALUES
    -- Deepika (Food 🍝)
    ('11111111-0001-4000-8000-000000000001', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Artisanal homemade truffle pasta with freshly shaved parmesan 🍝✨ #food #pasta #italian #delicious #foodie', NULL, NULL, '2026-10-21 10:00:00.000+00', '2026-10-21 10:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000002', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'The ultimate double cheeseburger with caramelized onions & crispy fries 🍔🍟 #food #burger #cheatmeal #comfortfood', NULL, NULL, '2026-10-21 12:00:00.000+00', '2026-10-21 12:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000003', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Freshly crafted sushi nigiri & sashimi selection 🍣🍱 #food #sushi #japanesefood #fresh #foodporn', NULL, NULL, '2026-10-21 14:00:00.000+00', '2026-10-21 14:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000004', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Authentic woodfired Margherita pizza straight from the stone oven 🍕🌿 #food #pizza #woodfired #napoli #crust', NULL, NULL, '2026-10-21 16:00:00.000+00', '2026-10-21 16:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000005', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Golden sourdough avocado toast with a runny poached egg 🥑🍳 #food #brunch #healthyfood #avocadotoast #breakfast', NULL, NULL, '2026-10-21 18:00:00.000+00', '2026-10-21 18:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000006', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Steaming bowl of spicy tonkotsu ramen with soft-boiled ajitsuke egg 🍜🥢 #food #ramen #noodles #comfortfood #tokyo', NULL, NULL, '2026-10-21 20:00:00.000+00', '2026-10-21 20:00:00.000+00'),
    ('fd2875cd-6570-42c1-92e3-029888f9477c', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Warm Belgian waffles loaded with fresh berries & pure maple syrup 🧇🍓 #food #waffles #dessert #sweettooth #brunch', NULL, NULL, '2026-10-21 22:00:00.000+00', '2026-10-21 22:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000008', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Authentic street tacos with charred salsa, cilantro & fresh lime 🌮🔥 #food #tacos #mexicanfood #streetfood #flavor', NULL, NULL, '2026-10-22 00:00:00.000+00', '2026-10-22 00:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000009', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Buttery Parisian croissants paired with freshly brewed velvet cappuccino 🥐☕ #food #pastry #croissant #cafe #paris', NULL, NULL, '2026-10-22 02:00:00.000+00', '2026-10-22 02:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000010', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Vibrant antioxidant acai smoothie bowl with granola & tropical kiwi 🥣🥝 #food #acaibowl #healthy #vegan #energy', NULL, NULL, '2026-10-22 04:00:00.000+00', '2026-10-22 04:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000011', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Warm molten chocolate lava cake with vanilla bean gelato 🍫🍨 #food #chocolate #dessert #baking #yummy', NULL, NULL, '2026-10-22 06:00:00.000+00', '2026-10-22 06:00:00.000+00'),
    ('11111111-0001-4000-8000-000000000012', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'original', 'Sizzling wok vegetables & teriyaki glazed tofu over jasmine rice 🥗🥢 #food #stirfry #healthyfood #organic #dinner', NULL, NULL, '2026-10-22 08:00:00.000+00', '2026-10-22 08:00:00.000+00'),

    -- Sneha (Flowers 🌸)
    ('11111111-0002-4000-8000-000000000001', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'A soft pastel bouquet of Dutch tulips to brighten the morning 🌷☀️ #flowers #tulips #spring #nature #bloom', NULL, NULL, '2026-10-22 10:00:00.000+00', '2026-10-22 10:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000002', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Fluffy garden peonies in full romantic bloom 🌸🌿 #flowers #peonies #floral #aesthetic #garden', NULL, NULL, '2026-10-22 12:00:00.000+00', '2026-10-22 12:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000003', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Endless golden sunflowers turning toward the warmth of the sun 🌻💛 #flowers #sunflower #summer #fields #goldenhour', NULL, NULL, '2026-10-22 14:00:00.000+00', '2026-10-22 14:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000004', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Wild alpine daisies blooming freely in the morning breeze 🌼🏔️ #flowers #daisies #wildflowers #nature #peace', NULL, NULL, '2026-10-22 16:00:00.000+00', '2026-10-22 16:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000005', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Deep crimson velvety roses arranged in an artisanal ceramic vase 🌹✨ #flowers #roses #redroses #love #botanical', NULL, NULL, '2026-10-22 18:00:00.000+00', '2026-10-22 18:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000006', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Delicate cherry blossoms signaling the arrival of spring 🌸🍃 #flowers #cherryblossom #sakura #springtime #japan', NULL, NULL, '2026-10-22 20:00:00.000+00', '2026-10-22 20:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000007', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Breathing in the calming fragrance of Provence lavender fields 💜🌾 #flowers #lavender #purple #calm #aromatherapy', NULL, NULL, '2026-10-22 22:00:00.000+00', '2026-10-22 22:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000008', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Pure white chamomile flowers basking in afternoon sunlight 🌼🍵 #flowers #chamomile #herbal #simplicity #clean', NULL, NULL, '2026-10-23 00:00:00.000+00', '2026-10-23 00:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000009', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Exotic moth orchids showing off intricate natural geometric patterns 🌺🌿 #flowers #orchids #botany #plantlove #indoorplants', NULL, NULL, '2026-10-23 02:00:00.000+00', '2026-10-23 02:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000010', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Morning dew droplets resting delicately on fresh flower petals 💧🌸 #flowers #dew #morninglight #macro #beauty', NULL, NULL, '2026-10-23 04:00:00.000+00', '2026-10-23 04:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000011', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Earthy dried floral bouquet bringing cozy warm tones to the room 🌾🏺 #flowers #driedflowers #neutraldecor #interiors #aesthetic', NULL, NULL, '2026-10-23 06:00:00.000+00', '2026-10-23 06:00:00.000+00'),
    ('11111111-0002-4000-8000-000000000012', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'original', 'Spectacular multicolored dahlia unfolding with hundreds of layered petals 🏵️🎨 #flowers #dahlia #natureart #colors #botanical', NULL, NULL, '2026-10-23 08:00:00.000+00', '2026-10-23 08:00:00.000+00'),

    -- Asha Patel (Books & Study 📚)
    ('11111111-0003-4000-8000-000000000001', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'A productive morning study session with clean stationery & hot matcha 📖✍️ #study #books #studygram #notes #focus', NULL, NULL, '2026-10-23 10:00:00.000+00', '2026-10-23 10:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000002', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'A stack of timeless classic literature accompanied by dark roast espresso 📚☕ #books #reading #classicliterature #bookworm #cafe', NULL, NULL, '2026-10-23 12:00:00.000+00', '2026-10-23 12:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000003', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Curling up in my favorite reading nook while rain taps against the glass 🌧️🛋️ #books #cozy #readingnook #hygge #booklover', NULL, NULL, '2026-10-23 14:00:00.000+00', '2026-10-23 14:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000004', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Lost in the majestic silence of the historic university library aisles 🏛️📜 #books #library #architecture #studytime #academia', NULL, NULL, '2026-10-23 16:00:00.000+00', '2026-10-23 16:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000005', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Golden hour rays falling across the open pages of a beloved novel 🌅📖 #books #sunset #goldenhour #peaceful #mindfulness', NULL, NULL, '2026-10-23 18:00:00.000+00', '2026-10-23 18:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000006', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Morning journaling routine to organize thoughts before a busy day 📝✒️ #study #journaling #stationery #productivity #routine', NULL, NULL, '2026-10-23 20:00:00.000+00', '2026-10-23 20:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000007', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Minimalist study desk setup: laptop, clean notepad, and green plant 💻🌱 #study #desksetup #minimalism #workspace #studentlife', NULL, NULL, '2026-10-23 22:00:00.000+00', '2026-10-23 22:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000008', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Reading glasses resting atop yellowed vintage book pages 👓📖 #books #vintage #aesthetic #reader #literary', NULL, NULL, '2026-10-24 00:00:00.000+00', '2026-10-24 00:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000009', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Deep focus session by the window surrounded by natural green plants 🌿☀️ #study #plants #focus #studyinspo #daylight', NULL, NULL, '2026-10-24 02:00:00.000+00', '2026-10-24 02:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000010', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'My dream wall-to-wall personal home library finally taking shape 📚🏰 #books #homelibrary #bookshelf #collection #goals', NULL, NULL, '2026-10-24 04:00:00.000+00', '2026-10-24 04:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000011', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Color-coded highlighters & revision flashcards for upcoming exams 🖍️📑 #study #examseason #revision #prep #motivation', NULL, NULL, '2026-10-24 06:00:00.000+00', '2026-10-24 06:00:00.000+00'),
    ('11111111-0003-4000-8000-000000000012', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'original', 'Browsing dusty shelves in a hidden secondhand bookstore in the city 🏷️📚 #books #bookshop #secondhand #treasure #explore', NULL, NULL, '2026-10-24 08:00:00.000+00', '2026-10-24 08:00:00.000+00'),

    -- Anirudh (Music 🎧)
    ('11111111-0004-4000-8000-000000000001', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Warm acoustic guitar chords filling the quiet evening room 🎸🕯️ #music #guitar #acoustic #musician #chords', NULL, NULL, '2026-10-24 10:00:00.000+00', '2026-10-24 10:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000002', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Practicing Chopin nocturnes on the grand piano keys 🎹🎼 #music #piano #classical #pianist #keys', NULL, NULL, '2026-10-24 12:00:00.000+00', '2026-10-24 12:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000003', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Mixing a new ambient electronic track in the home studio 🎧🎛️ #music #producer #mixing #homestudio #beats', NULL, NULL, '2026-10-24 14:00:00.000+00', '2026-10-24 14:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000004', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Spinning 70s vinyl on the vintage turntable needle 🎶📻 #music #vinyl #turntable #vintageaudio #analog', NULL, NULL, '2026-10-24 16:00:00.000+00', '2026-10-24 16:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000005', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Plugging into the vintage tube amplifier for a midnight guitar session ⚡🎸 #music #electricguitar #rock #fender #riff', NULL, NULL, '2026-10-24 18:00:00.000+00', '2026-10-24 18:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000006', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Ready behind the drum kit under vibrant stage floodlights 🥁🔥 #music #drums #drummer #livemusic #groove', NULL, NULL, '2026-10-24 20:00:00.000+00', '2026-10-24 20:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000007', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'The expressive richness of the wooden classical violin 🎻✨ #music #violin #orchestra #strings #harmony', NULL, NULL, '2026-10-24 22:00:00.000+00', '2026-10-24 22:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000008', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Late night jazz club melodies flowing through brass saxophone 🎷🌙 #music #saxophone #jazz #brass #smooth', NULL, NULL, '2026-10-25 00:00:00.000+00', '2026-10-25 00:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000009', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Synthesizer dials, patch cables & modular sound sculpting 🎚️🔊 #music #synth #sounddesign #electronic #modular', NULL, NULL, '2026-10-25 02:00:00.000+00', '2026-10-25 02:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000010', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Studio vocal booth recording session with vintage condenser mic 🎙️🎵 #music #recording #vocals #studio #artist', NULL, NULL, '2026-10-25 04:00:00.000+00', '2026-10-25 04:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000011', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Holding down the low end groove with 4-string electric bass 🎸🖤 #music #bass #bassguitar #rhythm #funk', NULL, NULL, '2026-10-25 06:00:00.000+00', '2026-10-25 06:00:00.000+00'),
    ('11111111-0004-4000-8000-000000000012', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'original', 'Sunset jam session with close friends by the campfire 🌇🎶 #music #jamsession #friends #singalong #memories', NULL, NULL, '2026-10-25 08:00:00.000+00', '2026-10-25 08:00:00.000+00'),

    -- Virat (Cricket 🏏)
    ('11111111-0005-4000-8000-000000000001', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'English willow bat & seasoned red leather ball ready for match day 🏏🔥 #cricket #matchday #willow #cricketlover #ready', NULL, NULL, '2026-10-25 10:00:00.000+00', '2026-10-25 10:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000002', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Stadium under dazzling floodlights ready for the championship final 🏟️✨ #cricket #stadium #floodlights #ipl #cricketfever', NULL, NULL, '2026-10-25 12:00:00.000+00', '2026-10-25 12:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000003', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', '6:00 AM net practice: Discipline, sweat, and relentless repetition 🏏💪 #cricket #training #nets #hardwork #discipline', NULL, NULL, '2026-10-25 14:00:00.000+00', '2026-10-25 14:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000004', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Padded up and locked in: Batting gloves, helmet & pads on the turf 🛡️🏏 #cricket #batting #gear #cricketkit #focus', NULL, NULL, '2026-10-25 16:00:00.000+00', '2026-10-25 16:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000005', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'The pristine green oval pitch waiting for the morning coin toss 🌿🏏 #cricket #pitch #oval #crickettournament #summer', NULL, NULL, '2026-10-25 18:00:00.000+00', '2026-10-25 18:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000006', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Sprint training between the wickets: speed is the game changer 🏃‍♂️⚡ #cricket #fitness #sprints #running #athlete', NULL, NULL, '2026-10-25 20:00:00.000+00', '2026-10-25 20:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000007', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Wooden stumps & bails glowing in the afternoon cricket sun 🪵🏏 #cricket #stumps #bowled #wicket #cricketlife', NULL, NULL, '2026-10-25 22:00:00.000+00', '2026-10-25 22:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000008', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', '80,000 passionate fans roaring on every single boundary delivery 📣🏟️ #cricket #crowd #cricketfans #passion #champions', NULL, NULL, '2026-10-26 00:00:00.000+00', '2026-10-26 00:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000009', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Walking out through the tunnel onto the pitch: pure adrenaline 🚶‍♂️🏏 #cricket #batsman #gameday #tunnel #determination', NULL, NULL, '2026-10-26 02:00:00.000+00', '2026-10-26 02:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000010', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Agility drills and core conditioning after intense batting sessions 🏋️‍♂️💯 #cricket #conditioning #gym #workout #athlete', NULL, NULL, '2026-10-26 04:00:00.000+00', '2026-10-26 04:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000011', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Lifting the championship trophy with the brothers who battled together 🏆🤝 #cricket #champions #trophy #teamspirit #victory', NULL, NULL, '2026-10-26 06:00:00.000+00', '2026-10-26 06:00:00.000+00'),
    ('11111111-0005-4000-8000-000000000012', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'original', 'Golden hour setting over the ground after 100 overs of hard cricket 🌅🏏 #cricket #sunset #sportsground #memories #cricketer', NULL, NULL, '2026-10-26 08:00:00.000+00', '2026-10-26 08:00:00.000+00')
ON CONFLICT (id) DO UPDATE SET
    author_id = EXCLUDED.author_id,
    kind = EXCLUDED.kind,
    text = EXCLUDED.text,
    created_at = EXCLUDED.created_at,
    updated_at = EXCLUDED.updated_at;

-- ----------------------------------------------------------------------------
-- 3. POST MEDIA (1 Media per Post = 60 Media Rows)
-- ----------------------------------------------------------------------------
INSERT INTO post_media (id, post_id, position, alt_text, width, height, small_url, large_url, created_at)
VALUES
    -- Deepika
    ('bbbbbbbb-0001-4000-8000-000000000001', '11111111-0001-4000-8000-000000000001', 0, 'Plate of creamy artisanal pasta with herbs and parmesan', 1080, 1350, 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1080&q=80', '2026-10-21 10:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000002', '11111111-0001-4000-8000-000000000002', 0, 'Juicy gourmet burger stacked high with melted cheese and fries', 1080, 1350, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1080&q=80', '2026-10-21 12:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000003', '11111111-0001-4000-8000-000000000003', 0, 'Beautiful wooden tray with assorted salmon, tuna, and roll sushi', 1080, 1350, 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1080&q=80', '2026-10-21 14:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000004', '11111111-0001-4000-8000-000000000004', 0, 'Woodfired pizza with bubbling mozzarella and fresh basil leaves', 1080, 1350, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1080&q=80', '2026-10-21 16:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000005', '11111111-0001-4000-8000-000000000005', 0, 'Artisanal bread topped with sliced avocado, sesame, and poached egg', 1080, 1350, 'https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1080&q=80', '2026-10-21 18:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000006', '11111111-0001-4000-8000-000000000006', 0, 'Bowl of rich broth ramen with chashu pork, egg, and green scallions', 1080, 1350, 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1080&q=80', '2026-10-21 20:00:00.000+00'),
    ('b5b56978-c9c6-4025-bade-c8e9a2939698', 'fd2875cd-6570-42c1-92e3-029888f9477c', 0, 'Stack of golden waffles decorated with strawberries, blueberries, and syrup', 1080, 1350, 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=1080&q=80', '2026-10-21 22:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000008', '11111111-0001-4000-8000-000000000008', 0, 'Three street tacos served on corn tortillas with onions and lime wedges', 1080, 1350, 'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=1080&q=80', '2026-10-22 00:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000009', '11111111-0001-4000-8000-000000000009', 0, 'Flaky golden croissants next to a ceramic cup of cappuccino with latte art', 1080, 1350, 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1080&q=80', '2026-10-22 02:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000010', '11111111-0001-4000-8000-000000000010', 0, 'Purple acai bowl arranged neatly with sliced bananas, chia seeds, and berries', 1080, 1350, 'https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=1080&q=80', '2026-10-22 04:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000011', '11111111-0001-4000-8000-000000000011', 0, 'Dark chocolate cake with flowing warm center and a scoop of vanilla ice cream', 1080, 1350, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=1080&q=80', '2026-10-22 06:00:00.000+00'),
    ('bbbbbbbb-0001-4000-8000-000000000012', '11111111-0001-4000-8000-000000000012', 0, 'Colorful stir-fried bell peppers, broccoli, and greens in a modern skillet', 1080, 1350, 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1080&q=80', '2026-10-22 08:00:00.000+00'),

    -- Sneha
    ('bbbbbbbb-0002-4000-8000-000000000001', '11111111-0002-4000-8000-000000000001', 0, 'Cluster of pink and white spring tulips in gentle morning sunlight', 1080, 1350, 'https://images.unsplash.com/photo-1520763185298-1b434c919102?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1520763185298-1b434c919102?auto=format&fit=crop&w=1080&q=80', '2026-10-22 10:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000002', '11111111-0002-4000-8000-000000000002', 0, 'Close-up of soft pink peony petals unfolding in a lush garden', 1080, 1350, 'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=1080&q=80', '2026-10-22 12:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000003', '11111111-0002-4000-8000-000000000003', 0, 'Vibrant sunflower head with a field of bright yellow blooms behind', 1080, 1350, 'https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=1080&q=80', '2026-10-22 14:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000004', '11111111-0002-4000-8000-000000000004', 0, 'White petals with yellow centers against natural green meadow grass', 1080, 1350, 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1080&q=80', '2026-10-22 16:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000005', '11111111-0002-4000-8000-000000000005', 0, 'Dramatic bunch of rich red roses with soft dark lighting', 1080, 1350, 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1080&q=80', '2026-10-22 18:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000006', '11111111-0002-4000-8000-000000000006', 0, 'Branches heavy with pale pink sakura cherry blossoms against blue sky', 1080, 1350, 'https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=1080&q=80', '2026-10-22 20:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000007', '11111111-0002-4000-8000-000000000007', 0, 'Rows of vivid violet lavender stretching into the sunset horizon', 1080, 1350, 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?auto=format&fit=crop&w=1080&q=80', '2026-10-22 22:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000008', '11111111-0002-4000-8000-000000000008', 0, 'Tiny delicate white chamomile blossoms in sharp focus', 1080, 1350, 'https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=1080&q=80', '2026-10-23 00:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000009', '11111111-0002-4000-8000-000000000009', 0, 'Purple and magenta orchid blooms curving gracefully from stem', 1080, 1350, 'https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?auto=format&fit=crop&w=1080&q=80', '2026-10-23 02:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000010', '11111111-0002-4000-8000-000000000010', 0, 'Macro photograph capturing crystal clear water droplets on flower petals', 1080, 1350, 'https://images.unsplash.com/photo-1469259943454-aa100abba749?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1469259943454-aa100abba749?auto=format&fit=crop&w=1080&q=80', '2026-10-23 04:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000011', '11111111-0002-4000-8000-000000000011', 0, 'Textured neutral pampas grass and preserved dried florals in modern vase', 1080, 1350, 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=1080&q=80', '2026-10-23 06:00:00.000+00'),
    ('bbbbbbbb-0002-4000-8000-000000000012', '11111111-0002-4000-8000-000000000012', 0, 'Mesmerizing geometric spiral of a vibrant coral dahlia bloom', 1080, 1350, 'https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=1080&q=80', '2026-10-23 08:00:00.000+00'),

    -- Asha Patel
    ('bbbbbbbb-0003-4000-8000-000000000001', '11111111-0003-4000-8000-000000000001', 0, 'Open notebook with handwritten study notes, fountain pen, and study supplies', 1080, 1350, 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1080&q=80', '2026-10-23 10:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000002', '11111111-0003-4000-8000-000000000002', 0, 'Pile of hardcover vintage books beside a hot ceramic coffee cup', 1080, 1350, 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=1080&q=80', '2026-10-23 12:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000003', '11111111-0003-4000-8000-000000000003', 0, 'Comfortable armchair with warm knitted throw blanket and open paperback', 1080, 1350, 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1080&q=80', '2026-10-23 14:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000004', '11111111-0003-4000-8000-000000000004', 0, 'Tall dark oak bookshelves in a quiet grand university library', 1080, 1350, 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1080&q=80', '2026-10-23 16:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000005', '11111111-0003-4000-8000-000000000005', 0, 'Warm evening sunlight illuminating the printed pages of an open book', 1080, 1350, 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1080&q=80', '2026-10-23 18:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000006', '11111111-0003-4000-8000-000000000006', 0, 'Leather-bound journal open on wooden table with elegant black ink pen', 1080, 1350, 'https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?auto=format&fit=crop&w=1080&q=80', '2026-10-23 20:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000007', '11111111-0003-4000-8000-000000000007', 0, 'Neat study desk with silver laptop, wireframe notebook, and small succulent', 1080, 1350, 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=1080&q=80', '2026-10-23 22:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000008', '11111111-0003-4000-8000-000000000008', 0, 'Classic round reading glasses sitting on top of an old printed novel', 1080, 1350, 'https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1080&q=80', '2026-10-24 00:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000009', '11111111-0003-4000-8000-000000000009', 0, 'Bright sunlit desk next to leafy monstera plants with textbooks open', 1080, 1350, 'https://images.unsplash.com/photo-1519791883288-dc8bd696e667?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1519791883288-dc8bd696e667?auto=format&fit=crop&w=1080&q=80', '2026-10-24 02:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000010', '11111111-0003-4000-8000-000000000010', 0, 'Full height white bookshelf packed with hundreds of organized books', 1080, 1350, 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1080&q=80', '2026-10-24 04:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000011', '11111111-0003-4000-8000-000000000011', 0, 'Pastel highlighters highlighting key terms on printed revision sheets', 1080, 1350, 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1080&q=80', '2026-10-24 06:00:00.000+00'),
    ('bbbbbbbb-0003-4000-8000-000000000012', '11111111-0003-4000-8000-000000000012', 0, 'Intimate bookstore corridor filled with stacked books and warm tungsten light', 1080, 1350, 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1080&q=80', '2026-10-24 08:00:00.000+00'),

    -- Anirudh
    ('bbbbbbbb-0004-4000-8000-000000000001', '11111111-0004-4000-8000-000000000001', 0, 'Wooden acoustic guitar leaning against a warm studio wall', 1080, 1350, 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=1080&q=80', '2026-10-24 10:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000002', '11111111-0004-4000-8000-000000000002', 0, 'Black and white keys of a polished grand piano in soft lighting', 1080, 1350, 'https://images.unsplash.com/photo-1520523839898-507127041490?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1520523839898-507127041490?auto=format&fit=crop&w=1080&q=80', '2026-10-24 12:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000003', '11111111-0004-4000-8000-000000000003', 0, 'Professional studio monitor headphones resting on audio mixing console', 1080, 1350, 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1080&q=80', '2026-10-24 14:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000004', '11111111-0004-4000-8000-000000000004', 0, 'Black vinyl record spinning on turntable with golden tonearm', 1080, 1350, 'https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=1080&q=80', '2026-10-24 16:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000005', '11111111-0004-4000-8000-000000000005', 0, 'Sunburst electric guitar resting beside an authentic tube amplifier', 1080, 1350, 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=1080&q=80', '2026-10-24 18:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000006', '11111111-0004-4000-8000-000000000006', 0, 'Custom drum kit with cymbals gleaming under stage colored lights', 1080, 1350, 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=1080&q=80', '2026-10-24 20:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000007', '11111111-0004-4000-8000-000000000007', 0, 'Close-up of a carved wooden violin resting beside printed sheet music', 1080, 1350, 'https://images.unsplash.com/photo-1612225330812-01a9c6b355ec?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1612225330812-01a9c6b355ec?auto=format&fit=crop&w=1080&q=80', '2026-10-24 22:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000008', '11111111-0004-4000-8000-000000000008', 0, 'Gleaming golden brass saxophone caught in moody jazz club lighting', 1080, 1350, 'https://images.unsplash.com/photo-1525994886773-080587e161c2?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1525994886773-080587e161c2?auto=format&fit=crop&w=1080&q=80', '2026-10-25 00:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000009', '11111111-0004-4000-8000-000000000009', 0, 'Hardware synthesizer front panel with illuminated buttons and sliders', 1080, 1350, 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1080&q=80', '2026-10-25 02:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000010', '11111111-0004-4000-8000-000000000010', 0, 'High-end studio condenser microphone mounted on boom arm with pop filter', 1080, 1350, 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=1080&q=80', '2026-10-25 04:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000011', '11111111-0004-4000-8000-000000000011', 0, 'Close-up on the thick steel strings and frets of an electric bass guitar', 1080, 1350, 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1080&q=80', '2026-10-25 06:00:00.000+00'),
    ('bbbbbbbb-0004-4000-8000-000000000012', '11111111-0004-4000-8000-000000000012', 0, 'Acoustic jam session outdoors during a golden sunset', 1080, 1350, 'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?auto=format&fit=crop&w=1080&q=80', '2026-10-25 08:00:00.000+00'),

    -- Virat
    ('bbbbbbbb-0005-4000-8000-000000000001', '11111111-0005-4000-8000-000000000001', 0, 'Classic wooden cricket bat and shining red leather ball lying on green grass', 1080, 1350, 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1080&q=80', '2026-10-25 10:00:00.000+00'),
    ('bbbbbbbb-0005-4000-8000-000000000002', '11111111-0005-4000-8000-000000000002', 0, 'Panoramic view of an enormous cricket stadium illuminated at night', 1080, 1350, 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=1080&q=80', '2026-10-25 12:00:00.000+00'),
    ('98a2e558-56f0-435e-9a38-ecf244890614', '11111111-0005-4000-8000-000000000003', 0, 'Cricket practice nets with player preparing to face incoming delivery', 1080, 1350, 'https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?auto=format&fit=crop&w=1080&q=80', '2026-10-25 14:00:00.000+00'),
    ('69328bca-c624-4701-bbc4-d47f808c7843', '11111111-0005-4000-8000-000000000004', 0, 'White leather cricket batting gloves and helmet resting on the ground', 1080, 1350, 'https://images.unsplash.com/photo-1593341646782-e0b495cff86d?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1593341646782-e0b495cff86d?auto=format&fit=crop&w=1080&q=80', '2026-10-25 16:00:00.000+00'),
    ('d659c041-9970-464e-a907-ea3ac363371f', '11111111-0005-4000-8000-000000000005', 0, 'Freshly mowed cricket pitch with white crease markings on green outfield', 1080, 1350, 'https://images.unsplash.com/photo-1589487391730-58f20eb2c308?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1589487391730-58f20eb2c308?auto=format&fit=crop&w=1080&q=80', '2026-10-25 18:00:00.000+00'),
    ('3191922f-3973-4571-b97a-20011048a9ea', '11111111-0005-4000-8000-000000000006', 0, 'Athlete in full sprint on the sports pitch practicing acceleration', 1080, 1350, 'https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=1080&q=80', '2026-10-25 20:00:00.000+00'),
    ('a2173e79-5bbc-48b9-b6cc-a199dda033b9', '11111111-0005-4000-8000-000000000007', 0, 'Three wooden cricket stumps with bails balanced on a grass wicket', 1080, 1350, 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1080&q=80', '2026-10-25 22:00:00.000+00'),
    ('840f5e2f-88b2-498c-be74-ff4c9a0ea55d', '11111111-0005-4000-8000-000000000008', 0, 'Packed stadium stands waving team flags and cheering with passion', 1080, 1350, 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1080&q=80', '2026-10-26 00:00:00.000+00'),
    ('8bb43f6f-a19e-4347-8773-3f50e5c9b04d', '11111111-0005-4000-8000-000000000009', 0, 'Cricketer with bat walking purposefully into the bright stadium sunshine', 1080, 1350, 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1080&q=80', '2026-10-26 02:00:00.000+00'),
    ('592b45f8-2a1f-47ec-ad8f-3f5790491e18', '11111111-0005-4000-8000-000000000010', 0, 'Fitness training workout with athletic equipment on turf', 1080, 1350, 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1080&q=80', '2026-10-26 04:00:00.000+00'),
    ('66c32d7d-0c1f-4914-aa3e-ff1144c4fcb5', '11111111-0005-4000-8000-000000000011', 0, 'Sports team celebrating victory and lifting a trophy together', 1080, 1350, 'https://images.unsplash.com/photo-1511886929837-354d827aae26?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1511886929837-354d827aae26?auto=format&fit=crop&w=1080&q=80', '2026-10-26 06:00:00.000+00'),
    ('7f114372-a843-4f85-8080-bd34bb6b529a', '11111111-0005-4000-8000-000000000012', 0, 'Dramatic golden sunset stretching across a tranquil cricket ground', 1080, 1350, 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=1080&q=80', 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=1080&q=80', '2026-10-26 08:00:00.000+00')
ON CONFLICT (id) DO UPDATE SET
    post_id = EXCLUDED.post_id,
    alt_text = EXCLUDED.alt_text,
    small_url = EXCLUDED.small_url,
    large_url = EXCLUDED.large_url;

-- ----------------------------------------------------------------------------
-- 4. FOLLOWS (Mutual Following Edges between the 5 Core Profiles)
-- ----------------------------------------------------------------------------
INSERT INTO follows (follower_id, following_id, status, created_at)
VALUES
    -- Deepika follows Asha, Sneha, Virat
    ('158469c3-4a2d-4bc6-bf96-5a7638847875', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'accepted', '2026-08-10 10:00:00.000+00'),
    ('158469c3-4a2d-4bc6-bf96-5a7638847875', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'accepted', '2026-08-10 10:01:00.000+00'),
    ('158469c3-4a2d-4bc6-bf96-5a7638847875', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'accepted', '2026-08-10 10:02:00.000+00'),

    -- Sneha follows Deepika, Asha, Virat, Anirudh
    ('bd4c55d9-31f3-42e9-a210-e1355a77101f', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'accepted', '2026-08-10 10:03:00.000+00'),
    ('bd4c55d9-31f3-42e9-a210-e1355a77101f', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'accepted', '2026-08-10 10:04:00.000+00'),
    ('bd4c55d9-31f3-42e9-a210-e1355a77101f', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'accepted', '2026-08-10 10:05:00.000+00'),
    ('bd4c55d9-31f3-42e9-a210-e1355a77101f', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'accepted', '2026-08-10 10:06:00.000+00'),

    -- Asha follows Deepika, Sneha, Anirudh
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'accepted', '2026-08-10 10:07:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'accepted', '2026-08-10 10:08:00.000+00'),
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'accepted', '2026-08-10 10:09:00.000+00'),

    -- Anirudh follows Deepika, Virat, Asha
    ('250070da-0c2b-4a91-8d1a-180a9a2d1781', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'accepted', '2026-08-10 10:10:00.000+00'),
    ('250070da-0c2b-4a91-8d1a-180a9a2d1781', '26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'accepted', '2026-08-10 10:11:00.000+00'),
    ('250070da-0c2b-4a91-8d1a-180a9a2d1781', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'accepted', '2026-08-10 10:12:00.000+00'),

    -- Virat follows Anirudh, Deepika, Sneha
    ('26ee15b1-6f04-4c8f-9cf5-61e28c5472db', '250070da-0c2b-4a91-8d1a-180a9a2d1781', 'accepted', '2026-08-10 10:13:00.000+00'),
    ('26ee15b1-6f04-4c8f-9cf5-61e28c5472db', '158469c3-4a2d-4bc6-bf96-5a7638847875', 'accepted', '2026-08-10 10:14:00.000+00'),
    ('26ee15b1-6f04-4c8f-9cf5-61e28c5472db', 'bd4c55d9-31f3-42e9-a210-e1355a77101f', 'accepted', '2026-08-10 10:15:00.000+00')
ON CONFLICT (follower_id, following_id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. POST LIKES (Clean Initial Reactions)
-- ----------------------------------------------------------------------------
INSERT INTO post_likes (user_id, post_id, created_at)
VALUES
    -- Sneha likes Deepika's waffle post
    ('bd4c55d9-31f3-42e9-a210-e1355a77101f', 'fd2875cd-6570-42c1-92e3-029888f9477c', '2026-10-21 22:30:00.000+00'),
    -- Asha likes Sneha's tulip post
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', '11111111-0002-4000-8000-000000000001', '2026-10-22 10:30:00.000+00'),
    -- Deepika likes Asha's library post
    ('158469c3-4a2d-4bc6-bf96-5a7638847875', '11111111-0003-4000-8000-000000000004', '2026-10-23 16:30:00.000+00'),
    -- Virat likes Anirudh's drum kit post
    ('26ee15b1-6f04-4c8f-9cf5-61e28c5472db', '11111111-0004-4000-8000-000000000006', '2026-10-24 20:30:00.000+00'),
    -- Anirudh likes Virat's trophy post
    ('250070da-0c2b-4a91-8d1a-180a9a2d1781', '11111111-0005-4000-8000-000000000011', '2026-10-26 06:30:00.000+00')
ON CONFLICT (user_id, post_id) DO NOTHING;
