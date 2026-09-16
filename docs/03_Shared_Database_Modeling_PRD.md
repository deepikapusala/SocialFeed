# PRD 03 — Both tracks: model a social-feed database

**Stage:** B — relational modeling and SQL. **Effort:** 12–16 hours.  
**Database:** PostgreSQL for both cohorts. **Prerequisite:** understand the [social scenario and API contract](00_Assignment_Brief_and_API_Contract.md); a working Stage A server helps but is not necessary to draw the model.  
**Consumers:** [JS integration](04_JS_Database_Integration_PRD.md) and [Python integration](05_Python_Database_Integration_PRD.md).

## Problem and outcome

An array of Post objects cannot enforce relationships across users, likes, media and follows after a restart. The application needs a durable relational model whose rules are visible in keys, constraints and transactions, and whose queries support the screens already built.

Each intern must **design and explain** the model before mapping it with an ORM. This PRD specifies product behavior and evidence; it intentionally does not give a complete solved ERD or SQL schema. Multiple normalized physical designs are acceptable if they satisfy the same contract and the intern can defend their trade-offs.

## Product stories to model

1. A visitor reads an original post, its author, images, reaction count and direct replies.
2. A visitor browses successive pages of originals without repeating the previous page.
3. A user opens a profile and its images with dimensions, alt text and source-size variants.
4. The demo user likes/unlikes once, even when the client retries the request.
5. A user writes a reply or reposts an original without duplicating the original's content.
6. Follow relationships let a future feature select posts from followed authors.
7. A future notification feature can identify who acted, who receives the notification and which post was involved.

Story 7 is an optional extension; the other stories are required. The required endpoint feed remains originals from all users, not an algorithmic or following-only feed.

## Deliverable 1: conceptual model — 2–3 hours

Identify entities, attributes, primary/foreign keys and relationships. The required concepts are **User, Post, PostMedia, Like and Follow**. Post includes original/reply/repost behavior. A separate Comment or Repost relation is acceptable if its joins, keys and API mapping are explicit. Do not mirror every class from the earlier OOP task into a table automatically.

Draw an ERD with cardinality and optionality at both ends. A Markdown table plus Mermaid or another clearly readable diagram is acceptable in the intern's submission. Explain at least these relationships:

- user → authored posts: one-to-many;
- original → direct replies and repost references;
- original → ordered images: zero-to-many, capped at four by the product rule;
- users ↔ posts through likes: many-to-many;
- users ↔ users through directional follows.

Write a data dictionary: column, logical meaning, PostgreSQL type, required/nullable, default, key/constraint and example. Choose UUID public identifiers, `timestamptz(3)` or an equivalent deliberate millisecond-precision policy, and suitable Unicode text types. Record any surrogate IDs used on association rows and why they are needed.

**Mentor checkpoint:** explain one alternative physical model and why you selected yours before writing ORM models.

## Deliverable 2: constraints and normalization — 3–4 hours

The following rules must have an explicit enforcement location. Use database constraints for local relational invariants wherever possible; document checks that require looking at other rows or counting a collection.

| Rule | Required enforcement/evidence |
|---|---|
| Unique normalized user handle | Database uniqueness; lowercase policy and invalid-handle example |
| Every author/like/media/follow/reference points to an existing row | Foreign keys; demonstrate an orphan insert failing |
| One user can like a given post once | Composite uniqueness; duplicate/concurrent insert evidence |
| No duplicate follow pair or self-follow | Uniqueness plus same-row check |
| Original/reply text is trimmed and 1–280 code points | Validated service input plus appropriate database checks for stored values |
| Repost has no new text and only a repost target | Kind/reference/text combination checks in the chosen model |
| Reply/repost target must be an original | Document a service lookup or database mechanism; a foreign key alone checks existence, not target kind |
| No user can repost the same original twice | Database uniqueness in the chosen model; conflict demonstrated |
| Media belongs only to an original, maximum four | Document enforcement; a row check alone cannot count sibling rows |
| Image dimensions positive, nonempty URL variants, alt text present | Column/check constraints and input validation; meaningful alt text needs review |
| Each media position unique within a post | Composite uniqueness and position range 0–3; zero-based order documented |
| Like counts, reply counts and follower counts are accurate | Derive from related rows; no caller-controlled cached counters in core scope |

Explain first through third normal form in terms of this scenario: no comma-separated likes/followers, no copied author profile on every post, no repeated repost content, and no stored count that can silently disagree with association rows. A few fixed URL variants on a media row are acceptable here; a separate variant table is an optional richer model, not a prerequisite.

Choose and document `ON DELETE` behavior for each foreign key. User/post deletion endpoints are outside scope, but test chosen policies on disposable data. An acceptable policy may restrict deleting a referenced original while cascading its media/likes only when deletion is permitted. Do not mix hard/soft deletion accidentally or leave the behavior unexplained.

**Important:** PostgreSQL `CHECK` constraints cannot be used as a general solution for arbitrary cross-row rules. Distinguish database guarantees, application validations and transactional enforcement. Avoid inventing triggers for every rule just to increase the schema's size.

## Deliverable 3: executable schema and deterministic seed — 2–3 hours

Create the schema in an isolated modeling database using reviewed SQL. Deliver `schema.sql` plus `seed.sql` or a documented deterministic seed script. This is the Stage B design artifact; Stage C generates versioned application migrations from it and verifies parity rather than blindly running both creation paths.

