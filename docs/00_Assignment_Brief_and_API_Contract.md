# Social Feed Backend — intern assignment brief and shared contract

**Audience:** interns who completed the supplied tweet/profile/feed JavaScript or Python hands-ons.  
**Scenario:** a small social application called **Social Feed**, connecting their existing tweet detail, profile, search, like button and infinite-scroll pages to a server and then PostgreSQL.  
**Purpose:** learn the HTTP request lifecycle, server organization, relational modeling, constraints, migrations and persistent API behavior.  
**Status:** ready to assign; all estimates are per intern and exclude optional extensions.

## Assignment order

| Stage | JS track | Python track | Estimate | Review gate |
|---|---|---|---:|---|
| A: server foundations | [PRD 01: Node/NestJS setup](01_JS_Server_Setup_PRD.md) | [PRD 02: Python/FastAPI setup](02_Python_Server_Setup_PRD.md) | 10–12 h | Runnable server with deterministic fixture responses |
| B: scenario modeling | [PRD 03: shared PostgreSQL modeling](03_Shared_Database_Modeling_PRD.md) | Same PRD, independently completed | 12–16 h | ERD, dictionary, constraints, seed and SQL evidence |
| C: persistence | [PRD 04: NestJS database integration](04_JS_Database_Integration_PRD.md) | [PRD 05: FastAPI database integration](05_Python_Database_Integration_PRD.md) | 10–14 h | Same frontend works against persisted data |
| Review | Individual demo and feedback | Individual demo and feedback | 2 h | Explain the request, query and failure paths |

Total: **34–44 hours per intern**, normally spread across about 7–10 working days depending on allocated hours and review availability. These estimates are for interns; the separate personal six-hour/day learning plan is not their schedule. Model review may begin while the server is being built, but persistence begins after the model is reviewed.

Each intern submits their own reasoning and tests. Cohort members may agree on fixtures and the API contract, then implement independently. Use a short feature branch and PR per stage, such as `intern/<name>/social-server`, `social-schema` and `social-persistence`. Attach the checklist and demo evidence to each PR. A mentor reviews each gate before the next dependent stage.

## Connection to the completed hands-ons

| Previous exercise | What this assignment adds |
|---|---|
| 1, 3: semantic tweet detail, thread, reply box and responsive images | Post/author/media response contract, reply relationship and persisted reply |
| 2: profile grid and horizontal image row | User/media model and paginated profile media data; existing layout can consume either display |
| 4: debounced search | A validated search endpoint; debounce remains a browser responsibility |
| 5: optimistic likes and event-loop logging | Explicit set-like/unlike operations, authoritative counts and rejection behavior |
| 6, 12: Post/Tweet/Comment/Retweet classes | Translate domain relationships into tables; class inheritance does not require table inheritance |
| 7: pure feed filter/sort/deduplicate | Server-defined eligibility/order and SQL querying; keep presentation transforms pure |
| 8: bounded lazy-image queue | Media URLs and dimensions; downloading/rendering concurrency remains client-side |
| 9: infinite scroll | Stable cursor pagination, retry and response IDs that support client deduplication |
| 10: Observer/toast notifications | Persistable event relationships are an optional modeling extension; no broker/WebSocket work yet |
| 11: generator paginator | A bounded repository/page iterator that does not load the full database feed |
| 13: `cache_feed(ttl=30)` | An optional cache exercise after correct uncached persistence |
| 14: async FastAPI cursor endpoint | Clear request schemas, repository boundary, lifecycle and real database queries |

Two corrections to carry forward: `.map()` by itself does not cause layout thrashing; interleaved layout reads and DOM writes can cause forced synchronous layout. Also, `functools.lru_cache` does not supply TTL behavior by itself. Any optional cache must define expiry and invalidation explicitly; never cache an async coroutine object as if it were its completed result.

## Scope boundaries

**Required now:** local development setup, validated HTTP APIs, deterministic fixtures, five core relational concepts, seeds, query exercises, migrations, cursor pagination, read endpoints and three write behaviors: create a post/reply/repost, like and unlike.

**Later:** registration/login/JWT, private accounts, upload processing, image transformation, recommendation algorithms, Redis, WebSockets, event brokers, email/push notifications, deploy pipelines and microservices. Optional work never substitutes for a failed core requirement. Keep the exercise local or in a private training environment until real authentication is introduced.

## Product rules shared by both tracks

