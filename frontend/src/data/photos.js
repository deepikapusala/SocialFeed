/**
 * Mock dataset representing Instagram posts.
 * 12 posts across 12 distinct topics.
 * Each post contains exactly 3 relevant carousel images, matching captions, and thematic tags.
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
    caption: 'Candid shadows and golden light bouncing off the downtown avenues during evening rush hour. 🏙️🚶 #streetphotography #urbanlife #cityscape #candid #streetvibes',
    likes: 1540,
    likedBy: 'marcus_snaps',
    timeAgo: '4 hours ago',
    images: [
      'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=800&q=80',
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
    userAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
    category: 'Astronomy',
    aspectRatio: 'landscape',
    caption: 'Stargazing under the Milky Way core far away from city lights. The sheer scale of the cosmos is humbling. 🌌✨ #astrophotography #space #milkyway #nightsky #stargazing',
    likes: 4200,
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
    likedBy: 'mindful_living',
    timeAgo: '18 hours ago',
    images: [
      'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
    ]
  },
];

// Alias for backward compatibility
export const photos = posts;

/**
 * Helper to build responsive srcset strings for image URLs that support width parameters.
 */
export function getResponsiveSrcSet(url) {
  if (!url) return '';
  if (url.includes('unsplash.com')) {
    const baseUrl = url.split('&w=')[0].split('?')[0];
    return `${baseUrl}?auto=format&fit=crop&w=400&q=80 400w, ${baseUrl}?auto=format&fit=crop&w=800&q=80 800w, ${baseUrl}?auto=format&fit=crop&w=1200&q=80 1200w`;
  }
  return `${url} 1x`;
}