Seed at least **6 users, 30 originals, 12 replies, 4 reposts, 10 media rows, 15 likes and 8 follow edges** with the cases listed in the shared brief. Use recognizable fixed IDs, fixed UTC timestamps and known relationships. Include two originals with identical timestamps and arrange a page boundary through a tie.

Create a seed manifest listing sample IDs, expected entity counts, one user's follower/following counts and one original's exact like/reply counts. Re-running the seed must not duplicate logical data; document idempotent upsert behavior or an explicit clean-database-only command. Do not reset a developer's database implicitly as part of ordinary application startup.

Submit `constraint-tests.sql` or a test script that demonstrates both valid and rejected data. Run negative cases inside transactions/savepoints so expected errors do not prevent the remaining checks.

## Deliverable 4: ten SQL use cases — 3–4 hours

Write parameterized query examples, explain their inputs and show expected output from the seed. Parameters are values, not string-concatenated SQL. For every list query, consider empty results and duplicates introduced by joins.

1. **Home feed:** originals with author data, newest tuple first, `limit+1`, first and continuation page. Apply selection before multiplying rows through media/like joins.
2. **Post detail:** one post with author and target reference where relevant, plus correct like/reply counts.
3. **Direct replies:** replies to one original, stable descending timestamp/ID and continuation.
4. **Profile media:** images for one user's originals, with alt text/dimensions/variants and stable media cursor.
5. **Profile statistics:** number of originals, followers and following for a user, including users with zero values.
6. **Like totals:** counts for a batch of feed post IDs, including zero-liked posts.
7. **Viewer state:** which of those posts the demo user has liked without N per-post queries.
8. **Following-feed exercise:** originals by followed authors; no duplicate rows; explain how this would differ from the core public feed endpoint.
9. **Search:** case-insensitive literal text match with escaped `%`/`_`, stable pagination and no-match behavior.
10. **Repost lookup:** list a user's reposts and each original/author without storing duplicated original text.

Do not write one enormous join that inflates counts by multiplying likes, replies and media. Use separate aggregate/subqueries or a bounded batch strategy and explain why its numbers are correct.

## Deliverable 5: indexes and transactions — included across the SQL/constraint time

Propose at least three useful indexes for actual access paths: feed ordering/filter, reply lookup/order, author/media lookup, follow lookup or reaction membership/counts. List which indexes PostgreSQL already creates for keys/uniqueness so you do not duplicate them without reason.

Run `EXPLAIN (ANALYZE, BUFFERS)` for two read queries before/after a candidate index on disposable development data. The small seed may correctly favor sequential scans. Either explain that result or generate a clearly labeled larger dataset; no invented speedup and no required percentage improvement. Describe write/storage cost as well as read benefit.

Demonstrate a real transaction: insert a valid like, then attempt an invalid foreign-key write in the same transaction and roll back. Verify neither partial effect survives. Use two connections/requests to insert the same like concurrently; prove the uniqueness rule prevents two rows. Explain which transaction/constraint behavior supports ACID; normalization alone does not guarantee ACID.

## Acceptance checklist

- [ ] ERD, cardinalities, dictionary and alternative-design reasoning are present.
- [ ] Core concepts and all product rules have an enforcement location.
- [ ] Schema creates successfully in an empty isolated database.
- [ ] Seed meets minimums and its manifest counts can be queried.
- [ ] Duplicate like/follow/repost, self-follow, orphan reference and malformed post/media cases are tested.
- [ ] Direct SQL tests demonstrate the rules actually guaranteed by the database; service-only rules are labeled honestly.
- [ ] Ten SQL use cases return correct seeded results, including zero-count and pagination ties.
- [ ] Two query-plan reports explain observed access paths without fabricated improvements.
- [ ] Rollback and a concurrent duplicate-like attempt are demonstrated.
- [ ] Deletion policy and migration handoff are documented.

## Handoff and mentor review

Submit `docs/erd.md`, `docs/data-dictionary.md`, `docs/decisions.md`, `db/schema.sql`, seed files, `db/constraint-tests.sql`, `db/queries.sql` and `docs/query-plan-report.md`. Equivalent paths are fine if the README links them.

The mentor asks: why a like is a relation rather than just a counter; how a reply differs from a repost; why the cursor includes two fields; what a foreign key does not validate; why a join can inflate counts; and what happens when two requests like the same post.

**Gate:** the model is executable, the evidence is reproducible and the intern can explain it. Stage C may begin after review. A diagram exported from an ORM without independent SQL evidence is insufficient.

## Optional extension: notification modeling

Model recipient, actor, event type, optional target post, created timestamp and read timestamp. Explain which event kinds need a post reference, what happens after target deletion, and which stable source-event ID prevents duplicate notification rows. Seed examples and write an unread-list query. Do not require delivery queues, real-time transport or a generic JSON-only event table for the core assignment.

## Free resources

- [PostgreSQL data definition](https://www.postgresql.org/docs/current/ddl.html), [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) and [indexes](https://www.postgresql.org/docs/current/indexes.html).
- [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html), [transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html) and [EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).
- [SQLBolt](https://sqlbolt.com/) for a short syntax repair; [SQLZoo](https://sqlzoo.net/wiki/SQL_Tutorial) for practice. Complete the scenario queries even if you finish these exercises.