1. A user has a unique lowercase handle, display name, optional bio and avatar URLs.
2. A post has a unique ID, author, creation timestamp and one of three kinds: `original`, `reply`, `repost`.
3. Originals and replies contain trimmed text of 1–280 Unicode code points. Replies reference one existing original post. This assignment supports one reply level; replies-to-replies are rejected.
4. A repost contains no new text or media and references one existing original. Reposting a reply or repost, and quote-posting, are deferred. A user can repost a particular original only once.
5. An original can have zero to four images. Store URL variants, dimensions, alt text and display order. Avatars may use a few scalar variant fields; a generalized image-processing service is not needed.
6. A user can like an original or a reply once. Liking a repost row is rejected; its UI can link to and like the referenced original instead. Counts come from relationships, not caller-supplied numbers.
7. A follow is directional: A following B does not imply B following A. No self-follow and no duplicate pair. Follows are seeded and modeled now; follow/unfollow endpoints are optional.
8. The core feed is public, reverse-chronological **originals only** from all users. Replies and reposts appear in their dedicated response/detail context and database exercises; a following-only or repost-mixed feed is an extension.
9. No runtime deletion of posts/users is required. Model and demonstrate deletion policies on disposable database fixtures anyway, so orphan handling is explicit.
10. Server timestamps are UTC. Use UUID strings for public IDs and millisecond precision for creation timestamps so both language tracks can round-trip the pagination key consistently.

These deliberate restrictions keep this an introductory backend assignment with a clear finish line. They are product requirements for the training scenario, not claims about Twitter or Instagram's actual implementation.

## Development identity

For Stage C writes, resolve the actor from a validated `DEMO_USER_ID` environment setting referencing a seeded user. The browser does **not** choose an arbitrary `userId` or like count in a write body. Reads use the same demo user for `likedByViewer`. In tests, override the identity dependency to simulate another actor.

This is a local training identity, **not authentication**. Reject missing/unknown configuration at startup or readiness before enabling writes. Document it prominently. Adding real authentication is a later assignment.

## API inventory and release stages

Paths below are exact and deliberately unversioned so the existing `/feed` exercise can connect directly. API versioning is a later topic.

| Method/path | Stage A: fixture server | Stage C: persisted server | Success |
|---|---|---|---|
| `GET /health/live` | Required | Required | 200 `{ "status": "ok" }` |
| `GET /health/ready` | Optional | Required: bounded DB check | 200 ready / 503 unavailable |
| `GET /feed?cursor=...&limit=10` | Required | Required | 200 paginated originals |
| `GET /posts/{id}` | Required | Required | 200 detail or 404 |
| `GET /users/{id}` | Required | Required | 200 profile or 404 |
| `GET /posts/{id}/replies?cursor=...&limit=10` | Extension | Required for original ID | 200 direct replies |
| `GET /users/{id}/media?cursor=...&limit=10` | Extension | Required | 200 user's original-post images |
| `GET /search/posts?q=...&cursor=...&limit=10` | Extension | Required | 200 matching originals |
| `POST /posts` | Not required | Required | 201 created original/reply/repost |
| `PUT /posts/{id}/like` | Not required | Required | 200 authoritative state |
| `DELETE /posts/{id}/like` | Not required | Required | 200 authoritative state |

Only `cursor` and `limit` pagination are supported. Passing legacy `page` returns 400 with a useful validation error; update the existing frontend to save `nextCursor`. List endpoints return 404 for a missing parent user/post and an empty list for an existing parent with no matching items. Requesting `/replies` for a non-original is 422.

## Shared response shapes

CamelCase is the wire format for both tracks. Database columns/Python internals may use snake_case. Shapes are contracts, not suggested database tables.

### Post item and detail

```json
{
  "id": "11111111-1111-4111-8111-111111111111",
  "kind": "original",
  "text": "My first database-backed post",
  "createdAt": "2026-09-01T10:00:00.000Z",
  "author": {
    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "handle": "asha",
    "displayName": "Asha",
    "avatar": { "smallUrl": "/fixtures/asha-48.jpg", "largeUrl": "/fixtures/asha-96.jpg" }
  },
  "media": [
    {
      "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      "altText": "A desk with a laptop",
      "width": 1200,
      "height": 800,
      "position": 0,
      "smallUrl": "/fixtures/desk-480.jpg",
      "largeUrl": "/fixtures/desk-1200.jpg"
    }
  ],
  "likeCount": 2,
  "replyCount": 1,
  "likedByViewer": false,
  "replyToId": null,
  "repostOfId": null
}
```

`GET /posts/{id}` returns that item under `{ "item": ... }`. A reply uses non-null `replyToId`; a repost uses non-null `repostOfId`, `text: null` and `media: []`. Detail may add `referencedPost: {id,text,author}` for a repost so clients do not infer duplicated source data. Profile response: `{ "item": {id,handle,displayName,bio,avatar,postCount,followerCount,followingCount} }`; `postCount` counts originals only.

### Paginated lists

```json
{
  "items": [],
  "nextCursor": null,
  "hasMore": false
}
```

Feed, replies and search items use the post shape. Profile media items use `{id,postId,createdAt,position,altText,width,height,smallUrl,largeUrl}`. The browser uses returned variants to build `srcset`; the server does not return an HTML string. Fixture URLs must resolve from a documented local asset origin or be mapped to existing frontend assets.

### Cursor rules

