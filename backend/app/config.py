import uuid
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Stage C Application Settings using pydantic-settings.
    Reads from environment variables and local .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PORT: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Local HTTP server listening port",
    )

    FRONTEND_ORIGIN: str = Field(
        default="http://localhost:5173",
        description="Allowed frontend CORS origin",
    )

    DEMO_USER_ID: str = Field(
        default="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        description="Development identity UUID matching fixture user",
    )

    SIMULATED_IO_MS: int = Field(
        default=0,
        ge=0,
        le=1000,
        description="Simulated I/O latency in milliseconds for concurrency experiments (0–1000)",
    )

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/instagram_modeling",
        description="SQLAlchemy async connection URL for PostgreSQL",
    )

    DATABASE_CONNECT_TIMEOUT_MS: int = Field(
        default=5000,
        ge=100,
        le=60000,
        description="Database connection timeout in milliseconds",
    )

    @field_validator("DEMO_USER_ID")
    @classmethod
    def validate_demo_user_id(cls, v: str) -> str:
        """Ensure DEMO_USER_ID is a valid UUID string."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError(f"DEMO_USER_ID must be a valid UUID string, got '{v}'")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings provider suitable for FastAPI Depends(get_settings).
    """
    return Settings()
