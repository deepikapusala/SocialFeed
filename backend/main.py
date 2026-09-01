# main.py
# Point 14 — FastAPI backend with a cursor-based infinite-scroll /feed endpoint.
#
# How to start:
#   cd backend
#   uvicorn main:app --reload
#
# Then open:
#   http://localhost:8000/feed?cursor=0&limit=10
#   http://localhost:8000/docs


import asyncio                          # gives us `await asyncio.sleep()`
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Import the 30 sample posts that already exist from Point 11.
from data import posts as ALL_POSTS


# ---------------------------------------------------------------------------
# Create the FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Instagram Feed API",
    description="Point 14 — Cursor-based infinite-scroll feed using FastAPI and async Python.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) allows the React frontend running on
# http://localhost:5173 (Vite) or http://localhost:3000 to call this backend
# on http://localhost:8000 without the browser blocking the request.
#
# For a learning project we allow all origins ("*").
# In production you would list only your real frontend URL.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow requests from any origin
    allow_methods=["GET"],    # we only have a GET endpoint
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Async mock database fetch (simulates real I/O latency)
# ---------------------------------------------------------------------------
#
# Why async?
# In a real app, fetching posts from a database takes time (network round-trip,
# disk I/O, etc.).  During that waiting time, an async server can handle OTHER
# incoming requests instead of sitting idle.
#
# `await asyncio.sleep(0.1)` tells Python:
#   "pause this function for 0.1 seconds, but let other async tasks run
#    while we wait — don't block the whole server."
#
# This is the same concept as a real database call:
#
#   Request
#     ↓
#   await database.fetch_posts(...)   ← server is free to handle other work here
#     ↓
#   data returns
#     ↓
#   send response

async def fetch_posts_from_db(cursor: int, limit: int) -> list:
    """
    Simulate an async database query with wrap-around for infinite scrolling.

    Instead of stopping when we reach the end of the posts list, this function
    wraps around using modular arithmetic so the feed never runs out.

    For example, if there are 51 posts and cursor=49, limit=10:
      - We need posts at indices 49, 50, 0, 1, 2, 3, 4, 5, 6, 7
      - Each index is computed as (cursor + i) % total_posts

    Each returned post gets a unique `id` based on the cursor position
    so the React frontend can use it as a stable key without collisions.

    Args:
        cursor (int): The starting index (can exceed total posts — it wraps).
        limit  (int): How many posts to return.

    Returns:
        list: A list of post dicts with unique IDs for this batch.
    """
    # Simulate the time a real database query would take (0.1 seconds).
    await asyncio.sleep(0.1)

    total = len(ALL_POSTS)
    if total == 0:
        return []

    # Build the batch by wrapping around the posts list
    batch = []
    for i in range(limit):
        # Use modular arithmetic to cycle through the posts array
        source_index = (cursor + i) % total
        # Make a shallow copy so we don't mutate the original data
        post = dict(ALL_POSTS[source_index])
        # Assign a unique id based on cursor position to avoid React key collisions
        post["id"] = cursor + i + 1
        batch.append(post)

    return batch


# ---------------------------------------------------------------------------
# /feed endpoint
# ---------------------------------------------------------------------------

@app.get("/feed")
async def get_feed(
    cursor: int = Query(default=0,  description="Starting index in the posts list."),
    limit:  int = Query(default=10, description="Number of posts to return per page."),
):
    """
    Cursor-based infinite-scroll feed with wrap-around.

    Returns a batch of posts starting at `cursor`, plus the cursor value
    to use for the next request. The feed wraps around the existing posts
    so it never ends — enabling true infinite scrolling.

    Examples:
    - GET /feed               → posts 0-9,   next_cursor=10, has_more=true
    - GET /feed?cursor=10     → posts 10-19, next_cursor=20, has_more=true
    - GET /feed?cursor=50     → wraps around, next_cursor=60, has_more=true
    """

    # ------------------------------------------------------------------
    # Simple validation
    # ------------------------------------------------------------------
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

    # Clamp limit to a maximum of 50 to prevent abusive requests.
    if limit > 50:
        raise HTTPException(
            status_code=400,
            detail="limit cannot exceed 50.",
        )

    # ------------------------------------------------------------------
    # Fetch the posts (async — wraps around for infinite scroll)
    # ------------------------------------------------------------------
    batch = await fetch_posts_from_db(cursor=cursor, limit=limit)

    # ------------------------------------------------------------------
    # Calculate the next cursor — always advance, never stop
    # ------------------------------------------------------------------
    next_cursor = cursor + len(batch)

    # ------------------------------------------------------------------
    # Return the response as JSON
    # ------------------------------------------------------------------
    return {
        "posts":       batch,
        "next_cursor": next_cursor,
        "has_more":    True,                 # always true — infinite scroll
        "count":       len(batch),           # convenient for the frontend
        "total_posts": len(ALL_POSTS),       # total unique posts available
    }
