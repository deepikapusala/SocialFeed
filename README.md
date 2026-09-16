# Instagram Explore Grid & Social Feed System

A full-stack social feed platform featuring a high-performance **FastAPI** async backend, **PostgreSQL** relational modeling with SQLAlchemy 2.x async ORM / asyncpg, keyset cursor pagination, and an authentic **React** explore feed with responsive multi-image carousels.

---

## 1. Quick Start Guide

### Prerequisites
- **Python:** 3.11+
- **Node.js:** 18+ and `npm`
- **PostgreSQL:** 15+ running locally on port `5432`

---

### Step 1: Environment Setup

1. Copy the example configuration files:
   ```bash
   # In backend/
   cp backend/.env.example backend/.env

   # In frontend/
   cp frontend/.env.example frontend/.env
   ```

2. Configure `backend/.env` with your local PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:<your_password>@127.0.0.1:5432/instagram_modeling
   PORT=8000
   FRONTEND_ORIGIN=http://localhost:5173
   DEMO_USER_ID=aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa
   ```
   *(Note: Special characters like `#` in database passwords must be URL-encoded, e.g. `%23`)*

---

### Step 2: Database Initialization

Initialize the isolated application database `instagram_modeling`:

```bash
# 1. Create isolated application database
createdb -U postgres instagram_modeling

# 2. Execute DDL Schema
psql -U postgres -d instagram_modeling -f db/schema.sql

# 3. Create Composite Performance Indexes
psql -U postgres -d instagram_modeling -f db/indexes.sql

# 4. Insert Deterministic Seed Dataset
psql -U postgres -d instagram_modeling -f db/seed.sql
```

> **Security Note:** The ONLY database targeted by this project is `instagram_modeling`. The `student` database is never accessed or modified.

---

### Step 3: Start the FastAPI Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Server: `http://127.0.0.1:8000`
- Interactive Swagger UI Docs: `http://127.0.0.1:8000/docs`
- OpenAPI Specification: `http://127.0.0.1:8000/openapi.json`

---

### Step 4: Start the React Frontend

```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 2. Test Suites & Verification

### Run Backend Regression Tests
```bash
cd backend
python -m pytest
```
*Executes all 128 automated tests covering ASGI lifespans, cursor encoding, ORM mapping parity, repository operations, error envelopes, and API routes.*

### Run Frontend Production Build
```bash
cd frontend
npm run build
```
*Validates syntax, asset bundling, and TypeScript/JSX compilation with zero errors.*

---

## 3. Architecture & Core Features

```
┌────────────────────────────────────────────────────────┐
│                   React 18 / Vite UI                   │
│   • Uniform 4:5 explore grid & responsive masonry      │
│   • Interactive multi-image carousel (1/3, 2/3, 3/3)   │
│   • Infinite scroll via Intersection Observer          │
│   • Keyboard navigation (Arrows, Escape) & Dark Mode   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP (camelCase, X-Request-Id)
                            ▼
┌────────────────────────────────────────────────────────┐
│              FastAPI Async Application Engine          │
│   • RequestIdMiddleware (UUID tracking & correlation)  │
│   • Dependency Injection (Scoped sessions & actors)    │
│   • Domain Validation & Standardized Error Envelopes   │
└───────────────────────────┬────────────────────────────┘
                            │ SQLAlchemy 2.x Async ORM
                            ▼
┌────────────────────────────────────────────────────────┐
│             PostgreSQL (instagram_modeling)            │
│   • Strict Relational Schema (users, posts, media...)  │
│   • Keyset pagination index: (kind, created_at, id)    │
│   • Idempotent reaction writes: ON CONFLICT DO NOTHING │
│   • Atomic transactions & rollback protection          │
└────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoints Reference

All API endpoints follow strict camelCase payload conventions and include `X-Request-Id` correlation headers:

| Method | Endpoint | Description | Key Query / Body Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health/live` | Liveness probe (process up) | — |
| `GET` | `/health/ready` | Readiness probe (database connectivity `SELECT 1`) | — |
| `GET` | `/feed` | Chronological original post feed | `cursor`, `limit` (1..50) |
| `GET` | `/posts/{id}` | Single post detail with media & author | — |
| `GET` | `/posts/{id}/replies` | Direct replies to an original post | `cursor`, `limit` |
| `GET` | `/users/{id}` | User profile and statistics | — |
| `GET` | `/users/{id}/media` | User profile media items | `cursor`, `limit` |
| `GET` | `/search/posts` | Literal case-insensitive search | `q` (2..80 chars), `cursor` |
| `POST` | `/posts` | Create original post, reply, or repost | `kind`, `text`, `media`, `replyToId`, `repostOfId` |
| `POST` | `/posts/{id}/like` | Like a post (idempotent write) | — |
| `DELETE` | `/posts/{id}/like` | Remove like from a post | — |

---

## 5. Domain Invariants & Constraint Rules

- **Post Kinds:** Strictly `'original'`, `'reply'`, or `'repost'`.
- **Media Attachments:** Only original posts may own media attachments (0 to 4 media items max, ordered by unique `position`).
- **Replies:** Can only target `original` posts. Nested replies are rejected (`422 Unprocessable Entity`).
- **Reposts:** Can only target `original` posts. Cannot contain new text or media. Duplicate reposts by the same author are rejected (`409 Conflict`).
- **Reactions:** Liking a repost is rejected; users react to the original post. Concurrent duplicate likes are handled idempotently (`ON CONFLICT DO NOTHING`).
- **Keyset Pagination:** Uses opaque base64 tokens encoding `(createdAt, id)` to prevent page-drift anomalies under descending order `(created_at DESC, id DESC)`.

---

## 6. Comprehensive Documentation Index

- **[`docs/00_Assignment_Brief_and_API_Contract.md`](file:///f:/Instagram/docs/00_Assignment_Brief_and_API_Contract.md):** Authoritative API contract and assignment specifications.
- **[`docs/03_Shared_Database_Modeling_PRD.md`](file:///f:/Instagram/docs/03_Shared_Database_Modeling_PRD.md):** Schema design, ERD diagrams, and constraint rationale.
- **[`docs/05_Python_Database_Integration_PRD.md`](file:///f:/Instagram/docs/05_Python_Database_Integration_PRD.md):** Python/SQLAlchemy integration, repository architecture, and lifecycle rules.
- **[`docs/seed-manifest.md`](file:///f:/Instagram/docs/seed-manifest.md):** Deterministic seed entities, user roles, tie-breaker boundaries, and baseline counts.
- **[`docs/query-plan-report.md`](file:///f:/Instagram/docs/query-plan-report.md):** `EXPLAIN (ANALYZE, BUFFERS)` execution plans and index verification evidence.
- **[`docs/decisions.md`](file:///f:/Instagram/docs/decisions.md):** Architectural decision records (ADRs) covering schema choices, cursor format, and error handling.
