"""
Database engine and session management for Stage C PostgreSQL integration.
Target Database: instagram_modeling
Reference: docs/05_Python_Database_Integration_PRD.md
"""

from typing import AsyncGenerator, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

# Global references for async engine and session factory
_async_engine: Optional[AsyncEngine] = None
_async_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_engine() -> AsyncEngine:
    """
    Returns the singleton AsyncEngine instance, initializing it lazily on first access.
    Configured with connection timeout and asyncpg driver.
    """
    global _async_engine
    if _async_engine is None:
        settings = get_settings()
        connect_args = {
            "timeout": settings.DATABASE_CONNECT_TIMEOUT_MS / 1000.0,
            "command_timeout": settings.DATABASE_CONNECT_TIMEOUT_MS / 1000.0,
        }
        _async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            connect_args=connect_args,
        )
    return _async_engine


def get_async_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Returns the singleton async_sessionmaker factory bound to the async engine.
    """
    global _async_sessionmaker
    if _async_sessionmaker is None:
        engine = get_async_engine()
        _async_sessionmaker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _async_sessionmaker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding a request-scoped AsyncSession.
    Commits changes on successful request completion, rolls back on exceptions,
    and cleanly closes upon request completion.
    """
    session_factory = get_async_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_async_engine() -> None:
    """
    Gracefully disposes the async engine during application shutdown.
    """
    global _async_engine, _async_sessionmaker
    if _async_engine is not None:
        await _async_engine.dispose()
        _async_engine = None
        _async_sessionmaker = None


async def check_database_connectivity() -> bool:
    """
    Executes a lightweight readiness check (SELECT 1) against instagram_modeling.
    Returns True if successful, False otherwise.
    """
    engine = get_async_engine()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1;"))
            scalar = result.scalar()
            return scalar == 1
    except Exception:
        return False
