"""API Routers Package."""

from app.api.health import router as health_router
from app.api.feed import router as feed_router
from app.api.posts import router as posts_router
from app.api.users import router as users_router
from app.api.search import router as search_router

__all__ = [
    "health_router",
    "feed_router",
    "posts_router",
    "users_router",
    "search_router",
]
