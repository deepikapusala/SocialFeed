# Release Runbook: Social Feed v2 (Python Track)

This document provides operations and release procedures for deploying **Social Feed v2** to production, satisfying the Stage 7 (`PY-P0-07`) release controls.

---

## 1. Release Overview & Compatibility

Social Feed v2 introduces:
- Stateful authentication and session revocation (`0002_add_auth_and_sessions`).
- Private account follow-request lifecycle (`0003_add_follow_privacy`).
- Feed query performance composite indexes (`0004_feed_indexes`).
- Soft deletion and optimistic concurrency control on posts (`0005_add_post_lifecycle`).
- Notification inbox with exactly-once transactional delivery (`0006_add_notifications`).

### Compatibility with v1:
- **Zero Breaking Contract Changes for Public Reads**: Existing v1 endpoints (`GET /feed`, `GET /posts/{id}`, `GET /users/{id_or_handle}`) remain backwards compatible.
- **V1 Data Forward Upgrade**: Users created under v1 without passwords are treated as legacy accounts; password registration is prompted upon first v2 sign-in.
- **Deleted Content Tombstoning**: V1 clients viewing replies or notifications referencing soft-deleted posts receive graceful tombstone structures (`isDeleted: true`, `text: "[Deleted]"`).

---

## 2. Production Configuration Checklist

Before deployment, verify the following environment variables in production:

| Variable | Required Value | Description |
|---|---|---|
| `ENVIRONMENT` | `production` | Enforces strict authentication; disables test shortcuts (`x-viewer-id`, `DEMO_USER_ID`) |
| `PORT` | `8000` (or host port) | Server HTTP port |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Secure connection string to PostgreSQL database |
| `DATABASE_CONNECT_TIMEOUT_MS` | `5000` | Connection timeout in milliseconds |
| `FRONTEND_ORIGIN` | `https://socialfeed.app` | Explicit production CORS origin (no wildcards `*`) |
| `DEMO_USER_ID` | Valid UUID | Fallback for dev mode only (ignored in production) |

### Security Verification:
1. **Wildcard CORS Prohibition**: Ensure `FRONTEND_ORIGIN` does not contain `*` when credentials are enabled.
2. **Database Pooling**: Set asyncpg connection pool size appropriately (`min_size=10`, `max_size=40`) based on expected concurrent load.
3. **Log Sanitization**: Verify logging transports do not ingest or print raw Authorization headers, passwords, or session tokens.

---

## 3. Database Migration Runbook

All database changes are managed via Alembic migrations.

### Step 1: Pre-migration Snapshot
Take a full PostgreSQL snapshot / logical dump prior to running migrations:
```bash
pg_dump -U postgres -d instagram_modeling -F c -b -v -f pre_release_v2_backup.dump
```

### Step 2: Forward Upgrade Rehearsal
Run Alembic upgrade to apply all pending revisions from `0001` through `0006`:
```bash
cd backend
alembic upgrade head
```

Verify current revision:
```bash
alembic current
# Expected head: 0006_add_notifications
```

---

## 4. Production Smoke Check Script

Run the following curl sequence or automated smoke checks against the running deployment:

### 1. Health Probe
```bash
curl -f -s -H "X-Request-Id: smoke-01" http://localhost:8000/health
# Response: {"status": "healthy"}
```

### 2. User Registration & Login
```bash
# Register test user
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: smoke-02" \
  -d '{"handle": "smoketest", "displayName": "Smoke Test", "password": "SecurePassword123!"}'

# Login test user
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Request-Id: smoke-03" \
  -d '{"handle": "smoketest", "password": "SecurePassword123!"}' | jq -r '.accessToken')
```

### 3. Authenticated Content Creation & Feed Read
```bash
# Create Post
POST_ID=$(curl -s -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"kind": "original", "text": "Smoke test release verification"}' | jq -r '.id')

# Verify in Feed
curl -s -X GET "http://localhost:8000/feed?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.items[0].id'
```

### 4. Permission Matrix & IDOR Check
```bash
# Anonymous mutation must fail with 401
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"kind": "original", "text": "Should fail"}'
# Output: 401

# Cross-user notification marking must fail with 403
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/notifications/00000000-0000-0000-0000-000000000000/read \
  -H "Authorization: Bearer $TOKEN"
# Output: 404 (if not found) or 403 (if wrong recipient)
```

---

## 5. Rollback Plan & Data Considerations

In the event of an operational release abort:

### Application Rollback:
- Revert application container/process to the previous v1 release tag.
- V1 application continues functioning against the v2 database because all schema modifications are additive:
  - New tables (`sessions`, `notifications`) are simply unused by v1.
  - New columns (`is_private` on `users`, `deleted_at`, `version` on `posts`, `status` on `follows`) have default values or allow NULLs.

### Database Downgrade (Emergency Only):
If schema rollback is strictly mandated:
```bash
alembic downgrade -1
```
*Note: Downgrading `0006` or `0005` permanently deletes notifications and post audit history created during the release window. Restoring from snapshot `pre_release_v2_backup.dump` is preferred if data corruption occurs.*

---

## 6. Known Limitations

1. **Async Fanout**: Feed and notifications currently rely on transactional pull queries rather than an asynchronous background worker (Celery/Temporal). High follower fanout (>10,000 followers) should be moved to outbox workers in P1.
2. **Search Indexing**: Search currently utilizes PostgreSQL ILIKE prefix querying. Full-text search or inverted index (e.g. pg_trgm / Elasticsearch) is scheduled for `PY-P1-01`.
3. **Session Purging**: Expired session tokens are ignored at query time (`expires_at > now()`), but physical cleanup of expired session rows should be scheduled via cron.
