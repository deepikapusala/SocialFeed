# Decision 03: Follow Graph and Privacy State Model

Decision:      Directional follow edges with an explicit `status` column (`'pending'`, `'accepted'`) backed by compound DB uniqueness on `(follower_id, following_id)`, a DB self-follow check constraint, and a boolean `is_private` flag on users.
Options:       1. Separate `follow_requests` table and `follows` table (requires complex multi-table transactions to promote requests).
               2. Toggle endpoint (`POST /follow` flips between follow/unfollow, vulnerable to retry race conditions).
               3. Single `follows` table with status discriminator and idempotent desired-state endpoints (chosen).
Why this one:  Single table simplifies compound uniqueness, eliminates split-table migration anomalies, and makes desired-state operations (`PUT /follow` and `DELETE /follow`) fully idempotent. Check constraint prevents self-follow at the database engine level.
Risks:         Private accounts require privacy gates across all 6 read surfaces; mitigated by checking active relationship state (`status = 'accepted'`) before returning private resources.
Test proving it: [tests/test_api_follows.py](file:///f:/Instagram/backend/tests/test_api_follows.py)

---

## Relationship State Machine Diagram

```
                ┌───────────────────────────────────────┐
                │            NO RELATIONSHIP            │
                └───────┬───────────────────────┬───────┘
                        │                       │
       [Requester calls]│                       │[Requester calls]
       PUT /follow      │                       │PUT /follow
       (Target is       │                       │(Target is
        PUBLIC)         │                       │ PRIVATE)
                        ▼                       ▼
            ┌───────────────────────┐       ┌───────────────────────┐
            │       ACCEPTED        │       │        PENDING        │
            │   (Active Follow)     │       │    (Follow Request)   │
            └───────┬─────────▲─────┘       └───────┬─────────┬─────┘
                    │         │                     │         │
          [Requester calls]   │[Target approves]    │         │[Target rejects
          DELETE /unfollow    │POST /requests/      │         │ OR requester
                    │         │     {id}/accept     │         │ cancels]
                    │         │                     │         │
                    │         └─────────────────────┘         │
                    ▼                                         ▼
                ┌───────────────────────────────────────┐
                │            NO RELATIONSHIP            │
                └───────────────────────────────────────┘
```
