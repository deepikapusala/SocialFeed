# PRD 02 — Python track: ASGI and FastAPI social-feed server

**Stage:** A — server foundations. **Effort:** 10–12 hours.  
**Prerequisites:** generator paginator, domain classes, decorators and async feed exercise; Git and Python types/exceptions.  
**Required companion:** [assignment brief and API contract](00_Assignment_Brief_and_API_Contract.md).  
**Next stage:** [database modeling](03_Shared_Database_Modeling_PRD.md), then [FastAPI persistence](05_Python_Database_Integration_PRD.md).

## Problem and outcome

The existing async `/feed` exercise needs to become a maintainable local application with clear HTTP contracts, reliable validation and replaceable data access. At completion, an intern can explain the ASGI request lifecycle and demonstrate the existing browser feed consuming the same contract as the JS cohort.

The product behavior is identical to the shared brief. The Python learning emphasis is resource lifetime, explicit schemas, dependency overrides, generator consumption and nonblocking waits. No ORM or database integration is required at this gate.

## Requirements

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| PY-S01 | Must | Build a small raw ASGI lab before the full framework application | Correct HTTP scope handling and response-start/body messages |
| PY-S02 | Must | Use an isolated environment and reproducible dependency installation | Python version, dependency/lock files and runnable commands |
| PY-S03 | Must | Separate routers, services, response schemas and fixture repository | Dependency override changes repository behavior in a test |
| PY-S04 | Must | Implement the Stage A routes and shared camelCase contract | Health, feed, post detail and profile responses |
| PY-S05 | Must | Validate query/path inputs and standardize exception output | Correct 400/404/500 envelope; no framework-default shape leaks |
| PY-S06 | Must | Explain and demonstrate async waiting/cancellation cleanup | Concurrent wait evidence and a cancellation/error cleanup test |
| PY-S07 | Must | Keep pagination bounded and stable | Three cursor pages; tied timestamp case; no eager full-feed conversion |
| PY-S08 | Must | Validate environment and configure CORS/request IDs | Startup checks and browser request against configured origin |
| PY-S09 | Must | Integrate existing feed/detail UI and OpenAPI docs | Documented `/docs` and manual loading/error/retry demo |

## Work breakdown

### A1: raw ASGI lab — 2 hours maximum

Create `labs/raw_asgi/` with a callable accepting `scope`, `receive` and `send`; run it with Uvicorn. Handle `GET /health/live` and `GET /feed`, including an HTTP response-start message and JSON response-body bytes; return 404 for an unknown path. State which scope types the toy lab supports. Disable lifespan for this toy runner or implement its handshake explicitly; do not leave the server hanging on startup events.

Write a short comparison of WSGI and ASGI responsibilities and why Uvicorn is a server while FastAPI is an application framework. Keep this lab minimal; the complete shared API contract is implemented in FastAPI.

### A2: application structure — 2 hours

Use a virtual environment, recorded Python version and one reproducible dependency workflow. Include FastAPI, Uvicorn, Pydantic/settings and test tools; use a compatible maintained release set and lock it. Avoid multiple competing package managers.

Suggested structure:

```text
social-feed-python/
  labs/raw_asgi/
  app/
    main.py                  # application factory and lifespan
    config.py
    api/                     # health/users/posts/feed routers
    schemas/                 # validated request/response models
    services/
    repositories/            # interface/protocol and fixture implementation
    common/                  # errors, cursors, request logging
    fixtures/
  tests/
  pyproject.toml
  .env.example
  README.md
```

Create an application factory or equivalent test-friendly setup. Use `APIRouter` and `Depends` where they solve a real boundary. Do not run network calls or expensive fixture creation merely by importing a module. Response models expose aliases for the shared camelCase contract; Pydantic request models should not be confused with database models or the earlier illustrative OOP classes.

### A3: read API and concurrency — 4 hours

