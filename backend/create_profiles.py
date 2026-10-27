"""
Script to create and maintain the 5 core demo profiles.
Ensures strictly the 5 core profiles exist with consistent UUIDs,
credentials, bios, avatars, and clean mutual follows.
"""

import asyncio
import uuid
from sqlalchemy import select, delete
from app.database import get_async_sessionmaker
from app.models.user import User
from app.models.follow import Follow
from app.models.session import Session
from app.models.notification import Notification
from app.common.security import hash_password

PROFILES = [
    {
        "id": uuid.UUID("158469c3-4a2d-4bc6-bf96-5a7638847875"),
        "handle": "deepu",
        "display_name": "Deepika",
        "password": "deepika123",
        "bio": "Artisanal recipes & gourmet food photography ✨🍝",
        "avatar_small": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": uuid.UUID("bd4c55d9-31f3-42e9-a210-e1355a77101f"),
        "handle": "sneha",
        "display_name": "Sneha",
        "password": "sneha123",
        "bio": "Botanical aesthetics & garden flora 🌿🌸",
        "avatar_small": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        "handle": "asha",
        "display_name": "Asha Patel",
        "password": "password123",
        "bio": "Book lover, stationery & study aesthetic 📖📚",
        "avatar_small": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": uuid.UUID("250070da-0c2b-4a91-8d1a-180a9a2d1781"),
        "handle": "ani",
        "display_name": "Anirudh",
        "password": "ani123",
        "bio": "Acoustic jams, audio production & beats 🎧🎸",
        "avatar_small": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
    },
    {
        "id": uuid.UUID("26ee15b1-6f04-4c8f-9cf5-61e28c5472db"),
        "handle": "virat",
        "display_name": "Virat",
        "password": "virat123",
        "bio": "Match day passion, fitness & willow cricket 🏏⚡",
        "avatar_small": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80",
        "avatar_large": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
    },
]


async def main():
    session_factory = get_async_sessionmaker()
    target_ids = [p["id"] for p in PROFILES]

    async with session_factory() as session:
        # 1. Upsert exactly the 5 target profiles
        for p in PROFILES:
            handle = p["handle"]
            hashed_pw = await hash_password(p["password"])

            res = await session.execute(select(User).where(User.id == p["id"]))
            user = res.scalar_one_or_none()
            if not user:
                res_h = await session.execute(select(User).where(User.handle == handle))
                user = res_h.scalar_one_or_none()

            if user:
                user.id = p["id"]
                user.handle = handle
                user.display_name = p["display_name"]
                user.password_hash = hashed_pw
                user.bio = p["bio"]
                user.avatar_small_url = p["avatar_small"]
                user.avatar_large_url = p["avatar_large"]
                user.is_active = True
                user.is_private = False
                print(f"Updated profile: @{handle} ({p['display_name']})")
            else:
                new_u = User(
                    id=p["id"],
                    handle=handle,
                    display_name=p["display_name"],
                    bio=p["bio"],
                    avatar_small_url=p["avatar_small"],
                    avatar_large_url=p["avatar_large"],
                    password_hash=hashed_pw,
                    is_active=True,
                    is_private=False,
                )
                session.add(new_u)
                print(f"Created profile: @{handle} ({p['display_name']}) id={p['id']}")

        await session.commit()

        # 2. Remove any old/unnecessary accounts outside the 5 profiles
        del_notifs = await session.execute(
            delete(Notification).where(
                ~Notification.recipient_id.in_(target_ids) | ~Notification.actor_id.in_(target_ids)
            )
        )
        del_sessions = await session.execute(
            delete(Session).where(~Session.user_id.in_(target_ids))
        )
        del_follows = await session.execute(
            delete(Follow).where(
                ~Follow.follower_id.in_(target_ids) | ~Follow.following_id.in_(target_ids)
            )
        )
        del_users = await session.execute(
            delete(User).where(~User.id.in_(target_ids))
        )
        if del_users.rowcount > 0:
            print(f"Cleaned up {del_users.rowcount} obsolete users outside the 5 profiles.")

        await session.commit()

        # 3. Establish mutual follows among the 5 profiles
        res = await session.execute(select(User).where(User.id.in_(target_ids)))
        all_users = {u.handle: u for u in res.scalars().all()}

        follow_relations = [
            ("deepu", ["asha", "sneha", "virat"]),
            ("sneha", ["deepu", "asha", "virat", "ani"]),
            ("asha", ["deepu", "sneha", "ani"]),
            ("ani", ["deepu", "virat", "asha"]),
            ("virat", ["ani", "deepu", "sneha"]),
        ]

        for follower_handle, following_handles in follow_relations:
            if follower_handle not in all_users:
                continue
            follower = all_users[follower_handle]

            for target_handle in following_handles:
                if target_handle in all_users and target_handle != follower_handle:
                    target = all_users[target_handle]
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
        print("\nAll 5 core profiles successfully configured and linked!")
        for p in PROFILES:
            print(f"- {p['display_name']}: @{p['handle']} | ID: {p['id']} | Password: {p['password']}")


if __name__ == "__main__":
    asyncio.run(main())
