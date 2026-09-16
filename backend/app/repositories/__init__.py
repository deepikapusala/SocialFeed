"""Repositories Package."""

from app.repositories.base import SocialRepositoryProtocol
from app.repositories.fixture_repository import FixtureRepository
from app.repositories.postgres_repository import PostgresRepository

__all__ = [
    "SocialRepositoryProtocol",
    "FixtureRepository",
    "PostgresRepository",
]
