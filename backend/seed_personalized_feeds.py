import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete, text
from app.database import get_async_sessionmaker
from app.models.user import User
from app.models.post import Post
from app.models.media import PostMedia
from app.models.like import PostLike
from app.models.follow import Follow

# 5 Profiles with exactly 12 posts each (1 image per post)
CATEGORY_DATA = {
    "deepu": {
        "category": "Food",
        "posts": [
            {
                "text": "Artisanal homemade truffle pasta with freshly shaved parmesan 🍝✨ #food #pasta #italian #delicious #foodie",
                "alt": "Plate of creamy artisanal pasta with herbs and parmesan",
                "url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "The ultimate double cheeseburger with caramelized onions & crispy fries 🍔🍟 #food #burger #cheatmeal #comfortfood",
                "alt": "Juicy gourmet burger stacked high with melted cheese and fries",
                "url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Freshly crafted sushi nigiri & sashimi selection 🍣🍱 #food #sushi #japanesefood #fresh #foodporn",
                "alt": "Beautiful wooden tray with assorted salmon, tuna, and roll sushi",
                "url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Authentic woodfired Margherita pizza straight from the stone oven 🍕🌿 #food #pizza #woodfired #napoli #crust",
                "alt": "Woodfired pizza with bubbling mozzarella and fresh basil leaves",
                "url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Golden sourdough avocado toast with a runny poached egg 🥑🍳 #food #brunch #healthyfood #avocadotoast #breakfast",
                "alt": "Artisanal bread topped with sliced avocado, sesame, and poached egg",
                "url": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Steaming bowl of spicy tonkotsu ramen with soft-boiled ajitsuke egg 🍜🥢 #food #ramen #noodles #comfortfood #tokyo",
                "alt": "Bowl of rich broth ramen with chashu pork, egg, and green scallions",
                "url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Warm Belgian waffles loaded with fresh berries & pure maple syrup 🧇🍓 #food #waffles #dessert #sweettooth #brunch",
                "alt": "Stack of golden waffles decorated with strawberries, blueberries, and syrup",
                "url": "https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Authentic street tacos with charred salsa, cilantro & fresh lime 🌮🔥 #food #tacos #mexicanfood #streetfood #flavor",
                "alt": "Three street tacos served on corn tortillas with onions and lime wedges",
                "url": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Buttery Parisian croissants paired with freshly brewed velvet cappuccino 🥐☕ #food #pastry #croissant #cafe #paris",
                "alt": "Flaky golden croissants next to a ceramic cup of cappuccino with latte art",
                "url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Vibrant antioxidant acai smoothie bowl with granola & tropical kiwi 🥣🥝 #food #acaibowl #healthy #vegan #energy",
                "alt": "Purple acai bowl arranged neatly with sliced bananas, chia seeds, and berries",
                "url": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Warm molten chocolate lava cake with vanilla bean gelato 🍫🍨 #food #chocolate #dessert #baking #yummy",
                "alt": "Dark chocolate cake with flowing warm center and a scoop of vanilla ice cream",
                "url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Sizzling wok vegetables & teriyaki glazed tofu over jasmine rice 🥗🥢 #food #stirfry #healthyfood #organic #dinner",
                "alt": "Colorful stir-fried bell peppers, broccoli, and greens in a modern skillet",
                "url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1080&q=80",
            },
        ],
    },
    "sneha": {
        "category": "Flowers",
        "posts": [
            {
                "text": "A soft pastel bouquet of Dutch tulips to brighten the morning 🌷☀️ #flowers #tulips #spring #nature #bloom",
                "alt": "Cluster of pink and white spring tulips in gentle morning sunlight",
                "url": "https://images.unsplash.com/photo-1520763185298-1b434c919102?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Fluffy garden peonies in full romantic bloom 🌸🌿 #flowers #peonies #floral #aesthetic #garden",
                "alt": "Close-up of soft pink peony petals unfolding in a lush garden",
                "url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Endless golden sunflowers turning toward the warmth of the sun 🌻💛 #flowers #sunflower #summer #fields #goldenhour",
                "alt": "Vibrant sunflower head with a field of bright yellow blooms behind",
                "url": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Wild alpine daisies blooming freely in the morning breeze 🌼🏔️ #flowers #daisies #wildflowers #nature #peace",
                "alt": "White petals with yellow centers against natural green meadow grass",
                "url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Deep crimson velvety roses arranged in an artisanal ceramic vase 🌹✨ #flowers #roses #redroses #love #botanical",
                "alt": "Dramatic bunch of rich red roses with soft dark lighting",
                "url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Delicate cherry blossoms signaling the arrival of spring 🌸🍃 #flowers #cherryblossom #sakura #springtime #japan",
                "alt": "Branches heavy with pale pink sakura cherry blossoms against blue sky",
                "url": "https://images.unsplash.com/photo-1522383225653-ed111181a951?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Breathing in the calming fragrance of Provence lavender fields 💜🌾 #flowers #lavender #purple #calm #aromatherapy",
                "alt": "Rows of vivid violet lavender stretching into the sunset horizon",
                "url": "https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Pure white chamomile flowers basking in afternoon sunlight 🌼🍵 #flowers #chamomile #herbal #simplicity #clean",
                "alt": "Tiny delicate white chamomile blossoms in sharp focus",
                "url": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Exotic moth orchids showing off intricate natural geometric patterns 🌺🌿 #flowers #orchids #botany #plantlove #indoorplants",
                "alt": "Purple and magenta orchid blooms curving gracefully from stem",
                "url": "https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Morning dew droplets resting delicately on fresh flower petals 💧🌸 #flowers #dew #morninglight #macro #beauty",
                "alt": "Macro photograph capturing crystal clear water droplets on flower petals",
                "url": "https://images.unsplash.com/photo-1469259943454-aa100abba749?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Earthy dried floral bouquet bringing cozy warm tones to the room 🌾🏺 #flowers #driedflowers #neutraldecor #interiors #aesthetic",
                "alt": "Textured neutral pampas grass and preserved dried florals in modern vase",
                "url": "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Spectacular multicolored dahlia unfolding with hundreds of layered petals 🏵️🎨 #flowers #dahlia #natureart #colors #botanical",
                "alt": "Mesmerizing geometric spiral of a vibrant coral dahlia bloom",
                "url": "https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=1080&q=80",
            },
        ],
    },
    "asha": {
        "category": "Books & Study",
        "posts": [
            {
                "text": "A productive morning study session with clean stationery & hot matcha 📖✍️ #study #books #studygram #notes #focus",
                "alt": "Open notebook with handwritten study notes, fountain pen, and study supplies",
                "url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "A stack of timeless classic literature accompanied by dark roast espresso 📚☕ #books #reading #classicliterature #bookworm #cafe",
                "alt": "Pile of hardcover vintage books beside a hot ceramic coffee cup",
                "url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Curling up in my favorite reading nook while rain taps against the glass 🌧️🛋️ #books #cozy #readingnook #hygge #booklover",
                "alt": "Comfortable armchair with warm knitted throw blanket and open paperback",
                "url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Lost in the majestic silence of the historic university library aisles 🏛️📜 #books #library #architecture #studytime #academia",
                "alt": "Tall dark oak bookshelves in a quiet grand university library",
                "url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Golden hour rays falling across the open pages of a beloved novel 🌅📖 #books #sunset #goldenhour #peaceful #mindfulness",
                "alt": "Warm evening sunlight illuminating the printed pages of an open book",
                "url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Morning journaling routine to organize thoughts before a busy day 📝✒️ #study #journaling #stationery #productivity #routine",
                "alt": "Leather-bound journal open on wooden table with elegant black ink pen",
                "url": "https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Minimalist study desk setup: laptop, clean notepad, and green plant 💻🌱 #study #desksetup #minimalism #workspace #studentlife",
                "alt": "Neat study desk with silver laptop, wireframe notebook, and small succulent",
                "url": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Reading glasses resting atop yellowed vintage book pages 👓📖 #books #vintage #aesthetic #reader #literary",
                "alt": "Classic round reading glasses sitting on top of an old printed novel",
                "url": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Deep focus session by the window surrounded by natural green plants 🌿☀️ #study #plants #focus #studyinspo #daylight",
                "alt": "Bright sunlit desk next to leafy monstera plants with textbooks open",
                "url": "https://images.unsplash.com/photo-1519791883288-dc8bd696e667?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "My dream wall-to-wall personal home library finally taking shape 📚🏰 #books #homelibrary #bookshelf #collection #goals",
                "alt": "Full height white bookshelf packed with hundreds of organized books",
                "url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Color-coded highlighters & revision flashcards for upcoming exams 🖍️📑 #study #examseason #revision #prep #motivation",
                "alt": "Pastel highlighters highlighting key terms on printed revision sheets",
                "url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Browsing dusty shelves in a hidden secondhand bookstore in the city 🏷️📚 #books #bookshop #secondhand #treasure #explore",
                "alt": "Intimate bookstore corridor filled with stacked books and warm tungsten light",
                "url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1080&q=80",
            },
        ],
    },
    "ani": {
        "category": "Music",
        "posts": [
            {
                "text": "Warm acoustic guitar chords filling the quiet evening room 🎸🕯️ #music #guitar #acoustic #musician #chords",
                "alt": "Wooden acoustic guitar leaning against a warm studio wall",
                "url": "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Practicing Chopin nocturnes on the grand piano keys 🎹🎼 #music #piano #classical #pianist #keys",
                "alt": "Black and white keys of a polished grand piano in soft lighting",
                "url": "https://images.unsplash.com/photo-1520523839898-507127041490?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Mixing a new ambient electronic track in the home studio 🎧🎛️ #music #producer #mixing #homestudio #beats",
                "alt": "Professional studio monitor headphones resting on audio mixing console",
                "url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Spinning 70s vinyl on the vintage turntable needle 🎶📻 #music #vinyl #turntable #vintageaudio #analog",
                "alt": "Black vinyl record spinning on turntable with golden tonearm",
                "url": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Plugging into the vintage tube amplifier for a midnight guitar session ⚡🎸 #music #electricguitar #rock #fender #riff",
                "alt": "Sunburst electric guitar resting beside an authentic tube amplifier",
                "url": "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Ready behind the drum kit under vibrant stage floodlights 🥁🔥 #music #drums #drummer #livemusic #groove",
                "alt": "Custom drum kit with cymbals gleaming under stage colored lights",
                "url": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "The expressive richness of the wooden classical violin 🎻✨ #music #violin #orchestra #strings #harmony",
                "alt": "Close-up of a carved wooden violin resting beside printed sheet music",
                "url": "https://images.unsplash.com/photo-1612225330812-01a9c6b355ec?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Late night jazz club melodies flowing through brass saxophone 🎷🌙 #music #saxophone #jazz #brass #smooth",
                "alt": "Gleaming golden brass saxophone caught in moody jazz club lighting",
                "url": "https://images.unsplash.com/photo-1525994886773-080587e161c2?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Synthesizer dials, patch cables & modular sound sculpting 🎚️🔊 #music #synth #sounddesign #electronic #modular",
                "alt": "Hardware synthesizer front panel with illuminated buttons and sliders",
                "url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Studio vocal booth recording session with vintage condenser mic 🎙️🎵 #music #recording #vocals #studio #artist",
                "alt": "High-end studio condenser microphone mounted on boom arm with pop filter",
                "url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Holding down the low end groove with 4-string electric bass 🎸🖤 #music #bass #bassguitar #rhythm #funk",
                "alt": "Close-up on the thick steel strings and frets of an electric bass guitar",
                "url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Sunset jam session with close friends by the campfire 🌇🎶 #music #jamsession #friends #singalong #memories",
                "alt": "Acoustic jam session outdoors during a golden sunset",
                "url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?auto=format&fit=crop&w=1080&q=80",
            },
        ],
    },
    "virat": {
        "category": "Cricket",
        "posts": [
            {
                "text": "English willow bat & seasoned red leather ball ready for match day 🏏🔥 #cricket #matchday #willow #cricketlover #ready",
                "alt": "Classic wooden cricket bat and shining red leather ball lying on green grass",
                "url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Stadium under dazzling floodlights ready for the championship final 🏟️✨ #cricket #stadium #floodlights #ipl #cricketfever",
                "alt": "Panoramic view of an enormous cricket stadium illuminated at night",
                "url": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "6:00 AM net practice: Discipline, sweat, and relentless repetition 🏏💪 #cricket #training #nets #hardwork #discipline",
                "alt": "Cricket practice nets with player preparing to face incoming delivery",
                "url": "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Padded up and locked in: Batting gloves, helmet & pads on the turf 🛡️🏏 #cricket #batting #gear #cricketkit #focus",
                "alt": "White leather cricket batting gloves and helmet resting on the ground",
                "url": "https://images.unsplash.com/photo-1593341646782-e0b495cff86d?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "The pristine green oval pitch waiting for the morning coin toss 🌿🏏 #cricket #pitch #oval #crickettournament #summer",
                "alt": "Freshly mowed cricket pitch with white crease markings on green outfield",
                "url": "https://images.unsplash.com/photo-1589487391730-58f20eb2c308?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Sprint training between the wickets: speed is the game changer 🏃‍♂️⚡ #cricket #fitness #sprints #running #athlete",
                "alt": "Athlete in full sprint on the sports pitch practicing acceleration",
                "url": "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Wooden stumps & bails glowing in the afternoon cricket sun 🪵🏏 #cricket #stumps #bowled #wicket #cricketlife",
                "alt": "Three wooden cricket stumps with bails balanced on a grass wicket",
                "url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "80,000 passionate fans roaring on every single boundary delivery 📣🏟️ #cricket #crowd #cricketfans #passion #champions",
                "alt": "Packed stadium stands waving team flags and cheering with passion",
                "url": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Walking out through the tunnel onto the pitch: pure adrenaline 🚶‍♂️🏏 #cricket #batsman #gameday #tunnel #determination",
                "alt": "Cricketer with bat walking purposefully into the bright stadium sunshine",
                "url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Agility drills and core conditioning after intense batting sessions 🏋️‍♂️💯 #cricket #conditioning #gym #workout #athlete",
                "alt": "Fitness training workout with athletic equipment on turf",
                "url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Lifting the championship trophy with the brothers who battled together 🏆🤝 #cricket #champions #trophy #teamspirit #victory",
                "alt": "Sports team celebrating victory and lifting a trophy together",
                "url": "https://images.unsplash.com/photo-1511886929837-354d827aae26?auto=format&fit=crop&w=1080&q=80",
            },
            {
                "text": "Golden hour setting over the ground after 100 overs of hard cricket 🌅🏏 #cricket #sunset #sportsground #memories #cricketer",
                "alt": "Dramatic golden sunset stretching across a tranquil cricket ground",
                "url": "https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=1080&q=80",
            },
        ],
    },
}

