# Decision 06: Notification Inbox, Delivery Guarantees & Atomicity

Decision:      Transactional generation (same DB transaction as source event) with composite unique deduplication keys, strict self-action suppression, keyset-paginated pull inbox, and authoritative COUNT-based unread state.
Options:       1. Separate commit / async outbox worker: decouples writes, but risks ghost notifications if the main transaction rolls back or creates eventual-consistency lag.
               2. In-memory messaging queue without DB persistence: volatile, lost on restart.
               3. Same-transaction atomic insertion with DB UNIQUE constraint deduplication (chosen).
Why this one:  Guarantees atomic consistency: a notification CANNOT claim an action that never committed (rollback of source mutation automatically rolls back notification). Deduplication is enforced at DB constraint level.
Required Source Events & Recipients:
1. Follow / Request Accepted: recipient is the followed user (or requester when accepted).
2. Like: recipient is author of original post; suppressed if liker == author.
3. Direct Reply: recipient is author of target original post; suppressed if replier == author.
4. Repost: recipient is author of referenced original post; suppressed if reposter == author.
Deduplication & Tombstone Policy:
- Unique constraint: (recipient_id, event_type, actor_id, target_post_id) for post-scoped events, and (recipient_id, event_type, actor_id) for follow events.
- Deleted target content displays tombstone indicator without breaking inbox payload.
- 'Mark all read' atomically updates all notifications for recipient where read_at IS NULL up to request timestamp.
Test proving it: [tests/test_api_notifications.py](file:///f:/Instagram/backend/tests/test_api_notifications.py)
