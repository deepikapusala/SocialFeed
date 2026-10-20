# Decision 01: Identity, Session & Revocation Model

Decision:      Stateful Bearer tokens with server-side SHA-256 hashed sessions in PostgreSQL, paired with Argon2id password hashing executed via asyncio.to_thread.
Options:       1. Pure stateless JWT (fast, but cannot revoke stolen tokens without complex distributed blocklists).
               2. Redis-backed sessions (fast, but adds external infrastructure dependency, violating single-service architecture).
               3. Database-backed session table in PostgreSQL with indexed token hashes (chosen).
Why this one:  PostgreSQL sessions provide instantaneous revocation on /auth/logout, transactional consistency with user accounts, and zero additional infrastructure. Argon2id provides memory-hard password protection while offloading hashing to worker threads prevents event-loop starvation.
Risks:         Database session lookup overhead on every authenticated request; mitigated by an index on `token_hash` and filtering `revoked_at IS NULL AND expires_at > CURRENT_TIMESTAMP`.
Test proving it: [tests/test_api_auth.py](file:///f:/Instagram/backend/tests/test_api_auth.py)
