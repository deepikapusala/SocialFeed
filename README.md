# Instagram Explore Grid & Social Feed System

A full-stack social feed platform featuring a high-performance **FastAPI** async backend, **PostgreSQL** relational modeling with SQLAlchemy 2.x async ORM / asyncpg, keyset cursor pagination, and an authentic **React** explore feed with responsive multi-image carousels.

---

## 🌐 1. Live Cloud Production Deployment (Immediate Evaluation)

The entire full-stack application is deployed live in the cloud and ready to explore without needing any local setup:

| Service | Provider | Live URL | Description |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | **Vercel** | [https://social-feed-deepikapusalas-projects.vercel.app/](https://social-feed-deepikapusalas-projects.vercel.app/) | Production React 18 / Vite SPA with full explore grid, carousels, modals, and dark mode. |
| **Backend API** | **Render** | [https://social-feed-backend-m32o.onrender.com/](https://social-feed-backend-m32o.onrender.com/) | Live FastAPI Async ASGI Engine with CORS, authentication, and session handling. |
| **Interactive API Docs** | **Swagger UI** | [https://social-feed-backend-m32o.onrender.com/docs](https://social-feed-backend-m32o.onrender.com/docs) | Interactive Swagger UI to inspect and test all API endpoints live. |
| **OpenAPI Spec** | **JSON** | [https://social-feed-backend-m32o.onrender.com/openapi.json](https://social-feed-backend-m32o.onrender.com/openapi.json) | Raw OpenAPI v3.1 schema. |
| **Database** | **Render PostgreSQL** | Singapore Region | Managed cloud PostgreSQL instance running schema and deterministic seed dataset. |

### 🗄️ Cloud Database Credentials & Connection Strings

| Connection Type | Connection String / Command |
| :--- | :--- |
| **External Database URL** *(For local tools, psql, pgAdmin)* | `postgresql://instagram_modeling_user:WaZk9Z0USSex8nF0APKxwCEoZVxgKo4L@dpg-dbh2avu1egvs7398p6g0-a.singapore-postgres.render.com/instagram_modeling` |
| **Internal Database URL** *(Used by Render backend)* | `postgresql://instagram_modeling_user:WaZk9Z0USSex8nF0APKxwCEoZVxgKo4L@dpg-dbh2avu1egvs7398p6g0-a/instagram_modeling` |
| **Direct PSQL CLI Command** | `PGPASSWORD=WaZk9Z0USSex8nF0APKxwCEoZVxgKo4L psql -h dpg-dbh2avu1egvs7398p6g0-a.singapore-postgres.render.com -U instagram_modeling_user instagram_modeling` |

#### How to Re-Seed or Populate the Cloud Database:
From your local Windows terminal at the project root (`Instagram\`):
```powershell
# Set UTF-8 encoding in PowerShell to support bio emojis
$env:PGCLIENTENCODING = "UTF8"

# Execute seed script directly against cloud database
psql "postgresql://instagram_modeling_user:WaZk9Z0USSex8nF0APKxwCEoZVxgKo4L@dpg-dbh2avu1egvs7398p6g0-a.singapore-postgres.render.com/instagram_modeling" -f db\seed.sql
```
*(Or inside `psql`, run `\encoding UTF8` followed by `\i db/seed.sql` and then `\q`).*

---

## 💻 2. Local Windows Setup Guide (Run from ZIP Archive)

If you downloaded the `.zip` archive to run and evaluate locally on Windows, follow these exact step-by-step instructions.

### Step 0: Extract the ZIP Archive
1. Right-click the downloaded `.zip` file and select **Extract All...**.
2. Extract to a clean folder without spaces (e.g., `C:\Instagram` or `D:\Instagram`).
3. Open the folder in **VS Code** (or open Windows Terminal / PowerShell).

---

### Step 1: System Prerequisites (Windows)

Ensure the following tools are installed:

| Tool | Recommended Version | Verification Command | Windows Installation Link |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11+ | `python --version` | [python.org/downloads](https://www.python.org/downloads/) *(Check "Add python.exe to PATH")* |
| **Node.js & npm** | Node 18+ / npm 9+ | `node --version` & `npm --version` | [nodejs.org](https://nodejs.org/) *(LTS version recommended)* |
| **PostgreSQL** | 15 or 16+ | `psql --version` | [enterprisedb.com/downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) |

> [!NOTE]
> Make sure the PostgreSQL Windows Service is running (`services.msc` -> `postgresql-x64-xx` status is **Running**).

---

### Step 2: Database Initialization (Local PostgreSQL)

Open **Windows PowerShell** at the project root (`Instagram\`):

#### 1. Create the Local Database
```powershell
createdb -U postgres instagram_modeling
```
*(Enter your PostgreSQL password when prompted. If `createdb` is not in PATH, use SQL Shell and run `CREATE DATABASE instagram_modeling;`).*

---

### Step 3: Backend Setup & Execution (Terminal 1)

Open **Terminal 1** and navigate into the `backend` folder:
```powershell
cd backend
```

#### 1. Configure the Backend `.env` File
```powershell
# In PowerShell:
Copy-Item .env.example .env

# Or in CMD:
copy .env.example .env
```
Open `backend\.env` in VS Code / Notepad and update line 18 with your local password:
```env
PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
DEMO_USER_ID=aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa
SIMULATED_IO_MS=0
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD_HERE@127.0.0.1:5432/instagram_modeling
DATABASE_CONNECT_TIMEOUT_MS=5000
```
*(Note: If your password contains special characters like `#` or `@`, URL-encode them or wrap in quotes).*

#### 2. Create & Activate Virtual Environment
```powershell
python -m venv venv

# Activate in PowerShell:
.\venv\Scripts\Activate.ps1

# Or activate in CMD:
.\venv\Scripts\activate.bat
```

#### 3. Install Python Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Run Schema Migrations (Alembic)
Creates all versioned tables, constraints, and composite pagination indexes:
```powershell
alembic upgrade head
```

#### 5. Seed Initial Data (Deterministic Dataset)
Populate the 5 core user profiles, 60 original posts, media, follows, and initial likes:
```powershell
$env:PGCLIENTENCODING = "UTF8"
psql -U postgres -d instagram_modeling -f ..\db\seed.sql
```

#### 6. Start the FastAPI Backend Server
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Backend Base:** `http://127.0.0.1:8000`
- **Swagger UI Docs:** `http://127.0.0.1:8000/docs`
- **Liveness Probe:** `http://127.0.0.1:8000/health/live`
- **Readiness Probe:** `http://127.0.0.1:8000/health/ready`

---

### Step 4: Frontend Setup & Execution (Terminal 2)

Open a **separate terminal (Terminal 2)** and navigate into the `frontend` directory:
```powershell
cd frontend
```

#### 1. Configure the Frontend `.env` File
```powershell
# In PowerShell:
Copy-Item .env.example .env

# Or in CMD:
copy .env.example .env
```
*(Verify `frontend\.env` contains `VITE_API_BASE_URL=http://localhost:8000`).*

#### 2. Install Node Dependencies
```powershell
npm install
```

#### 3. Start the React / Vite Development Server
```powershell
npm run dev
```

- **Web Application URL:** Open `http://localhost:5173` (or `http://localhost:3000`) in your browser.

---

## 🔑 3. Pre-Configured Test Accounts (Seed Dataset)

You can log in immediately using the **1-Click Login buttons** in the Sign In modal, or by typing the credentials below:

| Profile / Display Name | Handle / Username | 1-Click Modal Password | Fallback Password | Bio / Focus Area |
| :--- | :--- | :--- | :--- | :--- |
| **Deepika** | `deepu` | `deepika123` | `TestPassword123!` | Artisanal recipes & gourmet food photography ✨🍝 |
| **Sneha** | `sneha` | `sneha123` | `TestPassword123!` | Botanical aesthetics & garden flora 🌿🌸 |
| **Asha Patel** *(Default Demo)* | `asha` | `password123` | `TestPassword123!` | Book lover, stationery & study aesthetic 📖📚 |
| **Anirudh** | `ani` | `ani123` | `TestPassword123!` | Acoustic jams, audio production & beats 🎧🎸 |
| **Virat** | `virat` | `virat123` | `TestPassword123!` | Match day passion, fitness & willow cricket 🏏⚡ |

---

## 🧪 4. Test Suites & Verification

### Run Backend Regression Tests
Inside `backend/` with virtual environment active:
```powershell
cd backend
python -m pytest
```

### Run Frontend Production Build Validation
Inside `frontend/`:
```powershell
cd frontend
npm run build
```
*(Validates asset bundling, JSX syntax, and production build without errors).*

---

## 🛠️ 5. Windows Troubleshooting & FAQ

### 1. `ERROR: character with byte sequence 0x8d in encoding "WIN1252" has no equivalent in encoding "UTF8"`
- **Cause:** Windows terminal defaults to code page `1252` instead of `UTF-8`, and fails to process emojis in the seed dataset.
- **Solution:** 
  In your terminal before running `psql`, execute:
  ```powershell
  $env:PGCLIENTENCODING = "UTF8"
  ```
  Or inside the `psql` shell (`instagram_modeling=>`), run:
  ```sql
  \encoding UTF8
  \i db/seed.sql
  ```

### 2. `psql` or `createdb` is not recognized
- **Cause:** PostgreSQL `bin` folder is not in your Windows system `PATH`.
- **Solution:**
  1. Search for **Environment Variables** in Windows Start menu.
  2. Under **System variables**, edit `Path` and add: `C:\Program Files\PostgreSQL\16\bin` (or version 15/17).
  3. Restart your terminal. *(Or use the built-in **SQL Shell (psql)** app).*

### 3. PowerShell Error: `Execution of scripts is disabled on this system`
- **Cause:** Windows restricts PowerShell script execution by default.
- **Solution:** Run this one-time command in PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  Then re-run `.\venv\Scripts\Activate.ps1`.

### 4. Password Authentication Failed / Special Characters in Database URL
- **Cause:** Characters like `#`, `@`, or `%` in PostgreSQL passwords must be URL-encoded (e.g., `#` becomes `%23`).
- **Solution:** In `backend\.env`, wrap the connection string in single quotes or URL-encode the symbol:
  ```env
  DATABASE_URL='postgresql+asyncpg://postgres:YourPass%23@127.0.0.1:5432/instagram_modeling'
  ```

---

## 🏛️ 6. Architecture & Core Features

```
┌────────────────────────────────────────────────────────┐
│                   React 18 / Vite UI                   │
│   • Uniform 4:5 explore grid & responsive masonry      │
│   • Interactive multi-image carousel (1/3, 2/3, 3/3)   │
│   • Infinite scroll via Intersection Observer          │
│   • Keyboard navigation (Arrows, Escape) & Dark Mode   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP (camelCase, X-Request-Id)
                            ▼
┌────────────────────────────────────────────────────────┐
│              FastAPI Async Application Engine          │
│   • RequestIdMiddleware (UUID tracking & correlation)  │
│   • Dependency Injection (Scoped sessions & actors)    │
│   • Domain Validation & Standardized Error Envelopes   │
└───────────────────────────┬────────────────────────────┘
                            │ SQLAlchemy 2.x Async ORM
                            ▼
┌────────────────────────────────────────────────────────┐
│             PostgreSQL (instagram_modeling)            │
│   • Strict Relational Schema (users, posts, media...)  │
│   • Keyset pagination index: (kind, created_at, id)    │
│   • Idempotent reaction writes: ON CONFLICT DO NOTHING │
│   • Atomic transactions & rollback protection          │
└────────────────────────────────────────────────────────┘
```

---

## 📡 7. API Endpoints Reference

All API endpoints follow strict camelCase payload conventions and include `X-Request-Id` correlation headers:

| Method | Endpoint | Description | Key Query / Body Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health/live` | Liveness probe (process up) | — |
| `GET` | `/health/ready` | Readiness probe (database connectivity `SELECT 1`) | — |
| `GET` | `/feed` | Chronological original post feed | `cursor`, `limit` (1..50) |
| `GET` | `/posts/{id}` | Single post detail with media & author | — |
| `GET` | `/posts/{id}/replies` | Direct replies to an original post | `cursor`, `limit` |
| `GET` | `/users/{id}` | User profile and statistics | — |
| `GET` | `/users/{id}/media` | User profile media items | `cursor`, `limit` |
| `GET` | `/search/posts` | Literal case-insensitive search | `q` (2..80 chars), `cursor` |
| `POST` | `/posts` | Create original post, reply, or repost | `kind`, `text`, `media`, `replyToId`, `repostOfId` |
| `POST` | `/posts/{id}/like` | Like a post (idempotent write) | — |
| `DELETE`| `/posts/{id}/like` | Remove like from a post | — |
| `POST` | `/auth/login` | User login & token generation | `handle`, `password` |
| `POST` | `/auth/register` | New user registration | `handle`, `displayName`, `password` |
| `POST` | `/auth/logout` | Revoke active session token | — |
| `GET` | `/notifications` | List user notifications | `cursor`, `limit` |

---

## 🔒 8. Domain Invariants & Constraint Rules

- **Post Kinds:** Strictly `'original'`, `'reply'`, or `'repost'`.
- **Media Attachments:** Only original posts may own media attachments (0 to 4 media items max, ordered by unique `position`).
- **Replies:** Can only target `original` posts. Nested replies are rejected (`422 Unprocessable Entity`).
- **Reposts:** Can only target `original` posts. Cannot contain new text or media. Duplicate reposts by the same author are rejected (`409 Conflict`).
- **Reactions:** Liking a repost is rejected; users react to the original post. Concurrent duplicate likes are handled idempotently (`ON CONFLICT DO NOTHING`).
- **Keyset Pagination:** Uses opaque base64 tokens encoding `(createdAt, id)` to prevent page-drift anomalies under descending order `(created_at DESC, id DESC)`.

---

## 📚 9. Comprehensive Documentation Index

- **[`docs/00_Assignment_Brief_and_API_Contract.md`](file:///f:/Instagram/docs/00_Assignment_Brief_and_API_Contract.md):** Authoritative API contract and assignment specifications.
- **[`docs/03_Shared_Database_Modeling_PRD.md`](file:///f:/Instagram/docs/03_Shared_Database_Modeling_PRD.md):** Schema design, ERD diagrams, and constraint rationale.
- **[`docs/05_Python_Database_Integration_PRD.md`](file:///f:/Instagram/docs/05_Python_Database_Integration_PRD.md):** Python/SQLAlchemy integration, repository architecture, and lifecycle rules.
- **[`docs/seed-manifest.md`](file:///f:/Instagram/docs/seed-manifest.md):** Deterministic seed entities, user roles, tie-breaker boundaries, and baseline counts.
- **[`docs/query-plan-report.md`](file:///f:/Instagram/docs/query-plan-report.md):** `EXPLAIN (ANALYZE, BUFFERS)` execution plans and index verification evidence.
- **[`docs/decisions.md`](file:///f:/Instagram/docs/decisions.md):** Architectural decision records (ADRs) covering schema choices, cursor format, and error handling.
