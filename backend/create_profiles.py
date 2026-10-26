import asyncio
import uuid
from sqlalchemy import select, text
from app.database import get_async_sessionmaker
from app.models.user import User
from app.models.follow import Follow
from app.common.security import hash_password

PROFILES = [
    {
        "handle": "deepu",
        "display_name": "Deepika",
        "password": "deepika123",
        "bio": "Visual storyteller & designer ✨ | Chasing light & memories",
        "avatar_small": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
    },
    {
        "handle": "sneha",
        "display_name": "Sneha",
        "password": "sneha123",
        "bio": "Coffee, minimal aesthetics & design ☕🌿",
        "avatar_small": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
    },
    {
        "handle": "asha",
        "display_name": "Asha Patel",
        "password": "password123",
        "bio": "Photography enthusiast & urban explorer 📷",
        "avatar_small": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80",
    },
    {
        "handle": "ani",
        "display_name": "Anirudh",
        "password": "ani123",
        "bio": "Music, cityscapes & creative coding 🎧💻",
        "avatar_small": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
    },
    {
        "handle": "virat",
        "display_name": "Virat",
        "password": "virat123",
        "bio": "Athlete & explorer 🏃‍♂️ | Living life at 100%",
        "avatar_small": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
    },
]

async def main():
    session_factory = get_async_sessionmaker()
    async with session_factory() as session:
        user_map = {}

        # 1. Fetch all existing users
        res = await session.execute(select(User))
        existing_users = {u.handle: u for u in res.scalars().all()}
        print(f"Existing users in DB: {list(existing_users.keys())}")

        # 2. Insert or update the 5 requested profiles
        for p in PROFILES:
            handle = p["handle"]
            hashed_pw = await hash_password(p["password"])

            if handle in existing_users:
                u = existing_users[handle]
                u.display_name = p["display_name"]
                u.password_hash = hashed_pw
                u.bio = p["bio"]
                u.avatar_small_url = p["avatar_small"]
                u.avatar_large_url = p["avatar_large"]
                u.is_active = True
                print(f"Updated existing profile: @{handle} ({p['display_name']})")
                user_map[handle] = u
            else:
                new_id = uuid.uuid4()
                new_u = User(
                    id=new_id,
                    handle=handle,
                    display_name=p["display_name"],
                    bio=p["bio"],
                    avatar_small_url=p["avatar_small"],
                    avatar_large_url=p["avatar_large"],
                    password_hash=hashed_pw,
                    is_active=True,
                )
                session.add(new_u)
                print(f"Created new profile: @{handle} ({p['display_name']}) id={new_id}")
                user_map[handle] = new_u

        await session.commit()

        # Re-fetch users to get fresh IDs
        res = await session.execute(select(User))
        all_users = {u.handle: u for u in res.scalars().all()}

        # 3. Setup follows so all 5 profiles have interesting following feeds
        # Target creators who have popular posts in the database:
        seed_creators = [h for h in ["yosemite_wanderer", "atelier_canvas", "street_lens"] if h in all_users]

        # Each user follows seed creators + some of their fellow requested users
        follow_relations = [
            ("deepu", ["asha", "sneha"] + seed_creators),
            ("sneha", ["deepu", "asha", "virat"] + seed_creators),
            ("asha", ["deepu", "sneha", "ani"] + seed_creators),
            ("ani", ["deepu", "virat", "asha"] + seed_creators),
            ("virat", ["ani", "deepu", "sneha"] + seed_creators),
        ]

        for follower_handle, following_handles in follow_relations:
            if follower_handle not in all_users:
                continue
            follower = all_users[follower_handle]

            for target_handle in following_handles:
                if target_handle in all_users and target_handle != follower_handle:
                    target = all_users[target_handle]
                    # Check if already following
                    check = await session.execute(
                        select(Follow).where(
                            Follow.follower_id == follower.id,
                            Follow.following_id == target.id,
                        )
                    )
                    if not check.scalar_one_or_none():
                        session.add(Follow(follower_id=follower.id, following_id=target.id, status="accepted"))
                        print(f"Added follow: @{follower_handle} -> @{target_handle}")

        await session.commit()
        print("\nAll 5 profiles configured successfully!")
        for p in PROFILES:
            print(f"- {p['display_name']}: handle=@{p['handle']}, password={p['password']}")

if __name__ == "__main__":
    asyncio.run(main())
