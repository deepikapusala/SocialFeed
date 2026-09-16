# PRD 05 — Python track: persist the social feed with FastAPI and PostgreSQL

**Stage:** C — database integration. **Effort:** 10–14 hours.  
**Prerequisites:** [Python server setup](02_Python_Server_Setup_PRD.md) and reviewed [shared database model](03_Shared_Database_Modeling_PRD.md).  
**Default tools:** FastAPI, SQLAlchemy 2.x async ORM/Core, asyncpg, Alembic and PostgreSQL.

## Problem and outcome

The generator-based in-memory feed demonstrates bounded iteration but loses data at restart and cannot enforce relational rules. Replace the fixture repository with an async PostgreSQL repository while preserving the shared API, cursor semantics, frontend behavior and explicit validation boundaries.

At completion, an intern can explain where an `AsyncSession` starts/ends, how an Alembic migration changes a database, why a generator does not replace a database cursor, and how two concurrent like requests are handled safely.

## Requirements

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| PY-D01 | Must | Configure an async PostgreSQL engine/session factory safely | Missing config fails clearly; session lifecycle is request/task scoped |
| PY-D02 | Must | Generate and review versioned Alembic migrations | Empty DB upgrade and documented downgrade/check path |
| PY-D03 | Must | Implement repositories with async SQL and typed result mapping | Unit/HTTP tests and no ORM model leakage |
| PY-D04 | Must | Preserve cursor pagination, counts and viewer state | Tuple predicate, `limit+1`, batch relationships, no eager whole-feed load |
| PY-D05 | Must | Enforce model constraints and map database exceptions | Duplicate like/repost/follow tests and clear conflict/error mapping |
| PY-D06 | Must | Bound every `AsyncSession` and transaction | Commit/rollback behavior and no session sharing between concurrent tasks |
| PY-D07 | Must | Implement post/reply/repost and desired-state like/unlike writes | Retry-safe state and rollback test |
| PY-D08 | Must | Seed exact reviewed fixture data idempotently | Counts/manifest match modeling PRD |
| PY-D09 | Must | Run real PostgreSQL tests, not only mocks | Isolated test database and migration setup/teardown |
| PY-D10 | Must | Connect existing infinite-scroll and detail/profile pages | Cursor, skeleton, retry and authoritative like state work |
| PY-D11 | Should | Add DB readiness, query-plan report and optional async batch timing | 200/503 behavior and reproducible `EXPLAIN` evidence |

## Implementation plan

### C1: async engine, settings and migration baseline — 2–3 hours

Create typed settings for `DATABASE_URL`, `DEMO_USER_ID`, `FRONTEND_ORIGIN`, `PORT` and `DATABASE_CONNECT_TIMEOUT_MS`. Prefer a PostgreSQL async URL (`postgresql+asyncpg://...`) for the application. Build one engine and `async_sessionmaker`; do not create a new engine per request or share one mutable session among concurrent tasks. Dispose the engine on application lifespan shutdown.

Keep the application factory testable: dependency injection supplies an `AsyncSession` or repository, while tests can override it. A readiness query has a short timeout and returns 503 on database failure; liveness should not perform a database query.

Represent the reviewed data model as SQLAlchemy declarative models, but do not use those models as public response schemas. Use Pydantic request/response models and explicit conversion. Preserve camelCase aliases on the wire while Python internals/database columns can remain snake_case.

Initialize Alembic against an empty database, review generated SQL and adjust it manually where constraints/index names or partial behavior need precision. Commit revisions. The application startup does not call `create_all`; it assumes migrations ran. Provide an explicit developer migration command and a documented downgrade/check path.

### C2: bounded repositories and query methods — 3–4 hours

Use repository functions around the shared use cases: `list_original_feed`, `get_post_detail`, `get_profile`, `list_direct_replies`, `list_profile_media`, `search_originals`, `create_post` and `set_like`. Every function accepts the actor/viewer where needed and returns domain data/errors rather than leaking an `AsyncSession` into a response.

The feed query filters originals and applies a lexicographic tuple predicate on `(created_at, id)` before ordering. Read `limit + 1`, convert only the returned page to response objects, and close the session after the request. For multiple relationships, use separate grouped selects or carefully tested subqueries. Fetch viewer-liked IDs in one query for the page's post IDs. Verify SQL query count using SQLAlchemy event logging or a test hook; do not use an N+1 loop hidden behind a list comprehension.

