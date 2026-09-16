# Legacy Prototype Scripts (Points 12–14)

This folder contains early standalone mock files and practice exercises created during initial prototyping:

- `data.py`: Initial 12-post mock dictionary.
- `feed.py`: Initial standalone feed cache decorator (`@cache_feed`).
- `models.py`: Simple initial OOP classes (`Post`, `Comment`, `Like`).
- `main.py`: Initial standalone single-file FastAPI server.
- `test_models_cache.py`: Unit tests for the initial cache decorator and simple models.

### Active Production Architecture
The active production application does not use these files. Instead, it uses:
- **FastAPI Application:** `backend/app/` (`app.main`, `app.api`, `app.models`, `app.repositories`, `app.services`, `app.schemas`).
- **PostgreSQL Database:** `db/seed.sql` and `db/indexes.sql` against database `instagram_modeling`.
- **Frontend Feed:** `frontend/src/data/extendedFeed.js` and `frontend/src/utils/api.js`.
