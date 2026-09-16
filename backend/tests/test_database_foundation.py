import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.config import Settings
from app.database import (
    get_async_engine,
    get_async_sessionmaker,
    dispose_async_engine,
)


def test_stage_c_settings_fields():
    """Verify Stage C database configuration fields in Settings."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/instagram_modeling",
        DATABASE_CONNECT_TIMEOUT_MS=3000,
    )
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/instagram_modeling"
    assert settings.DATABASE_CONNECT_TIMEOUT_MS == 3000
    assert "instagram_modeling" in settings.DATABASE_URL
    assert "student" not in settings.DATABASE_URL


def test_async_engine_initialization():
    """Verify get_async_engine returns a configured AsyncEngine."""
    engine = get_async_engine()
    assert isinstance(engine, AsyncEngine)
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "asyncpg"


def test_async_sessionmaker_factory():
    """Verify get_async_sessionmaker returns a factory producing AsyncSession."""
    factory = get_async_sessionmaker()
    session = factory()
    assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_dispose_async_engine():
    """Verify dispose_async_engine cleanly resets the global engine singleton."""
    engine = get_async_engine()
    assert engine is not None
    await dispose_async_engine()
    from app import database
    assert database._async_engine is None
    assert database._async_sessionmaker is None
