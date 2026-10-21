# Decision 05: Owned-Content Lifecycle, Deletion & Concurrency Policy

Decision:      Soft-deletion with tombstoning (`deleted_at`), optimistic concurrency control via integer `version` increment and `If-Match` support, and strict allowlist text edits (`extra="forbid"`).
Options:       1. Hard-deletion (`DELETE FROM posts`): simple, but cascades destruction to other authors' replies and breaks conversation threads with dangling references.
               2. Soft-delete flag without concurrency checks: prone to last-write-wins race conditions when editing simultaneously across multiple devices/tabs.
               3. Soft-deletion with tombstoning (`deleted_at`), versioned optimistic concurrency, and cascade suppression (chosen).
Why this one:  Preserves reply tree continuity without orphaning replies, protects against accidental multi-tab edit overwrites (`409 Conflict`), and ensures immediate, atomic exclusion across all 9 read surfaces.
Delete Policy: Irrevocable state transition (`deleted_at = CURRENT_TIMESTAMP`). Decrements author's active `post_count`. Repeated DELETE is idempotent (`204 No Content`). Cross-user deletion is rejected (`403 Forbidden`).
Surfaces Table:
- Detail (`GET /posts/{id}`): returns 404 for deleted posts.
- Feed (`GET /feed`): excluded (`WHERE deleted_at IS NULL`).
- Search (`GET /search/originals`): excluded (`WHERE deleted_at IS NULL`).
- Profile Media (`GET /users/{id}/media`): excluded.
- Replies (`GET /posts/{id}/replies`): deleted replies excluded; children of deleted parent display tombstone indicator.
- Reposts & Likes: mutations on deleted posts rejected with 404 Not Found.
- Profile Counts: `postCount` counts only original posts with `deleted_at IS NULL`.
Test proving it: [tests/test_api_content_lifecycle.py](file:///f:/Instagram/backend/tests/test_api_content_lifecycle.py)
