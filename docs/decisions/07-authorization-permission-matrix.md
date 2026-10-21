# Decision 07: Authorization Placement, Route Permission Matrix & Release Controls

Decision:      Two-tier authorization architecture: Identity and Session verification at FastAPI Dependency Injection layer (`get_required_actor` / `get_current_actor_id`), combined with fine-grained Resource Ownership & Relationship authorization at Service and Repository layers. All mutations require verified identity; test/seed shortcuts are strictly disabled in production.
Options:       1. Pure Middleware authorization: lacks domain and entity context (cannot evaluate post author ownership or relationship status before DB load).
               2. Pure Controller authorization: code duplication across endpoints, prone to forgotten checks.
               3. Two-tier Dependency Injection + Domain Service Authorization (chosen): transport-level identity verification decoupled from domain resource ownership rules.
Why this one:  "Who are you" (Authentication) is evaluated deterministically at the transport boundary before handler execution; "May you touch this" (Authorization) is evaluated atomically against current DB state, eliminating TOCTOU races and preventing IDOR vulnerabilities.

## Route / Permission Matrix

| HTTP Method | Route Path | Anonymous | Resource Owner | Related User (e.g. Follower) | Unrelated User | Auth Mechanism |
|---|---|---|---|---|---|---|
| GET | `/health` | 200 OK | 200 OK | 200 OK | 200 OK | Public route |
| POST | `/auth/register` | 201 Created | 400/409 (if duplicate) | N/A | N/A | Public onboarding |
| POST | `/auth/login` | 200 OK | 200 OK | N/A | N/A | Public credential verify |
| POST | `/auth/logout` | 401 Unauthorized | 204 No Content | N/A | N/A | Verified Bearer session |
| GET | `/auth/me` | 401 Unauthorized | 200 OK | N/A | N/A | Verified Bearer session |
| GET | `/feed` | 200 OK (public) | 200 OK (own posts) | 200 OK (personalized) | 200 OK (public) | Optional Bearer identity |
| GET | `/posts/{id}` | 200 OK (if public) | 200 OK | 200 OK (if following) | 404/403 (if author private) | Privacy-aware lookup |
| POST | `/posts` | 401 Unauthorized | 201 Created | 201 Created | 201 Created | Verified Bearer session |
| PATCH | `/posts/{id}` | 401 Unauthorized | 200 OK | 403 Forbidden | 403 Forbidden | Owner match + OCC version |
| DELETE | `/posts/{id}` | 401 Unauthorized | 204 No Content | 403 Forbidden | 403 Forbidden | Owner match |
| POST | `/posts/{id}/like` | 401 Unauthorized | 200 OK (self-like) | 200 OK | 200 OK | Idempotent upsert |
| DELETE | `/posts/{id}/like` | 401 Unauthorized | 200 OK | 200 OK | 200 OK | Idempotent delete |
| POST | `/posts/{id}/repost` | 401 Unauthorized | 422 (no self-repost) | 200 OK | 200 OK | Unique author repost |
| DELETE | `/posts/{id}/repost` | 401 Unauthorized | 200 OK | 200 OK | 200 OK | Idempotent delete |
| GET | `/users/{id_or_handle}` | 200 OK (public) | 200 OK | 200 OK | 200 OK (limited if private) | Privacy projection |
| PATCH | `/users/{id_or_handle}` | 401 Unauthorized | 200 OK | 403 Forbidden | 403 Forbidden | Target == viewer identity |
| POST | `/users/{id_or_handle}/deactivate` | 401 Unauthorized | 200 OK | 403 Forbidden | 403 Forbidden | Target == viewer identity |
| POST | `/users/{id_or_handle}/follow` | 401 Unauthorized | 400 (no self-follow) | 200 OK | 200 OK (pending if private) | Desired-state follow |
| DELETE | `/users/{id_or_handle}/follow` | 401 Unauthorized | 400 | 200 OK | 200 OK | Desired-state unfollow |
| POST | `/users/{id_or_handle}/follow/accept` | 401 Unauthorized | 200 OK (target accepts) | 403 Forbidden | 403 Forbidden | Target user acceptance only |
| GET | `/notifications` | 401 Unauthorized | 200 OK | 403 (if cross-user) | 403 Forbidden | Recipient isolation |
| POST | `/notifications/read` | 401 Unauthorized | 200 OK | 403 Forbidden | 403 Forbidden | Recipient isolation |
| POST | `/notifications/{id}/read` | 401 Unauthorized | 200 OK | 403 Forbidden | 403 Forbidden | Recipient isolation |
| GET | `/search` | 200 OK | 200 OK | 200 OK | 200 OK | Bounded public search |

## Security Controls & Policies

1. **Unknown Fields & Unbounded Input Rejection**:
   - Pydantic models validate bounds (e.g. text 1-280 chars, handle regex `^[a-zA-Z0-9_]{3,30}$`, bio <= 150 chars).
   - Extra fields in strict payload schemas are rejected with standard 422 envelopes.
2. **CORS & Credential Transport**:
   - `allow_credentials=True` is strictly paired with explicit whitelist domains (`FRONTEND_ORIGIN`). Wildcards (`*`) are disallowed.
   - Development localhost origins are excluded when `ENVIRONMENT == "production"`.
3. **Impersonation Defense**:
   - In `ENVIRONMENT == "production"`, test headers (`x-viewer-id`) and `DEMO_USER_ID` fallbacks are prohibited. All mutations require valid Bearer tokens.
4. **Log & Response Sanitization**:
   - Passwords and raw session tokens are never logged.
   - Database stores only PBKDF2/Argon2 password hashes and SHA-256 session token digests.
5. **Observability & Request ID Traceability**:
   - Every request is tagged with a unique `X-Request-Id` (propagated in response headers and error envelopes).
   - Traceable through logs on both allowed and denied access paths.

Test proving it: [tests/test_permission_matrix.py](file:///f:/Instagram/backend/tests/test_permission_matrix.py)
