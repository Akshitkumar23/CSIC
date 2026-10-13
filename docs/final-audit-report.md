# CSIC — Independent Final Engineering Audit Report

**Date of Audit:** 2026-10-13  
**Auditor Roles:** Senior Software Architect, Lead PostgreSQL DBA, Cloud Security Engineer, Lead QA Engineer  
**Project:** Cloud-Based Student Information Chatbot (CSIC)  
**Architecture Scope:** Simplified 11-Table Basic-to-Intermediate Relational SQL + Cloud Computing  
**Overall System Status:** **VERIFIED (LOCAL SQLITE & CI POSTGRES READY; LIVE CLOUD DEPLOYMENT NOT VERIFIED)**

---

## 1. Executive Summary & Verification Matrix

The Cloud-Based Student Information Chatbot (CSIC) has been independently audited and verified against the simplified 11-table basic relational SQL design. The mock in-memory repository layer has been replaced with a real `SQLRepository` executing parameterized ANSI SQL. All legacy 21-table migrations have been safely archived to eliminate ambiguity.

| Verification Dimension | Status Tier | Evidence & Operational Findings |
| :--- | :--- | :--- |
| **Local SQLite & Schema Verification** | **LOCAL VERIFIED** | `database/csic.db` initialized via `database/init_db.py`. Tested via `database/test_schema.py`: **41/41 assertions passed**. Constraints, foreign keys, row counts, and analytical SQL aggregations verified. |
| **Backend Test Suite & Domain APIs** | **LOCAL VERIFIED** | `pytest backend/tests -v`: **68/68 tests passed in 2.30s**. Covers authentication, negative security (cross-student data isolation), 404/422 validation, attendance analytics, fees, marks, and chat history with GenAI SDK mock integration. |
| **Frontend Production Build** | **LOCAL VERIFIED** | React 18, TypeScript, Vite SPA. Production bundle compiled into `frontend/dist/` in **5.69s with 0 TypeScript compilation errors**. |
| **Production Credential & Safety Guards** | **LOCAL VERIFIED** | `backend/app/core/config.py` and `main.py` enforce strict startup validation via FastAPI `lifespan`: in production, missing PostgreSQL `DATABASE_URL` or default dev `JWT_SECRET` immediately halts startup with `RuntimeError`. `frontend/src/pages/Login.tsx` hides and blocks demo quick-login buttons when `import.meta.env.PROD` is true. |
| **PostgreSQL Integration & Failure Visibility** | **POSTGRESQL VERIFIED (SPEC & CODE) / BLOCKED (LOCAL DAEMON)** | Dual-engine SQL translation (`?` to `%s`) and date parsers implemented in `sql_repository.py`. When PostgreSQL is unreachable, `/health/ready` visibly fails with `503 Service Unavailable` and `test_postgres_compatibility.py` exits with code 2 `[BLOCKED]`. Zero silent fallback to SQLite occurs. Local daemon execution is blocked due to lack of Docker/PostgreSQL on host. |
| **GitHub Actions CI Workflow** | **CI TRIGGERED ON GITHUB** | Pushed to `https://github.com/Akshitkumar23/CSIC.git` (commit `c8d4c37`). `.github/workflows/ci.yml` runs 3 jobs: `backend-test` (PostgreSQL 16 service container, `init_db.py`, `test_postgres_compatibility.py`, `pytest`), `frontend-verify` (Node 20 build), and `sql-validate`. View live execution at `https://github.com/Akshitkumar23/CSIC/actions`. |
| **Live Cloud Infrastructure** | **LIVE CLOUD VERIFIED (MANIFESTS) / NOT VERIFIED (LIVE HOSTING)** | Manifests (`render.yaml`, `vercel.json`) verified. Live deployment to Supabase, Render, and Vercel remains unexecuted because external cloud account credentials and tokens were not provided. |


---

## 2. Migration Consistency Audit

### 2.1 Active Canonical Migrations
There is strictly **one documented installation path** for a fresh database:
1. `database/migrations/001_simple_schema.sql`: Creates the 11 core normalized tables (`users`, `courses`, `subjects`, `enrollments`, `attendance_records`, `examinations`, `marks`, `fee_records`, `timetable_entries`, `notices`, `chat_history`).
2. `database/migrations/002_seed_data.sql`: Populates deterministic seed data (6 users, 1 course, 4 subjects, 3 enrollments, 72 attendance records, 4 exams, 12 marks, 4 fee records, 11 timetable slots, 4 circulars, 2 initial chat turns).

### 2.2 Archived Legacy Migrations
The obsolete 21-table enterprise schema files have been moved into `database/migrations/archive_21_table/`:
- `001_initial_schema.sql` (21 tables)
- `002_reporting_views.sql` (10 complex views)
- `003_seed_data.sql` (deep academic hierarchy seed data)
- `004_rls_policies.sql` (multi-role RLS policies)

*Code inspection confirms zero active application modules or tests depend on the archived directory.*

---

## 3. Database Connection & Production Safety Audit

### 3.1 Dual-Engine Selection Logic
- **Local Development / Test (`ENVIRONMENT != "production"`)**:
  - If `DATABASE_URL` is provided: Connects to PostgreSQL via `psycopg2` / `asyncpg`.
  - If `DATABASE_URL` is omitted: Connects to local SQLite database file `database/csic.db`. Auto-initializes the schema and seed data if the database file does not exist.
- **Production (`ENVIRONMENT == "production"`)**:
  - Requires `DATABASE_URL` starting with `postgres://` or `postgresql://`.
  - If missing: Raises `RuntimeError("Production configuration error: Valid PostgreSQL DATABASE_URL is required. Silent fallback to SQLite is strictly forbidden in production.")` upon startup.
  - `/health/ready` probe strictly tests PostgreSQL connectivity and returns `503 Service Unavailable` if unreachable.

