"""
Security, hashing, and token helpers (Stage 1 PY-P0-01).

Implements:
- Argon2id password hashing executed in a worker thread to prevent event-loop blocking.
- Constant-time verification & dummy hashing to resist timing enumeration attacks.
- High-entropy cryptographic session tokens with SHA-256 storage hashing.
"""

import asyncio
import hashlib
import secrets
from typing import Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# Argon2id hasher configured per OWASP recommendations
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# Pre-computed dummy hash used to equalize execution timing when handle is not found
_DUMMY_HASH = _ph.hash("dummy_password_for_timing_mitigation_123")


async def hash_password(password: str) -> str:
    """
    Hashes a password with Argon2id inside a worker thread to avoid blocking the event loop.
    """
    return await asyncio.to_thread(_ph.hash, password)


async def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a password against an Argon2id hash inside a worker thread.
    Returns True if valid, False otherwise.
    """
    try:
        await asyncio.to_thread(_ph.verify, hashed_password, password)
        return True
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


async def dummy_verify_password(password: str) -> None:
    """
    Executes a dummy hash verification to burn approximately equal CPU time
    when a user account does not exist, mitigating timing-based account enumeration.
    """
    try:
        await asyncio.to_thread(_ph.verify, _DUMMY_HASH, password)
    except Exception:
        pass


def generate_session_token() -> Tuple[str, str]:
    """
    Generates a secure cryptographic session token (256-bit entropy).
    Returns (raw_bearer_token, sha256_storage_hash).
    Only the raw_bearer_token is sent to the client; only the sha256_storage_hash is stored in the DB.
    """
    raw_token = f"sf_{secrets.token_urlsafe(32)}"
    token_hash = hash_token(raw_token)
    return raw_token, token_hash


def hash_token(raw_token: str) -> str:
    """
    Computes deterministic SHA-256 hash of a session token for database lookup.
    """
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()