- Default `limit=10`; accept a single integer from 1 through 50. Reject zero, negatives, fractions, nonnumbers, values over 50 and duplicate parameters with 400.
- Order post lists by `(created_at DESC, id DESC)`. Store timestamp precision consistently at milliseconds. Each continuation selects rows with a tuple **strictly smaller** than the last returned tuple, not `OFFSET` rows.
- Encode `{ "v": 1, "createdAt": "...", "id": "..." }` as base64url JSON. Cursor is an opaque client continuation token, not an authorization credential. Validate length (maximum 1,024 characters), encoding, version, timestamp and UUID. Invalid cursors return 400; valid cursors need not point to a still-existing row.
- Read at most `limit + 1` matching records, return at most `limit`, and derive `hasMore` from the extra record. Only issue a cursor when there is another page, using the last returned item.
- Profile media uses the media row's immutable `(created_at,id)` tuple, avoiding ambiguity when one post has several images. Display order within a post remains `position`; profile media is newest-media first with ID tie-breaking.
- These are live lists, not historical snapshots. Test no duplicates/skips on an unchanged seed and no repeat of already-seen items when a newer original is inserted. Do not promise snapshot completeness across backdated insertions or eligibility changes.
- Treat cursor as scoped to the current route/filter. The frontend clears it on a new query or profile; the server always reapplies current route and search filters. No full result count is required.

### Writes

Original: `POST /posts` with `{ "kind": "original", "text": "Hello" }`. Reply: `{ "kind": "reply", "text": "Good point", "replyToId": "<original UUID>" }`. Repost: `{ "kind": "repost", "repostOfId": "<original UUID>" }`. Runtime media creation is optional; seeded media satisfies the image requirements.

For create requests, reject unknown fields, caller-selected IDs/timestamps/author, and inconsistent kind/reference combinations. Body validation failures use 422. Each successful create returns `{ "item": <post item> }`. A duplicate repost returns 409. Missing target is 404; an existing target of an unsupported kind is 422. `POST` creation is not automatically idempotent: the frontend disables repeated submission, and generic retry-safe post creation is deferred.

Like/unlike have no body. Both return `{ "postId": "<UUID>", "likedByViewer": true, "likeCount": 3 }` with the appropriate state. Repeated like keeps the state liked; repeated unlike keeps it unliked. Do not expose an increment/decrement or toggle endpoint. This lets optimistic UI recover from a retry without toggling twice. Serialize rapid like/unlike intents on the client and reconcile to the final server response.

Search is case-insensitive literal substring matching on original text after trimming `q`; accept 2–80 Unicode code points, otherwise 400. Parameterize SQL and treat `%` and `_` as literal user text, not wildcard operators. Always apply ordering and pagination after filtering. Search engines and full-text ranking are optional later work.

### Error envelope

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "limit must be an integer from 1 to 50",
    "details": [{ "field": "limit", "reason": "out_of_range" }]
  },
  "requestId": "opaque-request-id"
}
```

Codes: `VALIDATION_ERROR` (400 query/path, 422 body/domain), `NOT_FOUND` (404), `CONFLICT` (409), `SERVICE_UNAVAILABLE` (503 database unavailable), `INTERNAL_ERROR` (500). Malformed JSON is 400. Malformed path UUID is 400; well-formed absent UUID is 404. Return the same request ID in `X-Request-Id`; log it with method/path/status/duration, without bodies, secrets or connection strings. Framework default validation responses must be mapped to this contract in Stage A/C.

## Fixtures, failure demonstrations and frontend checks

Use at least **6 users, 30 originals, 12 replies, 4 reposts, 10 media rows, 15 likes and 8 follow edges**. Include two originals sharing a timestamp, a user with no media, an original with no reactions, a liked original, an empty search result and three distinct feed pages. Stage A may store the data as objects/JSON; Stage B/C must persist equivalent records. Include all fields and use fixed IDs/timestamps for reproducibility.

Simulated I/O latency is enabled only by documented local configuration and uses a nonblocking wait. Deterministic write-failure simulation belongs in a test override or local-only documented mode; one deliberately failed like must leave stored state unchanged so the existing button demonstrates rollback. Do not make ordinary behavior randomly fail.

Connect the existing infinite-scroll and tweet-detail pages: request page one, follow the cursor, show the skeleton while pending, show retry on a controlled error, deduplicate IDs on repeated responses and stop observing when `hasMore=false`. Connect profile media and search in Stage C. Preserve semantic structure, image alt text and keyboard access. Record a short manual screen-reader pass of the integrated tweet page using available screen-reader software; list tool/version, steps and actual findings. Automated accessibility results are supporting evidence, not a claimed screen-reader test.

After development, record before/after DevTools Performance traces for the existing intentional layout-read/write exercise. Identify the exact forcing code, batch layout reads/writes or otherwise fix the cause, and repeat the same viewport/data/throttling conditions. Explain separately server response time, image/network work and browser layout. Do not attribute every slow `.map()` to layout thrashing or treat one Lighthouse score as production performance evidence.

## Common completion rule

The mentor must be able to follow the README from a clean checkout, run the tests and inspect an actual request and SQL query. Every intern explains: where inputs are validated, where product rules live, where data is accessed, which database constraint prevents duplicates, how the cursor works, and what happens when the database or a write fails. A generated project scaffold alone does not pass.
