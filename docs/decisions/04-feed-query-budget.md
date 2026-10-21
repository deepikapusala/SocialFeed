# Decision 04: Personalized Home Feed Architecture & Query Budget

Decision:      Personalized home feed composed of eligible active originals from followed users (status = 'accepted') and the viewer, sorted by (created_at DESC, id DESC) using compound keyset cursor pagination with a strict $\le 3$ query-count budget per page.
Options:       1. Fan-out on write (push model): materialize a timeline table per user upon every post creation (fast reads, but massive write amplification on active posters and stale caches on privacy/unfollow changes).
               2. Offset pagination (`LIMIT N OFFSET M`): simple to write, but exhibits $O(N)$ scanning degradation and suffers row duplication/skips when items are posted or deleted between pages.
               3. Fan-out on read (pull model) with compound keyset pagination and composite indexes (chosen).
Why this one:  Guarantees instant visibility of relationship/privacy mutations, eliminates write amplification, and keeps response time bounded regardless of feed depth. Keyset pagination on `(created_at, id)` provides stable pagination with zero duplicate or skipped posts.
Query Budget:  Constant $\le 3$ queries per feed page (Query 1: Session/Viewer Auth, Query 2: Feed Posts with correlated scalar subqueries, Query 3: Eager load of post media & authors via `selectinload`). Zero N+1 query growth.
Empty State:   Explicit onboarding empty state (`items: []`, `nextCursor: null`, `hasMore: false`) when viewer follows nobody and has zero posts. Public global feed remains available via `GET /feed?scope=public`.
Consistency:   Live query consistency on read. If viewer unfollows an author between page 1 and page 2, the unfollowed author's posts will not appear on page 2; page 2 continues smoothly from the last cursor.
Test proving it: [tests/test_api_feed.py](file:///f:/Instagram/backend/tests/test_api_feed.py)
