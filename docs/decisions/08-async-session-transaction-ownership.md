# Decision 08: Async Session and Transaction Ownership

Decision:      FastAPI request-scoped `AsyncSession` with explicit service-level transaction boundaries (`async with session.begin():` or explicit `session.commit()`). Repositories never commit internally.
Options:       1. Repository methods commit on every write (leaks transaction ownership, prevents multi-table atomic operations).
               2. Middleware-level auto-commit (commits on 2xx responses even if invariant validation was incomplete).
               3. Service-managed transaction boundaries with repository execution-only access (chosen).
Why this one:  Preserves strict transaction boundaries required for notification atomicity, multi-row state machine updates, and rollback isolation. Repositories only query and stage entities; the service coordinates atomicity.
Risks:         Uncommitted sessions returning without error; mitigated by dependency-level rollback in `finally` and explicit integration tests for rollback behavior.
Test proving it: [tests/test_fastapi_postgres_integration.py](file:///f:/Instagram/backend/tests/test_fastapi_postgres_integration.py)
