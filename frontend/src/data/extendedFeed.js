/**
 * Extended 90-Post Demo Feed Dataset for Instagram Explore Grid.
 * Contains exactly 90 original posts, each with exactly 3 distinct media images
 * (270 media items total).
 * 
 * Supports deterministic cursor-based pagination:
 * (created_at DESC, id DESC)
 */

// Curated high quality image triplets for 90 distinct posts (3 images per post)
const THEMES = [
  {
    category: 'Nature & Wilderness',
    user: { handle: 'yosemite_wanderer', name: 'Marcus Thorne', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Morning mist rising over pine forests and alpine lakes. Nature quiet serenity never ceases to inspire. 🌲⛰️ #nature #wilderness #mountains #wanderlust',
      'Cascading waterfalls along the granite canyon trail. The sound of rushing water echoes through the valley. 💧🌲 #waterfall #granite #hiking #adventure',
      'Golden sunset illuminating the mountain peaks. Breathing in crisp alpine air at 10,000 feet. 🏔️✨ #sunset #alpine #peaks #outdoors',
      'Emerald river winding through deep mossy evergreen forests. Untouched wilderness at its finest. 🌿🏞️ #river #forest #moss #wildnature',
      'First autumn frost dusting the valley pines. Quiet transitions in the high country. ❄️🍂 #frost #autumn #winteriscoming #naturephotography',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1418065460487-3e41a6c84dc5?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Fine Art & Painting',
    user: { handle: 'atelier_canvas', name: 'Elena Rostova', avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Layers of texture and color on raw linen. Working through the new canvas collection in the studio today! 🎨✨ #art #oilpainting #contemporaryart #abstractart',
      'Mixing custom pigment tones on the wooden palette. Exploring deep cobalt blues and earthy ochres. 🖌️🎨 #palette #pigment #artstudio #fineart',
      'Charcoal sketches and preliminary studies for the upcoming gallery exhibition. 🖤✏️ #sketch #charcoal #drawing #gallery',
      'Vibrant acrylic glazes drying in the afternoon sun. Capturing light through semi-transparent layers. ☀️🎨 #acrylic #glaze #lightandshadow #artwork',
      'Studio corner details: well-loved brushes, linseed oil jars, and fresh canvas rolls. 🖼️🏺 #artiststudio #creativeprocess #studiovibes #workinprogress',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1561214115-f2f134cc4912?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1547891654-e66ed7ebb968?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1578925518470-4def7a0f08bb?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1582561424760-0321d75e81fa?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1577083552431-6e5fd01aa342?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1579783928621-7a13d66a62d1?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1579783901586-d88db74b4fe4?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1579783928621-7a13d66a62d1?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1580136579312-94651dfd596d?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Street & Urban Life',
    user: { handle: 'street_lens', name: 'David Kim', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Candid shadows and golden light bouncing off downtown avenues during evening rush hour. 🏙️🚶 #streetphotography #urbanlife #cityscape #candid',
      'Neon reflections and rainy asphalt in Shibuya crossing after midnight. 🌧️🏮 #nightphotography #tokyo #shibuya #cyberpunk',
      'Geometric subway tile patterns and fleeting commuter silhouettes. 🚇👥 #metro #commute #shadows #urbangeometry',
      'Vintage streetcar navigating historic downtown brick streets. Timeless city pulse. 🚋🌆 #streetcar #historic #citystreets #nostalgia',
      'Steaming alley food stalls and bustling night market energy. 🍜🏮 #nightmarket #streetfood #nightlife #vibes',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1492571350019-22de08371fd3?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1508873696983-2df5293cb32f?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1517732306149-e8f829eb588a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Architecture & Design',
    user: { handle: 'urban_geometry', name: 'Clara Vance', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Curving geometric facades and monolithic concrete forms. Architectural harmony in the financial district. 🏛️📐 #architecture #modernarchitecture #geometry',
      'Spiral staircase perspective from the museum atrium. Perfect mathematical rhythm. 🌀🏛️ #spiral #symmetry #stairs #atrium',
      'Brutalist concrete angles catching the early dawn shadows. Form follows function. 🏢📐 #brutalism #concrete #minimalist #building',
      'Glass curtain walls reflecting azure skies and cloudscapes. Modern skyline aesthetics. 🏙️☁️ #glass #reflection #skyline #highrise',
      'Cantilevered balconies and lush hanging gardens on a sustainable eco-tower. 🌿🏢 #greenbuilding #ecotower #sustainability #urbanliving',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1487958449943-2429e8be8625?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1487958449943-2429e8be8625?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1487958449943-2429e8be8625?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Gourmet & Culinary',
    user: { handle: 'culinary_atelier', name: 'Chef Clara Laurent', avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Plated perfection: fresh handmade pasta, infused olive oils, and wood-fired rustic flavors. Buon appetito! 🍝🌿 #food #gourmet #culinary #foodie',
      'Artisanal sourdough straight out of the hearth. That golden blistered crust is everything. 🍞🔥 #sourdough #baking #artisanbread #foodart',
      'Charred heirloom tomatoes with creamy burrata and basil microgreens. Summer harvest magic. 🍅🧀 #burrata #heirloom #fresh #farmtotable',
      'Tasting menu prep: seared scallops with saffron foam and pickled shallots. 🍽️✨ #finedining #chefmode #seafood #gourmet',
      'Decadent dark chocolate ganache tart with raspberry dust and sea salt flakes. 🍫🍓 #dessert #chocolate #pastrychef #sweettooth',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1549931319-a545dcf3bc73?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Coffee & Roastery',
    user: { handle: 'roastery_notes', name: 'Maya Lin', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Slow drip pour-overs and silky latte art to kickstart a productive morning at the local roastery. ☕🥐 #coffee #barista #latteart #coffeetime',
      'Dialing in the morning espresso extraction: notes of dark cherry, jasmine, and cocoa nibs. ☕✨ #espresso #coffeegrinder #singleorigin',
      'Freshly roasted Ethiopian Yirgacheffe beans cooling in the roaster drum. The aroma is unmatched. 🫘🔥 #roasting #ethiopiancoffee #specialtycoffee',
      'Cold brew towers slowly dripping through Japanese paper filters over 18 hours. 🧊⏳ #coldbrew #slowcoffee #pourover',
      'Afternoon quiet corner: a warm flat white, open notebook, and soft jazz. 🎶☕ #coffeeshop #flatwhite #mindfulness',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Ocean & Coastal',
    user: { handle: 'coastal_drift', name: 'Liam Brooks', avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Crystal clear turquoise waters, rolling tides, and untouched coral shores. The rhythm of the ocean is timeless. 🌊🏝️ #ocean #beach #coastal',
      'Surfing dawn patrol waves as sunlight breaks through morning sea spray. 🏄‍♂️🌅 #surfing #dawnpatrol #waves #oceanvibes',
      'Dramatic coastal sea cliffs battered by Pacific swell at high tide. 🌊🪨 #seacliffs #pacific #rugged #coastalwalk',
      'White sand dunes meeting sapphire waters on a hidden tropical cove. 🏖️🌴 #tropical #dunes #paradise #islandlife',
      'Bioluminescent waves glowing electric blue along the night shore. Pure natural wonder. ✨🌊 #bioluminescence #nightsea #oceanmagic',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1455729552865-3658a5d39692?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Fashion & Style',
    user: { handle: 'maison_vogue', name: 'Sophia Chen', avatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Minimalist silhouettes and timeless neutral tones. Autumn/Winter editorial mood board in full swing. 🧥🕶️ #fashion #editorial #ootd',
      'Tailored wool coats and structured leather accessories on the Parisian boulevards. 🇫🇷👢 #parisfashion #streetstyle #hautecouture',
      'Handcrafted silk scarves and delicate gold jewelry details in soft morning light. 🧣💍 #silk #accessories #finejewelry #details',
      'Monochrome layering: structured blazers paired with flowing pleated trousers. 🖤🤍 #monochrome #minimalism #tailoring',
      'Behind the scenes at Milan Fashion Week: final garment adjustments before the runway call. 👗✨ #mfw #runway #backstage #highfashion',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Astronomy & Cosmos',
    user: { handle: 'cosmos_odyssey', name: 'Dr. Neil Hunter', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Stargazing under the Milky Way core far away from city lights. The sheer scale of the cosmos is humbling. 🌌✨ #astrophotography #space #milkyway',
      'Aurora borealis dancing in vibrant emerald ribbons across the Arctic sky. 🌌❄️ #northernlights #aurora #arctic #nightsky',
      'Telescope deep-field capture of the Andromeda galaxy and distant star clusters. 🔭✨ #andromeda #galaxy #deepspace #astronomy',
      'Total solar eclipse corona glowing in ethereal silver against a pitch-black noon. 🌑☀️ #solareclipse #eclipse #corona #celestial',
      'Meteor trails burning across the Perseid shower above high mountain observatories. 🌠⛰️ #perseids #meteorshower #shootingstar',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1531306728370-e2ebd9d7bb99?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Travel & Exploration',
    user: { handle: 'aegean_nomad', name: 'Zoe Katsaros', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Whitewashed stone pathways, blue domes, and endless Aegean sea views. Lost in Mediterranean bliss. 🇬🇷☀️ #travel #mediterranean #wanderlust',
      'Sunrise over the fairy chimneys of Cappadocia with dozens of hot air balloons rising. 🎈🇹🇷 #cappadocia #hotairballoon #bucketlist',
      'Navigating the winding canals of Venice on an early morning wooden gondola ride. 🛶🇮🇹 #venice #canals #italy #gondola',
      'Old town Dubrovnik fortress walls overlooking the sparkling Adriatic sea. 🏰🇭🇷 #dubrovnik #adriatic #croatia #historic',
      'Ancient mossy temples and bamboo groves in the misty hills of Kyoto. ⛩️🎋 #kyoto #japan #temple #zen',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Wildlife & Nature',
    user: { handle: 'wild_chronicles', name: 'Tariq Ndlovu', avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Close encounters on the morning safari drive. Capturing the grace and strength of the wild. 🦁🐘 #wildlife #naturephotography #safari',
      'Majestic snow leopard surveying Himalayan rocky ridges from its high vantage point. 🐆🏔️ #snowleopard #mountains #endangered',
      'Playful sea otter floating on its back wrapped in giant kelp fronds. 🦦🌊 #seaotter #oceanwildlife #coastal #kelpforest',
      'Kingfisher perched motionless above the river rapids before a lightning dive. 🐦💦 #birdwatching #kingfisher #wildlifeplanet',
      'A herd of wild horses galloping through golden prairie grass at sunset. 🐎🌅 #wildhorses #prairie #freedom #goldenhour',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Wellness & Mindfulness',
    user: { handle: 'prana_wellness', name: 'Aria Sterling', avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Sunrise flow and breathwork to ground the mind and energize the body. Balance starts from within. 🧘‍♀️🌅 #fitness #wellness #yoga #mindfulness',
      'Ceremonial matcha whisked to perfection with oat foam. Mindful morning rituals. 🍵✨ #matcha #rituals #mindfulliving #greentea',
      'Sound bath meditation surrounded by brass singing bowls and eucalyptus steam. 🎶🌿 #soundbath #healing #meditation #innerpeace',
      'Forest bathing among ancient redwoods: reconnecting senses with the living earth. 🌲🧘‍♂️ #shinrinyoku #forestbathing #grounding',
      'Journaling intentions by candle light at dusk. Reflecting on gratitude and growth. 🕯️📖 #gratitude #journaling #selfcare',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  },
  {
    category: 'Botanical & Flora',
    user: { handle: 'botanical_studio', name: 'Jasmine Reed', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80' },
    captions: [
      'Monstera variegata and rare tropical foliage thriving under greenhouse glass. 🌿🌱 #plants #botanical #urbanjungle #houseplants',
      'Japanese bonsai maple with vibrant scarlet autumn leaves in a handcrafted clay pot. 🍁🪴 #bonsai #japanesemaple #gardening',
      'Desert succulent and cactus collection blooming with bright magenta flowers. 🌵🌸 #succulents #cactus #desertflora',
      'Macro study of morning dewdrops resting on fresh fern fronds. 💧🌿 #dewdrops #macro #fern #naturedetails',
      'Pressed flower botanicals and dried lavender bundles hanging in the herb shed. 💐🪻 #pressedflowers #lavender #herbal #apothecary',
    ],
    imageTriplets: [
      [
        'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&w=800&q=80'
      ],
      [
        'https://images.unsplash.com/photo-1463936575829-25148e1db1b8?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=800&q=80'
      ]
    ]
  }
];

// Generate deterministic 90 original posts
export const EXTENDED_DEMO_POSTS = [];

const BASE_TIMESTAMP = new Date('2026-09-01T12:00:00.000Z').getTime();

for (let i = 0; i < 90; i++) {
  const themeIndex = i % THEMES.length;
  const theme = THEMES[themeIndex];
  const variantIndex = Math.floor(i / THEMES.length) % theme.imageTriplets.length;

  const postId = `10000000-0000-4000-8000-${String(i + 1).padStart(12, '0')}`;
  const images = theme.imageTriplets[variantIndex];
  const caption = theme.captions[variantIndex] || theme.captions[0];
  const postTimeMs = BASE_TIMESTAMP - (i * 3600000 * 3); // 3 hours step between posts
  const createdAtIso = new Date(postTimeMs).toISOString();

  const postMedia = images.map((url, pos) => ({
    id: `20000000-0000-4000-8000-${String(i * 3 + pos + 1).padStart(12, '0')}`,
    postId: postId,
    position: pos,
    smallUrl: url.replace('w=800', 'w=400'),
    largeUrl: url,
    altText: `${theme.category} capture #${pos + 1} for ${theme.user.name}`,
    width: 1200,
    height: 800,
    createdAt: createdAtIso,
  }));

  EXTENDED_DEMO_POSTS.push({
    id: postId,
    kind: 'original',
    text: caption,
    caption: caption,
    category: theme.category,
    username: theme.user.handle,
    displayName: theme.user.name,
    userAvatar: theme.user.avatar,
    author: {
      id: `aaaaaaaa-aaaa-4aaa-8aaa-${String(themeIndex + 1).padStart(12, '0')}`,
      handle: theme.user.handle,
      displayName: theme.user.name,
      avatar: {
        smallUrl: theme.user.avatar,
        largeUrl: theme.user.avatar,
      },
    },
    media: postMedia,
    images: images,
    imageUrl: images[0],
    hasMedia: true,
    alt: postMedia[0].altText,
    likes: 850 + ((i * 137) % 2400),
    likeCount: 850 + ((i * 137) % 2400),
    replyCount: 2 + ((i * 19) % 28),
    likedByViewer: i % 4 === 0,
    createdAt: createdAtIso,
    timeAgo: `${Math.floor(i / 8) + 1}d ago`,
  });
}

/**
 * Returns a paginated slice of the 90-post demo feed using cursor pagination.
 */
export function getExtendedDemoFeedPage(cursor = null, limit = 10) {
  let startIndex = 0;
  if (cursor) {
    try {
      // Decode base64 cursor token
      const decodedJson = atob(cursor.replace(/-/g, '+').replace(/_/g, '/'));
      const parsed = JSON.parse(decodedJson);
      const foundIdx = EXTENDED_DEMO_POSTS.findIndex((p) => p.id === parsed.id);
      if (foundIdx !== -1) {
        startIndex = foundIdx + 1;
      }
    } catch {
      // If cursor is plain index or ID
      const foundIdx = EXTENDED_DEMO_POSTS.findIndex((p) => p.id === cursor);
      if (foundIdx !== -1) {
        startIndex = foundIdx + 1;
      }
    }
  }

  const pageItems = EXTENDED_DEMO_POSTS.slice(startIndex, startIndex + limit);
  const hasMore = startIndex + limit < EXTENDED_DEMO_POSTS.length;

  let nextCursor = null;
  if (hasMore && pageItems.length > 0) {
    const lastItem = pageItems[pageItems.length - 1];
    const cursorPayload = {
      v: 1,
      createdAt: lastItem.createdAt,
      id: lastItem.id,
    };
    const rawJson = JSON.stringify(cursorPayload);
    nextCursor = btoa(rawJson).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  return {
    items: pageItems,
    nextCursor,
    hasMore,
  };
}