async def main():
    session_factory = get_async_sessionmaker()
    async with session_factory() as session:
        # 1. Fetch user mapping
        res = await session.execute(select(User))
        all_users = {u.handle: u for u in res.scalars().all()}
        print(f"Users found in DB: {list(all_users.keys())}")

        for handle in CATEGORY_DATA.keys():
            if handle not in all_users:
                print(f"Error: user @{handle} missing!")
                return

        # 2. Clean up existing original posts and post media to establish the exact 60 curated posts
        print("Cleaning up old posts to install fresh 60 personalized posts (12 per profile)...")
        await session.execute(delete(PostMedia))
        await session.execute(delete(PostLike))
        await session.execute(delete(Post))
        # Clear cross-follows between the 5 demo users so each feed is 100% dedicated to their category
        await session.execute(delete(Follow))
        await session.commit()
        print("Database posts & follows cleared cleanly.")

        # 3. Insert exactly 12 posts for each of the 5 profiles (Total 60 posts)
        # Each post has EXACTLY 1 photo (1 URL)
        base_time = datetime.now(timezone.utc) - timedelta(days=5)
        post_counter = 0

        for handle, data in CATEGORY_DATA.items():
            user = all_users[handle]
            category = data["category"]
            posts = data["posts"]

            print(f"\nSeeding {len(posts)} '{category}' posts for @{handle} ({user.display_name})...")

            for i, p_info in enumerate(posts):
                post_counter += 1
                post_id = uuid.uuid4()
                # Timestamp spaced out so post 12 is newest
                post_time = base_time + timedelta(hours=post_counter * 2)

                new_post = Post(
                    id=post_id,
                    author_id=user.id,
                    kind="original",
                    text=p_info["text"],
                    created_at=post_time,
                    updated_at=post_time,
                )
                session.add(new_post)

                # Add EXACTLY 1 media item (position 0)
                media_id = uuid.uuid4()
                new_media = PostMedia(
                    id=media_id,
                    post_id=post_id,
                    position=0,
                    alt_text=p_info["alt"],
                    width=1080,
                    height=1350,
                    small_url=p_info["url"],
                    large_url=p_info["url"],
                    created_at=post_time,
                )
                session.add(new_media)

            print(f"-> Successfully inserted 12 {category} posts for @{handle}.")

        await session.commit()
        print("\nAll 60 posts (12 per profile, 1 pic each) created successfully!")

if __name__ == "__main__":
    asyncio.run(main())