Implement `GET /health/live`, `/feed`, `/posts/{id}` and `/users/{id}` with the exact fixture sizes, ordering, counts and cursor semantics from the brief. Use an injected fixture repository and explicit serializers/response models. A missing relationship must not accidentally expose an internal Python representation.

Validate `PORT`, `FRONTEND_ORIGIN`, fixture/demo user ID and `SIMULATED_IO_MS` (0–1,000, default 0). Runtime configuration is loaded once in an explicit application boundary. Configure the allowed browser origin and add request IDs to responses, errors and logs.

FastAPI commonly returns 422 for request validation by default. For this cross-track contract, map query/path failures to 400 and reserve 422 for Stage C body/domain failures. Reject duplicate/unknown query parameters and legacy `page`, not just invalid field values. Keep 404 and unexpected 500 errors in the shared envelope. Document actual responses in OpenAPI.

Use `await asyncio.sleep(...)` only for a configured mock-latency experiment; no `time.sleep` in async request work. Adapt the previous paginator so its consumer takes only the required batch. Fixtures may be small and in memory, but record the distinction between lazy iteration over a loaded list and bounded database fetching in the next stage. An async iterator is appropriate when fetching the next batch itself awaits I/O.

### A4: tests, integration and handoff — 2–4 hours

Use pytest and HTTP client tests with dependency overrides. Use FastAPI TestClient for synchronous HTTP tests or HTTPX async tests where async behavior is being tested. Ensure application lifespan runs in tests that depend on startup/shutdown state. Reset overrides/fixture state between tests.

Connect the existing browser feed using `nextCursor`; show a loading skeleton, controlled error and retry. Record concurrent fake I/O requests with clear start/end events, then explain why this demonstrates overlap but not CPU parallelism. Demonstrate cleanup when a fake resource operation raises or is canceled.

## Acceptance tests

| Case | Expected result |
|---|---|
| Startup and health | Documented command starts; 200 liveness; no import-time network dependency |
| Default feed and two continuations | At most 10 originals each; deterministic descending tuple order; no duplicates/skips on seed |
| Same creation timestamp | ID tie-breaker preserves both rows at a boundary |
| Invalid/repeated query or legacy `page` | 400 shared envelope, not FastAPI's unmodified default payload |
| Malformed UUID / absent valid UUID | 400 / 404 respectively |
| Existing profile/post | Shared casing, relationships, counts and media metadata |
| Oversized/invalid cursor | 400 with request ID; safe message |
| Dependency override raises | Error envelope; no raw traceback or environment values |
| Multiple delayed requests | Nonblocking overlap observed with timing/event evidence |
| Cancellation/exception | Fake resource cleanup executes and next request still works |

## Deliverables and review

Submit the raw ASGI lab, FastAPI app, deterministic fixtures, pytest suite, dependency files, `.env.example`, README and `request-lifecycle.md`. Document development start, lint/type checking if configured, tests, `/docs`, CORS origin and sample requests. Include the small async timing report and one dependency-override test.

Explain why `len(post)` from the earlier class exercise does not automatically become a SQL query; why a generator does not make an already-loaded dataset smaller; and why an async handler can still block if its dependencies are synchronous. The mentor must see both the successful feed and a controlled failure.

**Gate:** all must requirements and acceptance cases pass. Caching is deferred until uncached data access is correct; `lru_cache` must not wrap a coroutine result directly.

## Free resources

- [ASGI HTTP specification](https://asgi.readthedocs.io/en/latest/specs/www.html): HTTP scope and response messages.
- [FastAPI larger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/), [lifespan](https://fastapi.tiangolo.com/advanced/events/) and [concurrency](https://fastapi.tiangolo.com/async/).
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) and [async tests](https://fastapi.tiangolo.com/advanced/async-tests/).
- [Python coroutine/task documentation](https://docs.python.org/3/library/asyncio-task.html) and [functools](https://docs.python.org/3/library/functools.html).
