import asyncio
import uuid
from sqlalchemy import select, delete, text, func
from app.database import get_async_sessionmaker
from app.models.user import User
from app.models.post import Post
from app.models.media import PostMedia
from app.models.like import PostLike
from app.models.follow import Follow
from app.models.session import Session
from app.models.notification import Notification
from app.common.security import hash_password

TARGET_USERS = [
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

KEEP_HANDLES = {'asha', 'deepu', 'ani', 'virat', 'sneha', 'vivek', 'sand', 't1234', 'gollapilli'}

async def main():
    session_factory = get_async_sessionmaker()

    async with session_factory() as session:
        print("--- Step 1: Ensure Target Users Exist ---")
        for u_data in TARGET_USERS:
            pw_hash = await hash_password(u_data["password"])
            res = await session.execute(select(User).where(User.id == u_data["id"]))
            user = res.scalar_one_or_none()

            if not user:
                res_h = await session.execute(select(User).where(User.handle == u_data["handle"]))
                user = res_h.scalar_one_or_none()

            if user:
                user.id = u_data["id"]
                user.handle = u_data["handle"]
                user.display_name = u_data["display_name"]
                user.bio = u_data["bio"]
                user.avatar_small_url = u_data["avatar_small"]
                user.avatar_large_url = u_data["avatar_large"]
                user.password_hash = pw_hash
                user.is_active = True
                user.is_private = False
                print(f"Verified core user: @{user.handle}")

        # Get all 9 target user IDs
        res_ids = await session.execute(select(User.id).where(User.handle.in_(KEEP_HANDLES)))
        target_ids = [row[0] for row in res_ids.all()]
        print(f"Target users found: {len(target_ids)}")
            else:
                new_user = User(
                    id=u_data["id"],
                    handle=u_data["handle"],
                    display_name=u_data["display_name"],
                    bio=u_data["bio"],
                    avatar_small_url=u_data["avatar_small"],
                    avatar_large_url=u_data["avatar_large"],
                    password_hash=pw_hash,
                    is_active=True,
                    is_private=False,
                )
                session.add(new_user)
                print(f"Created user: @{new_user.handle} ({new_user.display_name}) [{new_user.id}]")

        await session.commit()

        print("\n--- Step 2: Remove test/junk data outside the 5 users ---")
        # 1. Notifications
        del_notif = await session.execute(
            delete(Notification).where(
                ~Notification.recipient_id.in_(target_ids) | ~Notification.actor_id.in_(target_ids)
            )
        )
        print(f"Deleted {del_notif.rowcount} orphan notifications")

        # 2. User sessions for non-5 users
        del_sessions = await session.execute(
            delete(Session).where(~Session.user_id.in_(target_ids))
        )
        print(f"Deleted {del_sessions.rowcount} orphan sessions")

        # 3. Follows involving non-5 users
        del_follows = await session.execute(
            delete(Follow).where(
                ~Follow.follower_id.in_(target_ids) | ~Follow.following_id.in_(target_ids)
            )
        )
        print(f"Deleted {del_follows.rowcount} orphan follows")

        # 4. Likes from non-5 users
        del_likes = await session.execute(
            delete(PostLike).where(~PostLike.user_id.in_(target_ids))
        )
        print(f"Deleted {del_likes.rowcount} orphan likes")

        # 5. Media for posts authored by non-5 users
        subq = select(Post.id).where(~Post.author_id.in_(target_ids))
        del_media = await session.execute(
            delete(PostMedia).where(PostMedia.post_id.in_(subq))
        )
        print(f"Deleted {del_media.rowcount} orphan media items")

        # 6. Posts authored by non-5 users
        del_posts = await session.execute(
            delete(Post).where(~Post.author_id.in_(target_ids))
        )
        print(f"Deleted {del_posts.rowcount} orphan posts")

        # 7. Now delete all users EXCEPT the 5 target profiles!
        del_users = await session.execute(
            delete(User).where(~User.id.in_(target_ids))
        )
        print(f"Deleted {del_users.rowcount} unwanted test users from users table.")

        await session.commit()

        # Step 3: Verification
        count_users = (await session.execute(select(func.count(User.id)))).scalar()
        print(f"\n==========================================")
        print(f"TOTAL ROWS IN 'users' TABLE NOW: {count_users}")
        print(f"==========================================")

        all_u = (await session.execute(select(User).order_by(User.handle))).scalars().all()
        for idx, u in enumerate(all_u, 1):
            print(f"{idx}. @{u.handle} | Name: {u.display_name} | ID: {u.id} | Bio: {u.bio[:30]}... | Active: {u.is_active}")

        count_posts = (await session.execute(select(func.count(Post.id)))).scalar()
        print(f"Total posts in DB: {count_posts}")

if __name__ == "__main__":
    asyncio.run(main())
