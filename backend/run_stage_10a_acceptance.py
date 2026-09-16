import asyncio
import json
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings
from app.database import get_async_sessionmaker, dispose_async_engine
from app.repositories.postgres_repository import PostgresRepository
from app.services.feed_service import FeedService
from app.services.social_service import SocialService

async def run_audit():
    settings = get_settings()
    results = {}
    
    # 1. Connection & DB Name & Current User
    try:
        connect_args = {
            "timeout": settings.DATABASE_CONNECT_TIMEOUT_MS / 1000.0,
            "command_timeout": settings.DATABASE_CONNECT_TIMEOUT_MS / 1000.0,
        }
        engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True, connect_args=connect_args)
        
        async with engine.connect() as conn:
            # 2. Confirm current database
            db_res = await conn.execute(text("SELECT current_database();"))
            current_db = db_res.scalar()
            
            # 3. Confirm current user
            user_res = await conn.execute(text("SELECT current_user;"))
            current_user = user_res.scalar()
            
            results["1_connection"] = "PASS"
            results["2_database_name"] = current_db
            results["3_current_user"] = current_user
            
            if current_db != "instagram_modeling":
                print(f"ERROR: Expected database 'instagram_modeling', got '{current_db}'")
                return
            
            # 4. Confirm tables exist in public schema
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables_res = await conn.execute(tables_query)
            existing_tables = set(r[0] for r in tables_res.fetchall())
            required_tables = {"users", "posts", "post_media", "post_likes", "follows"}
            
            results["4_tables_exist"] = "PASS" if required_tables.issubset(existing_tables) else "FAIL"
            results["4_found_tables"] = sorted(list(existing_tables))
            
            # 5. Query safe aggregate counts
            counts = {}
            for tbl in ["users", "post_media", "post_likes", "follows"]:
                c_res = await conn.execute(text(f"SELECT COUNT(*) FROM {tbl};"))
                counts[tbl] = c_res.scalar()
            
            orig_res = await conn.execute(text("SELECT COUNT(*) FROM posts WHERE kind = 'original';"))
            counts["original_posts"] = orig_res.scalar()
            
            rep_res = await conn.execute(text("SELECT COUNT(*) FROM posts WHERE kind = 'reply';"))
            counts["replies"] = rep_res.scalar()
            
            repost_res = await conn.execute(text("SELECT COUNT(*) FROM posts WHERE kind = 'repost';"))
            counts["reposts"] = repost_res.scalar()
            
            results["5_counts"] = counts
            
            # 6. Verify deterministic seed minimums
            # 6 users, 30 originals, 12 replies, 4 reposts, 10 media, 15 likes, 8 follows
            seed_ok = (
                counts["users"] >= 6 and
                counts["original_posts"] >= 30 and
                counts["replies"] >= 12 and
                counts["reposts"] >= 4 and
                counts["post_media"] >= 10 and
                counts["post_likes"] >= 15 and
                counts["follows"] >= 8
            )
            results["6_seed_minimums"] = "PASS" if seed_ok else "FAIL"
            
            # 7. Two originals with same created_at timestamp
            tie_res = await conn.execute(text("""
                SELECT created_at, COUNT(*) 
                FROM posts 
                WHERE kind = 'original' 
                GROUP BY created_at 
                HAVING COUNT(*) > 1;
            """))
            ties = tie_res.fetchall()
            results["7_timestamp_tie"] = "PASS" if len(ties) > 0 else "FAIL"
            results["7_tie_count"] = len(ties)
            
            # 8. At least one user has zero media
            user_no_media_res = await conn.execute(text("""
                SELECT u.id 
                FROM users u
                LEFT JOIN posts p ON p.author_id = u.id
                LEFT JOIN post_media pm ON pm.post_id = p.id
                GROUP BY u.id
                HAVING COUNT(pm.id) = 0;
            """))
            users_zero_media = user_no_media_res.fetchall()
            results["8_user_zero_media"] = "PASS" if len(users_zero_media) > 0 else "FAIL"
            
            # 9. At least one original has zero likes
            orig_no_likes_res = await conn.execute(text("""
                SELECT p.id 
                FROM posts p
                LEFT JOIN post_likes pl ON pl.post_id = p.id
                WHERE p.kind = 'original'
                GROUP BY p.id
                HAVING COUNT(pl.user_id) = 0;
            """))
            orig_zero_likes = orig_no_likes_res.fetchall()
            results["9_orig_zero_likes"] = "PASS" if len(orig_zero_likes) > 0 else "FAIL"
            
            # 10. At least one original is liked
            orig_liked_res = await conn.execute(text("""
                SELECT p.id 
                FROM posts p
                INNER JOIN post_likes pl ON pl.post_id = p.id
                WHERE p.kind = 'original'
                GROUP BY p.id
                HAVING COUNT(pl.user_id) > 0;
            """))
            orig_liked = orig_liked_res.fetchall()
            results["10_orig_liked"] = "PASS" if len(orig_liked) > 0 else "FAIL"

        # Test Services backed by PostgresRepository
        session_factory = get_async_sessionmaker()
        async with session_factory() as session:
            repo = PostgresRepository(session=session)
            feed_service = FeedService(repository=repo)
            social_service = SocialService(repository=repo)
            
            # 11. Feed query with cursor pagination
            feed_p1 = await feed_service.get_feed(cursor_str=None, limit=10, viewer_id=settings.DEMO_USER_ID)
            results["11_feed_p1_count"] = len(feed_p1.items)
            results["11_feed_p1_has_more"] = feed_p1.has_more
            results["11_feed_p1_next_cursor"] = bool(feed_p1.next_cursor)
            results["11_feed_status"] = "PASS" if len(feed_p1.items) == 10 and feed_p1.has_more else "FAIL"
            
            # 12. Continuation request using nextCursor without duplicate IDs
            feed_p2 = await feed_service.get_feed(cursor_str=feed_p1.next_cursor, limit=10, viewer_id=settings.DEMO_USER_ID)
            p1_ids = set(str(item.id) for item in feed_p1.items)
            p2_ids = set(str(item.id) for item in feed_p2.items)
            duplicates = p1_ids.intersection(p2_ids)
            results["12_continuation_count"] = len(feed_p2.items)
            results["12_continuation_duplicates"] = len(duplicates)
            results["12_continuation_status"] = "PASS" if len(feed_p2.items) == 10 and len(duplicates) == 0 else "FAIL"
            
            # 13. Post detail works from PostgreSQL
            target_post_id = str(feed_p1.items[0].id)
            post_detail_resp = await social_service.get_post_detail(post_id=target_post_id, viewer_id=settings.DEMO_USER_ID)
            post_detail = post_detail_resp.item
            results["13_post_detail_id"] = str(post_detail.id)
            results["13_post_detail_author"] = post_detail.author.handle
            results["13_post_detail_status"] = "PASS" if str(post_detail.id) == target_post_id else "FAIL"
            
            # 14. Profile and profile-media endpoints
            author_id = str(post_detail.author.id)
            profile_resp = await social_service.get_user_profile(user_id=author_id)
            profile = profile_resp.item
            profile_media = await social_service.list_profile_media(user_id=author_id, cursor_str=None, limit=20)
            results["14_profile_handle"] = profile.handle
            results["14_profile_posts_count"] = profile.post_count
            results["14_profile_media_count"] = len(profile_media.items)
            results["14_profile_status"] = "PASS" if str(profile.id) == author_id else "FAIL"
            
            # 15. Search endpoint (positive and empty result)
            search_query_term = profile.handle[:4]
            search_pos = await social_service.search_originals(query=search_query_term, cursor_str=None, limit=10, viewer_id=settings.DEMO_USER_ID)
            search_empty = await social_service.search_originals(query="xyznonexistentquery999", cursor_str=None, limit=10, viewer_id=settings.DEMO_USER_ID)
            results["15_search_pos_count"] = len(search_pos.items)
            results["15_search_empty_count"] = len(search_empty.items)
            results["15_search_status"] = "PASS" if len(search_empty.items) == 0 else "FAIL"
            
            # 16. Like/unlike repository authoritative state
            initial_liked = post_detail.liked_by_viewer
            
            if initial_liked:
                unlike_res = await social_service.remove_like(user_id=settings.DEMO_USER_ID, post_id=target_post_id)
                relike_res = await social_service.set_like(user_id=settings.DEMO_USER_ID, post_id=target_post_id)
                like_test_ok = (unlike_res.liked_by_viewer == False and relike_res.liked_by_viewer == True)
            else:
                like_res = await social_service.set_like(user_id=settings.DEMO_USER_ID, post_id=target_post_id)
                unlike_res = await social_service.remove_like(user_id=settings.DEMO_USER_ID, post_id=target_post_id)
                like_test_ok = (like_res.liked_by_viewer == True and unlike_res.liked_by_viewer == False)
                
            results["16_like_toggle_authoritative"] = "PASS" if like_test_ok else "FAIL"

        # 17. Readiness vs Liveness checks
        from app.database import check_database_connectivity
        ready_ok = await check_database_connectivity()
        results["17_readiness_db_check"] = "PASS" if ready_ok else "FAIL"
        
        await dispose_async_engine()
        await engine.dispose()
        
    except Exception as e:
        import traceback
        results["ERROR"] = str(e)
        results["TRACEBACK"] = traceback.format_exc()
        
    print("AUDIT_RESULTS_JSON:" + json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(run_audit())