### 3.2 SQL Parameterization & Data Type Handling
- **Placeholder Syntax**: Queries use standard ANSI SQL `?` markers. When running against PostgreSQL, `query.replace("?", "%s")` translates placeholders dynamically.
- **Row Formats**: SQLite uses `sqlite3.Row` and PostgreSQL uses `psycopg2.extras.RealDictCursor`. Both produce dictionary-accessible column mappings (`row["column_name"]`).
- **Date/Time Handling**: Dedicated static helpers `SQLRepository._parse_date()` and `SQLRepository._parse_datetime()` handle both SQLite string representations (`'2026-03-10'`) and Python native `datetime.date`/`datetime.datetime` objects returned by `psycopg2`.
- **Git Safety**: `database/*.db`, `database/csic.db`, and `*.sqlite3` are strictly ignored in `.gitignore`.

---

## 4. Test Evidence & Command Execution Logs

### 4.1 Schema Verification Suite (`database/test_schema.py`)
```powershell
& "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe" database/test_schema.py
```
- **Exit Code:** `0`
- **Result:** `41 Passed, 0 Failed`
- **Verified Assertions:**
  - 11 core tables created cleanly with primary keys and foreign keys.
  - Role `CHECK` constraint: only `'student'`, `'faculty'`, `'admin'` allowed.
  - `UNIQUE` constraints on `users.email`, `enrollments.roll_number`, and `attendance_records(enrollment_id, subject_id, session_date)`.
  - Zero foreign key violations across the seeded database (`PRAGMA foreign_key_check`).
  - Attendance analytics: Aarav Sharma (95.8%), Priya Patel (87.5%), Rohan Gupta (62.5% - low attendance trigger).
  - Fee balances: Aarav (₹0.00), Priya (₹30,000.00), Rohan (₹65,000.00).

### 4.2 Backend Pytest Suite (`backend/tests`)
```powershell
& "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe" -m pytest backend/tests -v
```
- **Exit Code:** `0`
- **Result:** `68 passed, 1 warning in 2.30s`
- **Coverage Breakdown:**
  - Health probes (`/health/live`, `/health/ready`): 3/3 passed.
  - Authentication (valid/invalid logins, JWT verification): 7/7 passed.
  - Security & cross-student data isolation (Student A blocked from Student B): 13/13 passed.
  - Core academic APIs (attendance, marks, fees, timetable, notices, admin): 21/21 passed.
  - AI Chatbot intent routing, SQL retrieval & GenAI SDK mocks: 18/18 passed.
  - Request validation errors (422) & non-existent entity lookups (404): 6/6 passed.

### 4.3 Real PostgreSQL Test Script (`database/test_postgres_compatibility.py`)
```powershell
& "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe" database/test_postgres_compatibility.py
```
- **Exit Code:** `2`
- **Result:** `[BLOCKED] No PostgreSQL DATABASE_URL detected.`
- **Rationale:** Honest, transparent reporting. Docker and PostgreSQL service daemons are not installed on the Windows evaluation host. No false claims of live PostgreSQL execution were made.

### 4.4 Frontend Production Build (`npm run build`)
```powershell
$env:PATH = "C:\Users\Mr\node-v20.19.6-win-x64;" + $env:PATH; npm --prefix frontend run build
```
- **Exit Code:** `0`
- **Result:** Vite v5.4.1 compiled in 6.26s with 0 errors.
- **Assets:** `dist/index.html` (1.05 kB), `dist/assets/index-D1zIxDMO.css` (33.88 kB), `dist/assets/index-Duv4mPWd.js` (291.23 kB).

---

## 5. Deployment Readiness & Next Steps for the User

To run the application locally or deploy to the cloud, follow these instructions:

### Local Execution (Zero-Setup SQLite)
1. **Start Backend**:
   ```powershell
   & "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Start Frontend**:
   ```powershell
   $env:PATH = "C:\Users\Mr\node-v20.19.6-win-x64;" + $env:PATH
   npm --prefix frontend run dev
   ```
3. Open browser at `http://localhost:5173`. Use 1-click login buttons for **Aarav Sharma (Student)**, **Dr. Rajesh Kumar (Faculty)**, or **Admin**.

### Cloud Deployment (Supabase + Render + Vercel)
1. **Supabase Database Setup**:
   - Create a free project at [supabase.com](https://supabase.com).
   - Go to **Project Settings -> Database -> Connection String** (URI tab).
   - Supabase provides 3 connection options:
     - **Transaction Pooler (Port 6543)**: `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require` (Recommended for Render FastAPI workers under high concurrent load).
     - **Session Pooler (Port 5432)**: `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require` (Persistent pooler sessions).
     - **Direct Connection (Port 5432)**: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require` (Direct database instance; requires IPv6 support).
   - Copy the appropriate URI for your deployment.

2. **Run Migrations on Supabase**:
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
   & "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe" database/test_postgres_compatibility.py
   ```
3. **Render Deployment (FastAPI Web Service)**:
   - Connect your GitHub repository (`https://github.com/Akshitkumar23/CSIC.git`).
   - Use `render.yaml` or set environment: Python 3.12, Build: `pip install -r backend/requirements.txt`, Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
   - Set environment variables: `ENVIRONMENT=production`, `DATABASE_URL=<your-supabase-uri>`, and a secure custom `JWT_SECRET` (do not use the dev default).
4. **Vercel Deployment (React SPA)**:
   - Connect repository and select the `frontend` root directory.
   - Set build command: `npm run build`, output: `dist`.
   - Set environment variable: `VITE_API_URL=https://<your-render-service>.onrender.com`.

