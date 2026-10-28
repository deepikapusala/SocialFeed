# Instagram Explore Grid & Social Feed System

A full-stack social feed platform featuring a high-performance **FastAPI** async backend, **PostgreSQL** relational modeling with SQLAlchemy 2.x async ORM / asyncpg, keyset cursor pagination, and an authentic **React** explore feed with responsive multi-image carousels.

---

## 💻 Windows Quick Start Guide (Step-by-Step for Evaluators / Mentors)

This guide is specifically tailored for **Windows (PowerShell or Command Prompt)**. Follow each step sequentially using dedicated terminal windows.

---

### Step 0: Extract the ZIP Archive
1. Right-click the downloaded `.zip` file and select **Extract All...**.
2. Choose an extraction destination (for example: `C:\Instagram` or `D:\Instagram`).
3. Open the extracted folder in **VS Code** (or open Windows Terminal / PowerShell here).

---

### Step 1: System Prerequisites (Windows)

Ensure the following tools are installed and accessible from your Windows terminal:

| Tool | Recommended Version | Verification Command | Windows Installation Link |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11 or higher | `python --version` | [python.org/downloads](https://www.python.org/downloads/) *(Check "Add python.exe to PATH")* |
| **Node.js & npm** | Node 18+ / npm 9+ | `node --version` & `npm --version` | [nodejs.org](https://nodejs.org/) *(LTS version recommended)* |
| **PostgreSQL** | 15 or 16+ | `psql --version` | [enterprisedb.com/downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) |

> [!NOTE]
> **PostgreSQL on Windows:** Ensure the PostgreSQL Windows Service is running (search for `Services` in the Windows Start menu, locate `postgresql-x64-xx`, and verify its status is **Running**).  
> Remember the password you set for the default `postgres` user during installation.

---

### Step 2: Database Setup & Migration (PostgreSQL)

Open a terminal at the project root (`Instagram\`) or use **Windows PowerShell**:

#### 1. Create the Isolated Application Database
Run the following command to create the `instagram_modeling` database:
```powershell
createdb -U postgres instagram_modeling
```
*(Enter your PostgreSQL `postgres` password when prompted).*

> **Alternative (using SQL Shell / psql):**
> If `createdb` is not recognized, run `psql -U postgres` and execute:
> ```sql
> CREATE DATABASE instagram_modeling;
> \q
> ```

---

### Step 3: Backend Setup & Execution (Terminal 1)

Open **Terminal 1** and navigate into the `backend` folder:

```powershell
cd backend
```

#### 1. Configure the Backend `.env` File
Copy the example environment file:
```powershell
# In PowerShell:
Copy-Item .env.example .env

# Or in Command Prompt (CMD):
copy .env.example .env
```

Open `backend\.env` in Notepad or VS Code and update your PostgreSQL password on line 18:
```env
PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
DEMO_USER_ID=aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa
SIMULATED_IO_MS=0
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD_HERE@127.0.0.1:5432/instagram_modeling
DATABASE_CONNECT_TIMEOUT_MS=5000
```
> [!IMPORTANT]
> If your database password contains special characters (such as `#`, `@`, `:`, `/`), URL-encode them (e.g., `#` becomes `%23`, `@` becomes `%40`) or wrap the value in single quotes:  
> `DATABASE_URL='postgresql+asyncpg://postgres:YourPass#123@127.0.0.1:5432/instagram_modeling'`

#### 2. Create and Activate Python Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Or activate on Windows (Command Prompt):
.\venv\Scripts\activate.bat
```
*(If PowerShell shows a script execution error, see the [Troubleshooting section](#windows-troubleshooting--faq) below).*

#### 3. Install Python Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Run Schema Migrations (Alembic)
This creates all database tables, foreign keys, and optimized composite indexes:
```powershell
alembic upgrade head
```

#### 5. Seed Initial Data (Deterministic Dataset)
Populate the 5 core user profiles, 60 original posts, media, mutual follows, and initial likes:
```powershell
psql -U postgres -d instagram_modeling -f ..\db\seed.sql
```
*(Enter your PostgreSQL password when prompted).*

#### 6. Start the FastAPI Backend Server
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Backend API Base:** `http://127.0.0.1:8000`
- **Interactive Swagger UI Docs:** `http://127.0.0.1:8000/docs`
- **Health Live Check:** `http://127.0.0.1:8000/health/live`
- **Database Readiness Check:** `http://127.0.0.1:8000/health/ready`

---

### Step 4: Frontend Setup & Execution (Terminal 2)

Open a **new separate terminal (Terminal 2)** and navigate into the `frontend` directory:

```powershell
cd frontend
```

#### 1. Configure the Frontend `.env` File
Copy the example environment file:
```powershell
# In PowerShell:
Copy-Item .env.example .env

# Or in Command Prompt (CMD):
copy .env.example .env
```
*(Verify `frontend\.env` contains `VITE_API_BASE_URL=http://localhost:8000`).*

#### 2. Install Node Dependencies
```powershell
npm install
```

#### 3. Start the Vite React Development Server
```powershell
npm run dev
```

- **Web Application URL:** Open `http://localhost:5173` in your browser (Google Chrome, Edge, Brave, etc.).

---

## 🔑 Pre-Configured Test Accounts (Seed Dataset)

You can log in immediately with any of the seeded creator accounts to test posting, liking, replying, and following:

| Profile / Display Name | Handle / Username | Password | Bio / Focus Area |
| :--- | :--- | :--- | :--- |
| **Asha Patel** *(Default Demo User)* | `asha` | `TestPassword123!` | Book lover, stationery & study aesthetic 📖📚 |
| **Deepika** | `deepu` | `TestPassword123!` | Artisanal recipes & gourmet food photography ✨🍝 |
| **Sneha** | `sneha` | `TestPassword123!` | Botanical aesthetics & garden flora 🌿🌸 |
| **Anirudh** | `ani` | `TestPassword123!` | Acoustic jams, audio production & beats 🎧🎸 |
| **Virat** | `virat` | `TestPassword123!` | Match day passion, fitness & willow cricket 🏏⚡ |

---

## 🧪 Test Suites & Verification

### Run Backend Regression Tests
Inside the `backend/` directory with virtual environment activated:
```powershell
cd backend
python -m pytest
```

### Run Frontend Production Build Validation
Inside the `frontend/` directory:
```powershell
cd frontend
npm run build
```
*(Validates asset bundling, JSX syntax, and production build without errors).*

---

## 🛠️ Windows Troubleshooting & FAQ

### 1. `psql` or `createdb` is not recognized as an internal or external command
- **Cause:** PostgreSQL's `bin` folder is not in your Windows system `PATH`.
- **Solution:**
  1. Press `Win + S` and search for **Environment Variables**.
  2. Click **Edit the system environment variables** -> **Environment Variables**.
  3. Under **System variables**, select `Path` and click **Edit**.
  4. Click **New** and add your PostgreSQL bin path, typically:
     `C:\Program Files\PostgreSQL\16\bin` (or version `15`, `17`).
  5. Click **OK** on all dialogs and **restart your terminal**.
  - *Quick alternative:* Run commands directly from the **SQL Shell (psql)** app included with PostgreSQL.

### 2. PowerShell Error: `Execution of scripts is disabled on this system`
- **Cause:** Windows PowerShell restricts running scripts by default policy.
- **Solution:** Run this one-time command in PowerShell to allow script execution for the current session:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  Then re-run `.\venv\Scripts\Activate.ps1`.

### 3. Password Authentication Failed / Special Characters in Database URL
- **Cause:** If your database password contains characters like `#`, `@`, or `%`, asyncpg may fail to parse the URI.
- **Solution:** In `backend\.env`, URL-encode the special characters or enclose the full URL string in single quotes:
  ```env
  DATABASE_URL='postgresql+asyncpg://postgres:YourPass%23@127.0.0.1:5432/instagram_modeling'
  ```

### 4. Port 8000 or Port 5173 is already in use
- **Check and free Port 8000 on Windows:**
  ```powershell
  netstat -ano | findstr :8000
  taskkill /PID <PID_NUMBER> /F
  ```
- **Or change port in `.env`:** Change `PORT=8001` in `backend\.env` and update `VITE_API_BASE_URL=http://localhost:8001` in `frontend\.env`.

---

## 🏛️ Architecture & Core Features

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

## 📡 API Endpoints Reference

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

## 🔒 Domain Invariants & Constraint Rules

- **Post Kinds:** Strictly `'original'`, `'reply'`, or `'repost'`.
- **Media Attachments:** Only original posts may own media attachments (0 to 4 media items max, ordered by unique `position`).
- **Replies:** Can only target `original` posts. Nested replies are rejected (`422 Unprocessable Entity`).
- **Reposts:** Can only target `original` posts. Cannot contain new text or media. Duplicate reposts by the same author are rejected (`409 Conflict`).
- **Reactions:** Liking a repost is rejected; users react to the original post. Concurrent duplicate likes are handled idempotently (`ON CONFLICT DO NOTHING`).
- **Keyset Pagination:** Uses opaque base64 tokens encoding `(createdAt, id)` to prevent page-drift anomalies under descending order `(created_at DESC, id DESC)`.

---

## 📚 Comprehensive Documentation Index

- **[`docs/00_Assignment_Brief_and_API_Contract.md`](file:///f:/Instagram/docs/00_Assignment_Brief_and_API_Contract.md):** Authoritative API contract and assignment specifications.
- **[`docs/03_Shared_Database_Modeling_PRD.md`](file:///f:/Instagram/docs/03_Shared_Database_Modeling_PRD.md):** Schema design, ERD diagrams, and constraint rationale.
- **[`docs/05_Python_Database_Integration_PRD.md`](file:///f:/Instagram/docs/05_Python_Database_Integration_PRD.md):** Python/SQLAlchemy integration, repository architecture, and lifecycle rules.
- **[`docs/seed-manifest.md`](file:///f:/Instagram/docs/seed-manifest.md):** Deterministic seed entities, user roles, tie-breaker boundaries, and baseline counts.
- **[`docs/query-plan-report.md`](file:///f:/Instagram/docs/query-plan-report.md):** `EXPLAIN (ANALYZE, BUFFERS)` execution plans and index verification evidence.
- **[`docs/decisions.md`](file:///f:/Instagram/docs/decisions.md):** Architectural decision records (ADRs) covering schema choices, cursor format, and error handling.
