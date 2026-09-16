# Social Feed (Python Track) — Stage A Documentation

## Overview

This repository contains **Stage A: Server Foundations** for the **Social Feed** application. 

Stage A provides:
1. A **FastAPI** backend built around clean application factories, dependency injection, and deterministic in-memory fixtures.
2. An **ASGI** architecture demonstrating non-blocking async execution, task cancellation, and standardized request tracing.
3. An integrated **React** explore feed that consumes real backend data via opaque cursor pagination and standardized camelCase API contracts.

> **Stage Note:** Stage A deliberately uses in-memory fixtures. PostgreSQL, SQLAlchemy, asyncpg, Alembic, Redis, and JWT authentication are intentionally excluded and will be introduced in Stages B and C.

---

## 1. Quick Start / How to Run Locally

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### Step 1: Start the FastAPI Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
The backend starts at `http://127.0.0.1:8000`.

### Step 2: Start the React Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend starts on the configured Vite development server at `http://localhost:3000`.

---

## 2. Key API Endpoints

| Endpoint | Method | Description | Response Shape |
|---|---|---|---|
| `/health/live` | `GET` | Liveness health check. Does not connect to or depend on any database. | `{"status": "ok"}` |
| `/feed` | `GET` | Paginated chronological feed of original posts. Supports `cursor` and `limit`. | `{"items": [...], "nextCursor": "...", "hasMore": true}` |
| `/posts/{id}` | `GET` | Single post detail with author, media variants, and viewer reaction state. | `{"item": { ... }}` (or 404 envelope) |
| `/users/{id}` | `GET` | User profile with author metadata and post/follower counts. | `{"item": { ... }}` (or 404 envelope) |
| `/docs` | `GET` | Interactive Swagger UI API documentation. | HTML / Interactive UI |
| `/openapi.json` | `GET` | OpenAPI 3.x schema definition. | JSON Schema |

---

## 3. Stage A Architecture

```
                  ┌─────────────────────────────────────────┐
                  │    React / Vite Frontend UI             │
                  │    (http://localhost:3000)              │
                  └────────────────────┬────────────────────┘
                                       │ HTTP Requests (camelCase, X-Request-Id)
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    FastAPI Application Factory          │
                  │    (app.main:create_app)                │
                  ├─────────────────────────────────────────┤
                  │ Middlewares:                            │
                  │   • RequestIdMiddleware (X-Request-Id)  │
                  │   • CORSMiddleware (Port 3000 & 5173)   │
                  │   • Global Error Exception Handlers     │
                  └────────────────────┬────────────────────┘
                                       │
                  ┌────────────────────▼────────────────────┐
                  │    API Routers                          │
                  │    (/health, /feed, /posts, /users)     │
                  └────────────────────┬────────────────────┘
                                       │ Dependency Injection (Depends)
                  ┌────────────────────▼────────────────────┐
                  │    Application Services                 │
                  │    (FeedService, SocialService)         │
                  └────────────────────┬────────────────────┘
                                       │ SocialRepositoryProtocol
                  ┌────────────────────▼────────────────────┐
                  │    FixtureRepository                    │
                  │    (app/repositories/fixture_repo.py)   │
                  └────────────────────┬────────────────────┘
                                       │
                  ┌────────────────────▼────────────────────┐
                  │    Deterministic Fixture Dataset        │
                  │    (6 users, 30 originals, 12 replies,  │
                  │     4 reposts, 10 media, 15 likes)      │
                  └─────────────────────────────────────────┘
```

---

## 4. Shared API Contracts

All wire payloads use **camelCase** naming.

### Post Item Schema
```json
{
  "id": "11111111-1111-4111-8111-111111111101",
  "kind": "original",
  "text": "Morning mist rising over pine forests and alpine lakes. 🌲⛰️",
  "createdAt": "2026-09-01T10:30:00.000Z",
  "author": {
    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa02",
    "handle": "yosemite_wanderer",
    "displayName": "Marcus Thorne",
    "avatar": {
      "smallUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&q=80",
      "largeUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=80"
    }
  },
  "media": [
    {
      "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01",
      "altText": "Morning mist rising over pine forests",
      "width": 1200,
      "height": 800,
      "position": 0,
      "smallUrl": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&q=80",
      "largeUrl": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&q=80"
    }
  ],
  "likeCount": 3,
  "replyCount": 2,
  "likedByViewer": false,
  "replyToId": null,
  "repostOfId": null
}
```

