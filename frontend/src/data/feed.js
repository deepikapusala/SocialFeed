/**
 * Mock dataset representing Instagram posts.
 * 15 curated posts across diverse topics.
 * Each post contains id, username, userAvatar, category, aspectRatio, caption, likes, comments, likedBy, timeAgo, and 3 distinct Unsplash images.
 */

export const posts = [
  {
    id: 1,
    username: 'yosemite_wanderer',
    userAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
    category: 'Nature',
    aspectRatio: 'landscape',
    caption: "Morning mist rising over pine forests and alpine lakes. Nature's quiet serenity never ceases to inspire. 🌲⛰️ #nature #wilderness #mountains #wanderlust #optoutside",
    likes: 1342,
    comments: 4,
    likedBy: 'alex_travels',
    timeAgo: '2 hours ago',
    images: [
      'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 2,
    username: 'atelier_canvas',
    userAvatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80',
    category: 'Art',
    aspectRatio: 'square',
    caption: 'Layers of texture and color on raw linen. Working through the new canvas collection in the studio today! 🎨✨ #art #oilpainting #contemporaryart #abstractart #fineart',
    likes: 890,
    comments: 7,
    likedBy: 'deepika_art',
    timeAgo: '3 hours ago',
    images: [
      'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1561214115-f2f134cc4912?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 3,
    username: 'street_lens',
    userAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
    category: 'Street Photography',
    aspectRatio: 'portrait',
    caption: 'Candid shadows and golden light bouncing off downtown avenues during evening rush hour. 🏙️🚶 #streetphotography #urbanlife #cityscape #candid #streetvibes',
    likes: 1540,
    comments: 5,
    likedBy: 'marcus_snaps',
    timeAgo: '4 hours ago',
    images: [
      'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 4,
    username: 'urban_geometry',
    userAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80',
    category: 'Architecture',
    aspectRatio: 'tall',
    caption: 'Curving geometric facades and monolithic concrete forms. Architectural harmony in the financial district. 🏛️📐 #architecture #modernarchitecture #geometry #facade #minimalist',
    likes: 1120,
    comments: 3,
    likedBy: 'archilovers',
    timeAgo: '5 hours ago',
    images: [
      'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1487958449943-2429e8be8625?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 5,
    username: 'culinary_atelier',
    userAvatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=150&q=80',
    category: 'Food',
    aspectRatio: 'square',
    caption: 'Plated perfection: fresh handmade pasta, infused olive oils, and wood-fired rustic flavors. Buon appetito! 🍝🌿 #food #gourmet #culinary #foodie #artisanfood',
    likes: 2180,
    comments: 9,
    likedBy: 'chef_clara',
    timeAgo: '6 hours ago',
    images: [
      'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 6,
    username: 'roastery_notes',
    userAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80',
    category: 'Coffee',
    aspectRatio: 'portrait',
    caption: 'Slow drip pour-overs and silky latte art to kickstart a productive morning at the local roastery. ☕🥐 #coffee #barista #latteart #coffeetime #specialtycoffee',
    likes: 1640,
    comments: 6,
    likedBy: 'caffeine_daily',
    timeAgo: '7 hours ago',
    images: [
      'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 7,
    username: 'coastal_drift',
    userAvatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80',
    category: 'Ocean',
    aspectRatio: 'landscape',
    caption: 'Crystal clear turquoise waters, rolling tides, and untouched coral shores. The rhythm of the ocean is timeless. 🌊🏝️ #ocean #beach #coastal #seascape #marinelife',
    likes: 2890,
    comments: 8,
    likedBy: 'ocean_escape',
    timeAgo: '8 hours ago',
    images: [
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 8,
    username: 'maison_vogue',
    userAvatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=150&q=80',
    category: 'Fashion',
    aspectRatio: 'portrait',
    caption: 'Minimalist silhouettes and timeless neutral tones. Autumn/Winter editorial mood board in full swing. 🧥🕶️ #fashion #editorial #ootd #minimaliststyle #streetwear',
    likes: 3410,
    comments: 7,
    likedBy: 'style_insider',
    timeAgo: '10 hours ago',
    images: [
      'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 9,
    username: 'cosmos_odyssey',
    userAvatar: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=150&q=80',
    category: 'Astronomy',
    aspectRatio: 'landscape',
    caption: 'Stargazing under the Milky Way core far away from city lights. The sheer scale of the cosmos is humbling. 🌌✨ #astrophotography #space #milkyway #nightsky #stargazing',
    likes: 4200,
    comments: 5,
    likedBy: 'astro_geeks',
    timeAgo: '12 hours ago',
    images: [
      'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 10,
    username: 'aegean_nomad',
    userAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
    category: 'Travel',
    aspectRatio: 'square',
    caption: 'Whitewashed stone pathways, blue domes, and endless Aegean sea views. Lost in Mediterranean bliss. 🇬🇷☀️ #travel #mediterranean #wanderlust #santorini #travelgram',
    likes: 2750,
    comments: 4,
    likedBy: 'wanderer_club',
    timeAgo: '14 hours ago',
    images: [
      'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 11,
    username: 'wild_chronicles',
    userAvatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80',
    category: 'Wildlife',
    aspectRatio: 'tall',
    caption: 'Close encounters on the morning safari drive. Capturing the grace and strength of the wild. 🦁🐘 #wildlife #naturephotography #safari #wildlifephotography #animals',
    likes: 3120,
    comments: 8,
    likedBy: 'safari_lovers',
    timeAgo: '16 hours ago',
    images: [
      'https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 12,
    username: 'prana_wellness',
    userAvatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80',
    category: 'Wellness',
    aspectRatio: 'portrait',
    caption: 'Sunrise flow and breathwork to ground the mind and energize the body. Balance starts from within. 🧘‍♀️🌅 #fitness #wellness #yoga #mindfulness #healthylifestyle',
    likes: 1980,
    comments: 3,
    likedBy: 'mindful_living',
    timeAgo: '18 hours ago',
    images: [
      'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 13,
    username: 'botanical_studio',
    userAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
    category: 'Botanical',
    aspectRatio: 'square',
    caption: 'Monstera variegata, lush ferns, and rare tropical foliage thriving under greenhouse glass. 🌿🌱 #plants #botanical #urbanjungle #houseplants',
    likes: 1420,
    comments: 6,
    likedBy: 'green_thumb',
    timeAgo: '1d ago',
    images: [
      'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 14,
    username: 'nordic_trails',
    userAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80',
    category: 'Adventure',
    aspectRatio: 'landscape',
    caption: 'Glacial fjords and mirror-still waters under the midnight sun. Pure Arctic serenity. ❄️🏔️ #norway #fjords #arctic #nordic #outdoors',
    likes: 2450,
    comments: 5,
    likedBy: 'yosemite_wanderer',
    timeAgo: '1d ago',
    images: [
      'https://images.unsplash.com/photo-1517411032315-54ef2cb783bb?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80',
    ]
  },
  {
    id: 15,
    username: 'minimal_spaces',
    userAvatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=150&q=80',
    category: 'Interiors',
    aspectRatio: 'portrait',
    caption: 'Warm oak timber, soft morning shadows, and clean architectural lines. Less is always more. 🛋️✨ #interiordesign #minimalism #japandi #architecture',
    likes: 1890,
    comments: 2,
    likedBy: 'urban_geometry',
    timeAgo: '2d ago',
    images: [
      'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80',
    ]
  }
];

// Compatibility exports
export const FEED_POSTS = posts;
export const EXTENDED_DEMO_POSTS = posts;
export const photos = posts;

/**
 * Returns a paginated batch of 10 posts with infinite scrolling loop.
 * After post 15, it seamlessly loops back to post 1, 2, 3...
 * Each looped post gets a unique compound ID so React keys and deduplication work seamlessly.
 */
export function getFeedPage(cursor = null, limit = 10) {
  let startOffset = 0;

  if (cursor !== null && cursor !== undefined) {
    const parsed = parseInt(cursor, 10);
    if (!isNaN(parsed)) {
      startOffset = parsed;
    } else {
      const cleanCursor = String(cursor).split('_')[0];
      const foundIdx = posts.findIndex((p) => String(p.id) === cleanCursor);
      if (foundIdx !== -1) {
        startOffset = foundIdx + 1;
      }
    }
  }

  const totalPosts = posts.length;
  const pageItems = [];

  for (let i = 0; i < limit; i++) {
    const globalIndex = startOffset + i;
    const baseIndex = globalIndex % totalPosts;
    const cycle = Math.floor(globalIndex / totalPosts);
    const basePost = posts[baseIndex];

    // For the initial cycle (0..14), keep standard id (1..15).
    // For subsequent infinite scroll loops, attach cycle suffix so React keys and sets never collide.
    const uniqueId = cycle === 0 ? basePost.id : `${basePost.id}_loop_${cycle}`;

    pageItems.push({
      ...basePost,
      id: uniqueId,
    });
  }

  const nextCursor = String(startOffset + limit);

  return {
    items: pageItems,
    nextCursor,
    hasMore: true, // Infinite scroll never ends!
  };
}

export const getExtendedDemoFeedPage = getFeedPage;