The earlier generator paginator is still useful at the repository boundary when a caller wants pages: an async generator may yield one result page at a time, but it must not hold one transaction/session open indefinitely. Define whether each yielded page has its own session or whether the caller owns a bounded context. For the HTTP endpoint, a simple one-page repository method is easier to reason about.

For literal search, use parameter binding and explicit escaping/operator semantics. `q` is validated before SQL. Do not build a SQL string through f-strings. Map `NoResult`, not-found and database errors to the shared error envelope in the service/exception layer.

### C3: transactions, constraints and concurrency — 3–4 hours

Use a transaction context for multi-row post/reply/repost creation. Validate target kind before inserting a reply/repost; the database foreign key proves existence, while service/domain logic proves it is an original. Map `IntegrityError` by constraint or a safe domain translation to 409 for duplicate repost/like/follow rather than exposing driver text.

Like/unlike is a desired-state operation. For like, insert the `(viewer_id,post_id)` relation and handle the unique conflict as already liked; for unlike, delete and return unliked if absent. Either approach may be used, but test two concurrent sessions and make the response contract stable. Never call `session.commit()` in a repository helper that is supposed to compose with a larger service transaction without documenting that boundary.

A transaction rollback test should perform a valid insert then force a second operation to violate a constraint, catch the error at the correct boundary, and verify the first row is absent using a new session. Do not reuse a session in a failed transaction without an explicit rollback/cleanup. Use `expire_on_commit=False` only with a reason and avoid relying on lazy loads after the session is closed.

### C4: seed, frontend integration and measurements — 2–3 hours

Write an explicit seed command using the reviewed fixed IDs/timestamps. It may use Core bulk inserts for deterministic data, then verify the manifest through SQL. Re-running should upsert fixed IDs or require a clearly named disposable reset; never silently wipe a developer database from application startup.

Switch the existing browser pages to the persisted API and shared cursor. Ensure the endpoint returns an independent response after each page and that the browser pauses duplicate IntersectionObserver fires. Keep optimistic likes but reconcile to desired-state responses and test a controlled database/write failure for rollback.

Run two `EXPLAIN (ANALYZE, BUFFERS)` reports. Record async query timing separately from serialization and network time; simulated `asyncio.sleep` is not database performance evidence. Use a larger labeled fixture if the seed is too small to show an index decision. The expected result can be “sequential scan is correct for this size.”

## Acceptance tests

| Test | Expected |
|---|---|
| Empty PostgreSQL + Alembic upgrade | All tables, constraints and indexes create; revision is recorded |
| Seed/reseed | Manifest counts stay exact; no duplicate logical IDs |
| Feed pages and timestamp tie | Correct tuple order, continuation, no duplicate/skip on unchanged seed |
| Async session scope | Concurrent requests do not share a session; failed transaction is rolled back |
| Count/viewer-state query | Correct zero counts and liked flags without per-post query loop |
| Duplicate like/repost/follow/self-follow | Constraint/domain errors map to shared status/code |
| Two concurrent like sessions | At most one relation and coherent desired-state response |
| Reply/repost invalid target | Existing non-original target returns 422; missing target 404 |
| Search | Literal `%`/`_` behavior is documented and parameterized |
| Database outage/readiness | Bounded 503; liveness remains distinct |
| Frontend integration | Cursor, skeleton, retry, de-dupe and like rollback work against real DB |
| Query plans | Two reports include SQL shape, data size, conditions and observed plan |

## Deliverables and review

Submit SQLAlchemy models, Alembic revisions, settings/lifespan changes, repositories/services/routes, seed command, tests, query reports and README updates. Add `docs/async-session-boundaries.md` with one request timeline and one failed-transaction timeline. Include a short note explaining why `len(post)` is a domain convenience in the earlier class exercise, not a license to load all comments, and how a feed page remains bounded.

The mentor asks: when is the session committed; what happens after an `IntegrityError`; why an async generator can still hold a connection too long; how the tuple cursor handles equal timestamps; which constraints belong in SQL; and how a caller retry behaves after a network timeout.

**Gate:** all must requirements and acceptance cases pass against PostgreSQL. A mocked repository test alone is not persistence evidence. The optional `cache_feed` decorator can follow this gate with a measured invalidation/TTL design; it is not part of the core persistence PRD.

## Free resources

- [FastAPI database testing](https://fastapi.tiangolo.com/how-to/testing-database/), [bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) and [lifespan](https://fastapi.tiangolo.com/advanced/events/).
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) and [session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) and [autogenerate limitations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html).
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [indexes](https://www.postgresql.org/docs/current/indexes.html), [transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html) and [EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).
