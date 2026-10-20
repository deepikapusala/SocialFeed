# Decision 02: Handle-Change and Deactivation Policy

Decision:      Handles are immutable after registration in V2; deactivation is a soft-delete (`is_active = FALSE`) accompanied by immediate revocation of all user sessions; profile updates enforce a strict allowlist.
Options:       1. Mutable handles with redirects (complex table tracking handle history, risk of broken mentions and links).
               2. Hard account deletion (violates foreign key integrity with historical posts, likes, and replies).
               3. Immutable handles + soft-deactivation with instantaneous session revocation (chosen).
Why this one:  Immutable handles preserve URL integrity and guarantee permanent mention resolution. Soft-deactivation cuts off access immediately via session invalidation while preserving relational consistency for historical threads without data corruption.
Risks:         Deactivated users must be filtered out of feeds, search queries, and direct profile views; mitigated by filtering `User.is_active.is_(True)` across all read paths.
Test proving it: [tests/test_api_profile.py](file:///f:/Instagram/backend/tests/test_api_profile.py)