### Paginated Feed Response (`GET /feed`)
```json
{
  "items": [ /* array of PostItems */ ],
  "nextCursor": "eyJ2IjoxLCJjcmVhdGVkQXQiOiIyMDI2LTA5LTAxVDEwOjIwOjAwLjAwMFoiLCJpZCI6IjExMTExMTExLTExMTEtNDExMS04MTExLTExMTExMTExMTExMSJ9",
  "hasMore": true
}
```

---

## 5. Cursor Pagination Mechanics

1. **Ordering Rule:** Posts are sorted strictly in descending order by `(createdAt DESC, id DESC)`.
2. **Deterministic Tie-Breaking:** If two posts share identical timestamps, their unique UUIDs serve as the descending tie-breaker.
3. **Bounded `limit + 1` Retrieval:** The server queries at most `limit + 1` rows to determine `hasMore` without performing an expensive total count query.
4. **Opaque Cursor Encoding:**
   - Tokens encode `{"v": 1, "createdAt": "...", "id": "..."}` as URL-safe base64 strings.
   - Tokens are validated for size (<= 1024 characters), version (`v: 1`), timestamp formatting, and UUID format.
5. **Validation Constraints:**
   - `limit`: Integer from `1` to `50` (default `10`).
   - Legacy query parameter `page` is rejected with `400 Bad Request`.
   - Unknown or duplicate query parameters are rejected with `400 Bad Request`.

---

## 6. Error Envelope Contract

All errors return a uniform JSON envelope accompanied by an `X-Request-Id` response header:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "limit must be an integer from 1 to 50",
    "details": [
      {
        "field": "limit",
        "reason": "out_of_range"
      }
    ]
  },
  "requestId": "a97493c4-c31e-4794-a193-f57de2b391dc"
}
```

### Error Code Mappings
| Status Code | Error Code | Trigger Condition |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Malformed query/path inputs, invalid/oversized cursors, legacy `page` params, duplicate query parameters. |
| `404` | `NOT_FOUND` | Resource (post or user) does not exist. |
| `409` | `CONFLICT` | Conflict / duplicate action. |
| `422` | `VALIDATION_ERROR` | Unprocessable entity / body validation. |
| `500` | `INTERNAL_ERROR` | Unhandled server exception. Raw internal stack traces are redacted. |
| `503` | `SERVICE_UNAVAILABLE` | Downstream unavailable / bounded readiness failure. |

---

## 7. Environment Variables

Stage A uses typed configuration loaded via `pydantic-settings`:

| Variable | Type | Default | Description |
|---|---|---|---|
| `PORT` | `int` | `8000` | Server listening port (1..65535). |
| `FRONTEND_ORIGIN` | `str` | `http://localhost:5173` | Allowed CORS origins. Also automatically permits local development on port 3000. |
| `DEMO_USER_ID` | `str` | `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa` | Development actor identity matching fixture user "asha". |
| `SIMULATED_IO_MS` | `int` | `0` | Non-blocking simulated I/O latency in milliseconds (0..1000) for concurrency testing. |

> **Security Note:** Stage A does not require or use any database credentials, secret keys, or JWT tokens.

---

## 8. Test Suite & Verification

### Running the Backend Tests
```bash
cd backend
python -m pytest
```
**Current Test Results:**
- **103 passed**, 0 failed, 1 warning (Starlette test client deprecation notice).
- Full coverage over:
  - Startup / shutdown lifespan
  - Feed pagination, boundaries, and tie-breaking
  - UUID validation and error envelopes
  - Request ID propagation and sanitization
  - OpenAPI schema and route definitions
  - Non-blocking async concurrency and overlapping timelines
  - Task cancellation and resource cleanup
  - Raw ASGI lab compliance

### Building the Frontend
```bash
cd frontend
npm run build
```
**Result:** `vite build` completes successfully with `dist/` production assets generated without errors.

---

## 9. Next Stages Roadmap

- **Stage B ([`03_Shared_Database_Modeling_PRD.md`](file:///f:/Instagram/docs/03_Shared_Database_Modeling_PRD.md)):** Shared PostgreSQL schema modeling, ERD, tables, constraints, foreign keys, and seed SQL.
- **Stage C ([`05_Python_Database_Integration_PRD.md`](file:///f:/Instagram/docs/05_Python_Database_Integration_PRD.md)):** Persistence layer connecting FastAPI to PostgreSQL with asyncpg/SQLAlchemy, migrations, and write endpoints.
