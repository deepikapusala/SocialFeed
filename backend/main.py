
import asyncio                          # gives us `await asyncio.sleep()`
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data import posts as ALL_POSTS

app = FastAPI(
    title="Instagram Feed API",
    description="Point 14 — Cursor-based infinite-scroll feed using FastAPI and async Python.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow requests from any origin
    allow_methods=["GET"],    # we only have a GET endpoint
    allow_headers=["*"],
)

async def fetch_posts_from_db(cursor: int, limit: int) -> list:

    await asyncio.sleep(0.1)

    total = len(ALL_POSTS)
    if total == 0:
        return []

    # Build the batch by wrapping around the posts list
    batch = []
    for i in range(limit):
        source_index = (cursor + i) % total #(24+1)%12=1
        post = dict(ALL_POSTS[source_index])
        post["id"] = cursor + i + 1
        batch.append(post)

    return batch

@app.get("/feed")
async def get_feed(
    cursor: int = Query(default=0,  description="Starting index in the posts list."),
    limit:  int = Query(default=10, description="Number of posts to return per page."),
):

    if cursor < 0:
        raise HTTPException(
            status_code=400,
            detail="cursor must be 0 or greater.",
        )

    if limit <= 0:
        raise HTTPException(
            status_code=400,
            detail="limit must be 1 or greater.",
        )

    if limit > 50:
        raise HTTPException(
            status_code=400,
            detail="limit cannot exceed 50.",
        )

    batch = await fetch_posts_from_db(cursor=cursor, limit=limit)

    next_cursor = cursor + len(batch)

    return {
        "posts":       batch,
        "next_cursor": next_cursor,
        "has_more":    True,                 # always true — infinite scroll
        "count":       len(batch),           # convenient for the frontend
        "total_posts": len(ALL_POSTS),       # total unique posts available
    } 
