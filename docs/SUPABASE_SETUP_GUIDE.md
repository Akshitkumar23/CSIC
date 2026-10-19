# CSIC — Supabase Cloud Database Setup & Migration Guide
**Document Version:** 1.0.0  
**Target Environment:** Supabase Cloud PostgreSQL 16+  
**Target Host / Consumer:** Render Web Service (`csic-backend` / FastAPI)  
**Branch:** `feature/chatbot-first-redesign`  
**Security Classification:** Public / Zero-Secret (Production credentials omitted)  

---

## 1. Executive Summary & Audit Scorecard

This guide provides an independent, verified technical assessment and step-by-step procedure for connecting the **Cloud-Based Student Information Chatbot (CSIC)** backend to **Supabase Cloud PostgreSQL**.

### System Architecture Summary
- **Frontend:** Vercel (React 18 + TypeScript + Vite Single Page Application).
- **Backend:** Render Web Service (FastAPI + Python 3.12 + Uvicorn).
- **Database:** Supabase Cloud PostgreSQL 16+ (Managed DBaaS).
- **AI / NLP:** Deterministic local NLP pipeline (TF-IDF + Logistic Regression); **Zero Ollama, Zero external LLM runtime dependency**.
- **Database Connectivity:** Direct DB-driver via `psycopg2-binary` using parameterized ANSI SQL.

### Audit Scorecard

| Area | Status | Verification Summary |
| :--- | :---: | :--- |
| **Active Schema Portability** | **PASS** | `001_simple_schema.sql` (11 tables) and `003_chat_sessions.sql` (2 tables) use pure ANSI SQL compatible with PostgreSQL 16+ and SQLite 3+. All 13 tables compile without errors. |
| **Seed Data Portability** | **PASS** | `002_seed_data.sql` utilizes standard PostgreSQL `ON CONFLICT (id) DO NOTHING` syntax. All foreign keys and check constraints resolve deterministically. |
| **Archived 21-Table Schema Isolation** | **PASS** | Files under `database/migrations/archive_21_table/` are strictly educational/historical artifacts. The backend codebase has zero dependencies on them. **THEY MUST NOT BE RUN ON SUPABASE.** |
| **Connection Pooling Compatibility** | **PASS** | `SQLRepository` uses short-lived, autocommit connections (`conn.autocommit = True; conn.close()`), making it 100% compatible with Supavisor Transaction Pooler on Port `6543`. |
| **IPv4 Cloud Network Routing** | **PASS** | Supavisor Pooler (`pooler.supabase.com`) provides dual-stack IPv4/IPv6 support required by Render's outbound networking. Supabase direct connections (`db.[ref].supabase.co`) are IPv6-only on the free tier and will time out on Render. |
| **Auth Architecture Alignment** | **PASS** | FastAPI executes self-contained stateless JWT authentication (`python-jose`, bcrypt, `HS256`). Supabase is used strictly as a managed PostgreSQL relational store; Supabase GoTrue Auth is decoupled. |
| **Student Multi-Tenancy Boundary** | **PASS** | Application-level authorization (`verify_student_access()`) strictly isolates student attendance, marks, fees, and chat turns. 13 automated security tests pass (`backend/tests/test_security.py`). |
| **Production Startup Gatekeeper** | **PASS** | `Settings.check_production_safety()` in `backend/app/core/config.py` enforces valid PostgreSQL `DATABASE_URL` and a non-default `JWT_SECRET` before the Uvicorn server will boot in `production` mode. |
| **Secret Zero-Exposure Compliance** | **PASS** | Zero passwords, API keys, service-role keys, or JWT secrets are stored in Git. All production secrets are configured through Render and Supabase environment variables. |

---

## 2. Migration Audit & Schema Analysis

### 2.1 Active Schema (What Goes to Supabase)
The CSIC production backend communicates exclusively with the **13-table simplified schema**:

```
Active Migrations (database/migrations/):
├── 001_simple_schema.sql       -> 11 core tables + 8 performance indexes
├── 003_chat_sessions.sql       -> 2 multi-session chat tables + 2 indexes
└── 002_seed_data.sql           -> Deterministic seed records (6 users, 3 enrollments, 72 attendance records)
```

#### Detailed Table Inventory (13 Tables)
1. `users` (Identity: students, faculty, admin; bcrypt password hashes).
2. `courses` (Degree programs and departments).
3. `subjects` (Curriculum subjects, credits, semester, faculty assignments).
4. `enrollments` (Student registrations, roll numbers, semesters, sections).
5. `attendance_records` (Session-by-session records: present, absent, excused).
6. `examinations` (Mid-term and end-term assessment definitions).
7. `marks` (Student scores, grades, absence tracking).
8. `fee_records` (Invoices, fee amounts, amounts paid, payment statuses).
9. `timetable_entries` (Weekly lecture slots, rooms, start/end times).
10. `notices` (Official circulars, categories, target roles).
11. `chat_history` (Legacy conversational audit log).
12. `chat_sessions` (Conversational threads per student).
13. `chat_messages` (Turn-by-turn messages, query types, verified facts, sources).

#### Critical Audit Finding on `database/init_db.py`
In `database/init_db.py`, the `init_postgres` function was previously written as:
```python
# Lines 71-79 of database/init_db.py
with open(SCHEMA_FILE, "r") as f:
    cursor.execute(f.read())  # 001_simple_schema.sql
with open(SEED_FILE, "r") as f:
    cursor.execute(f.read())  # 002_seed_data.sql
```
Notice that `init_postgres` omitted `003_chat_sessions.sql`! If someone were to run only 001 and 002, the chatbot multi-session features (`chat_sessions`, `chat_messages`) would be missing, causing runtime SQL errors whenever a user opens the chat drawer.  
**Resolution:** Migration `003_chat_sessions.sql` **MUST** be executed immediately after `001_simple_schema.sql` on Supabase.

---

### 2.2 Archived Schema: DO NOT RUN ON SUPABASE

Located in `database/migrations/archive_21_table/`:
- `001_initial_schema.sql` (21 tables: `profiles`, `departments`, `programs`, `fee_invoices`, `documents`, etc.)
- `002_reporting_views.sql` (10 SQL views: `v_student_attendance`, `v_low_attendance_warnings`, etc.)
- `003_seed_data.sql` (Synthetic data using UUIDs)
- `004_rls_policies.sql` (Row-Level Security policies referencing `auth.users` and `profiles`)

```
================================================================================
                    CRITICAL WARNING: DO NOT EXECUTE
            DO NOT RUN ANY SCRIPT IN database/migrations/archive_21_table/
================================================================================
```

#### Why the Archived Files Must NOT Be Run:
1. **Schema Mismatch:** The active backend code (`backend/app/repositories/sql_repository.py`) has been written against the 13-table schema using deterministic string identifiers (e.g., `stu-001`, `crs-01`, `sub-01`, `enr-001`). The archived schema uses PostgreSQL `gen_random_uuid()` UUID types throughout.
2. **Table Collision & Split Entities:** The archived schema splits user identity between Supabase's `auth.users` and a separate `profiles` table, and splits fees into `fee_invoices` and `fee_payments`. The active backend queries `users` and `fee_records` directly.
3. **Foreign Key Collisions:** Running `archive_21_table/001_initial_schema.sql` creates a mock `auth.users` table inside Supabase's managed `auth` schema, which violates Supabase's managed database ownership and causes fatal DDL conflicts.
4. **RLS Policy Incompatibility:** `004_rls_policies.sql` enables RLS on tables (`profiles`, `fee_invoices`) that do not exist in the 13-table schema. Running it will result in `ERROR: relation "profiles" does not exist`.
5. **No Views Used in Backend:** A code search across `backend/` confirms that zero queries reference `v_*` SQL views. All business logic aggregations (e.g. attendance percentage, GPA, fee balance) are computed either via parameterized SQL aggregations or in Python domain services.

---

## 3. Exact Supabase Migration Execution Order

Follow this exact sequence in the **Supabase Dashboard SQL Editor**:

```mermaid
flowchart TD
    Step1["Step 1: Execute 001_simple_schema.sql<br/>(Creates 11 Core Tables + 8 Indexes)"] --> Step2["Step 2: Execute 003_chat_sessions.sql<br/>(Creates 2 Multi-Session Chat Tables + 2 Indexes)"]
    Step2 --> Step3["Step 3: Execute 002_seed_data.sql<br/>(Populates Users, Courses, Attendance, Marks, Fees, Timetable)"]
    Step3 --> Step4["Step 4: Execute Verification SQL<br/>(Assert 13 Tables and Expected Row Counts)"]
```

### Execution Steps in Supabase SQL Editor:

#### Step 1: Core Relational Schema
- Open Supabase Dashboard $\to$ **SQL Editor** $\to$ **New query**.
- Paste the full contents of `database/migrations/001_simple_schema.sql`.
- Click **Run**.
- Expected Result: `Success. No rows returned.` (11 tables and 8 indexes created).

#### Step 2: Multi-Session Chat Schema
- In SQL Editor $\to$ **New query**.
- Paste the full contents of `database/migrations/003_chat_sessions.sql`.
- Click **Run**.
- Expected Result: `Success. No rows returned.` (2 tables and 2 indexes created).

#### Step 3: Deterministic Seed Data
- In SQL Editor $\to$ **New query**.
- Paste the full contents of `database/migrations/002_seed_data.sql`.
- Click **Run**.
- Expected Result: `Success. No rows returned.` (Rows inserted with `ON CONFLICT (id) DO NOTHING`).

#### Step 4: Verification Queries
Run the following verification script in the SQL Editor to confirm table creation and row counts:

```sql
-- ==============================================================================
-- CSIC Schema & Seed Verification Query
-- ==============================================================================

-- 1. Verify all 13 core tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 2. Verify row counts across all 13 tables
SELECT 
    (SELECT COUNT(*) FROM users) AS users_count,
    (SELECT COUNT(*) FROM courses) AS courses_count,
    (SELECT COUNT(*) FROM subjects) AS subjects_count,
    (SELECT COUNT(*) FROM enrollments) AS enrollments_count,
    (SELECT COUNT(*) FROM attendance_records) AS attendance_count,
    (SELECT COUNT(*) FROM examinations) AS examinations_count,
    (SELECT COUNT(*) FROM marks) AS marks_count,
    (SELECT COUNT(*) FROM fee_records) AS fee_records_count,
    (SELECT COUNT(*) FROM timetable_entries) AS timetable_count,
    (SELECT COUNT(*) FROM notices) AS notices_count,
    (SELECT COUNT(*) FROM chat_history) AS chat_history_count,
    (SELECT COUNT(*) FROM chat_sessions) AS chat_sessions_count,
    (SELECT COUNT(*) FROM chat_messages) AS chat_messages_count;
```

#### Expected Verification Output:
```
users_count          : 6
courses_count        : 1
subjects_count       : 4
enrollments_count    : 3
attendance_count     : 72
examinations_count   : 4
marks_count          : 12
fee_records_count    : 4
timetable_count      : 11
notices_count        : 4
chat_history_count   : 2
chat_sessions_count  : 0
chat_messages_count  : 0
```

---

## 4. Supabase Connection Architecture Analysis (Render vs. Supabase)

Connecting a PaaS web service (Render) to a Cloud Database (Supabase) requires careful attention to **network protocol (IPv4 vs. IPv6)** and **connection pooler modes**.

```mermaid
flowchart LR
    subgraph Render["Render Cloud (IPv4 Outbound)"]
        FastAPI["FastAPI Web Service<br/>(psycopg2-binary)"]
    end

    subgraph Supabase["Supabase Cloud"]
        Pooler["Supavisor Connection Pooler<br/>aws-0-[region].pooler.supabase.com<br/>Port 6543 (Transaction Mode)"]
        Direct["Direct DB Connection<br/>db.[project-ref].supabase.co<br/>Port 5432 (IPv6 Only)"]
        Postgres[("PostgreSQL 16 Engine")]
        
        Pooler -->|IPv4 / Dual-Stack| Postgres
        Direct -.->|IPv6 Only| Postgres
    end

    FastAPI -->|RECOMMENDED: Port 6543<br/>IPv4 Compatible| Pooler
    FastAPI -.->|DO NOT USE ON RENDER<br/>Times out / Network unreachable| Direct
```

### 4.1 Connection Type Comparison

| Parameter | Direct Connection | Supavisor Session Pooler | Supavisor Transaction Pooler (RECOMMENDED) |
| :--- | :--- | :--- | :--- |
| **Hostname** | `db.[PROJECT_REF].supabase.co` | `aws-0-[REGION].pooler.supabase.com` | `aws-0-[REGION].pooler.supabase.com` |
| **Port** | `5432` | `5432` | `6543` |
| **Username** | `postgres` | `postgres.[PROJECT_REF]` | `postgres.[PROJECT_REF]` |
| **Network IP** | **IPv6 Only** (Free Tier) | **IPv4 & IPv6 Dual-Stack** | **IPv4 & IPv6 Dual-Stack** |
| **Render Compatibility** | ❌ **INCOMPATIBLE** (Render outbound network cannot route IPv6 to external hosts) | ⚠️ Compatible, but holds dedicated backend slots |  **OPTIMAL** (Native IPv4 support) |
| **Max Connections** | ~60 on free tier | ~60 backend connections | Up to thousands of client connections |
| **CSIC Suitability** | High latency; prone to connection drops | Good for long sessions | **Ideal** for `SQLRepository` short-lived, autocommit queries |

### 4.2 Why Port 6543 (Transaction Pooler) is Mandatory for Render
1. **IPv6 Incompatibility:** Render's free and standard web service containers communicate with external hosts over IPv4. Supabase free-tier direct connections on `db.[PROJECT_REF].supabase.co` do not have public IPv4 addresses. Attempting to connect directly from Render causes:
   ```
   psycopg2.OperationalError: could not translate host name "db.[ref].supabase.co" to address
   or
   psycopg2.OperationalError: Connection timed out
   ```
   Supavisor pooler endpoints (`aws-0-[region].pooler.supabase.com`) resolve to public IPv4 addresses, avoiding this failure.
2. **Connection Lifecycle in CSIC:** In `backend/app/repositories/sql_repository.py`:
   - Every query calls `_get_connection()`, sets `conn.autocommit = True`, executes the parameterized SQL statement, and immediately runs `conn.close()` in a `finally:` block.
   - Transaction Mode (Port `6543`) holds a PostgreSQL backend worker only for the duration of each individual transaction, releasing it back to the pool instantly. This allows the backend to handle high traffic without exhausting Supabase's database connection limit.
3. **Required SSL Parameter:** Supabase PostgreSQL requires SSL encryption across all public connections. The connection string must include `?sslmode=require`.

### 4.3 Recommended Connection String Format
```
postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
```
> [!IMPORTANT]
> The username is `postgres.[PROJECT_REF]` (with your project reference appended), **NOT** just `postgres`. Supavisor requires this tenant prefix to route your queries to the appropriate database.

---

## 5. Authentication & Multi-Tenancy Architecture

### 5.1 FastAPI Custom JWT vs. Supabase Auth
- **Design Decision:** CSIC intentionally uses **self-contained stateless JWT authentication** managed directly by the FastAPI backend (`backend/app/core/security.py`).
- **Why Supabase Auth (GoTrue) is Not Used:**
  - Decouples the application logic from vendor-specific auth libraries.
  - Allows full student, faculty, and administrator role handling with standard HTTP Bearer tokens.
  - Keeps user authentication and data operations entirely within standard ANSI SQL.
  - Zero proprietary client libraries required; compatible with standard frontend HTTP clients.
- **Password Security:** User passwords are encrypted with `bcrypt` (work factor 12) via `passlib[bcrypt]` and stored in `users.password_hash`.
- **Token Signing:** Tokens are signed using `HS256` HMAC with a high-entropy `JWT_SECRET` configured via environment variables.

### 5.2 Multi-Tenant Data Isolation Enforcement
Data privacy between students is strictly maintained at the **application layer**:
1. **Identity Resolution:** FastAPI extracts and verifies the student's ID from the cryptographic JWT payload on every request:
   ```python
   # backend/app/core/security.py
   async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserProfile:
       # Validates HMAC-SHA256 signature, expiry, and returns authenticated UserProfile
   ```
2. **Access Control Boundary:** In `backend/app/api/v1/students.py`:
   ```python
   def verify_student_access(student_id: str, current_user: UserProfile) -> None:
       if current_user.role == "student" and current_user.id != student_id:
           raise HTTPException(
               status_code=403, 
               detail="Forbidden: You can only access your own student records."
           )
   ```
3. **Chatbot Context Isolation:** When a student queries the chatbot in `backend/app/api/v1/chat.py`, queries are executed against `sql_repo` using `current_user.id`. A student cannot query another student's attendance, marks, fees, or chat turns.
4. **Automated Verification:** The entire access-control matrix is validated by 13 dedicated automated tests in `backend/tests/test_security.py` (e.g., `test_student_cannot_access_other_student_attendance`, `test_student_cannot_access_other_student_fees`), all passing with 100% compliance.

---

## 6. Render Environment Variables Configuration

Configure these environment variables in the **Render Dashboard** (`Dashboard` $\to$ `csic-backend` $\to$ `Environment`):

### 6.1 Variable Reference (Names Only — Zero Secrets)

| Variable Name | Required? | Recommended Production Value | Description |
| :--- | :---: | :--- | :--- |
| `PYTHON_VERSION` | Yes | `3.12.0` | Python runtime version on Render. |
| `ENVIRONMENT` | Yes | `production` | Enforces production safety checks on startup. |
| `PORT` | Yes | `8000` | Render injects this automatically; defaults to 8000. |
| `DATABASE_URL` | Yes | `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require` | Supavisor Transaction Pooler connection URI. |
| `JWT_SECRET` | Yes | *(A random 64-character hex string)* | Secret key for JWT signature verification. **Must not be default.** |
| `JWT_ALGORITHM` | No | `HS256` | Cryptographic algorithm for JWT signatures. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token validity duration (1440 minutes = 24 hours). |
| `ALLOWED_ORIGINS` | Yes | `https://csic-portal.vercel.app,http://localhost:5173` | Comma-separated CORS allowed origins (your Vercel frontend URL). |
| `GEMINI_API_KEY` | Optional | *(Your Google Gemini API Key)* | Optional for external Gemini 2.5 Flash; local NLP runs without it. |

> [!CAUTION]
> **Production Safety Gate:** If `ENVIRONMENT=production` and `JWT_SECRET` is left as the default dev secret or `DATABASE_URL` does not start with `postgres`, the backend will raise a `RuntimeError` during the FastAPI startup lifespan and refuse to boot.

---

## 7. Connectivity & Health Check Verification

### 7.1 Verify Connection from Local Machine (Optional Pre-Deployment Test)
You can verify PostgreSQL connectivity before deploying to Render by running the built-in compatibility test:

```powershell
# Set the Supavisor Pooler URL in your local terminal
$env:DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"

# Run the automated PostgreSQL verification script
C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe database/test_postgres_compatibility.py
```

Expected output:
```
======================================================================
CSIC: Real PostgreSQL 16 Verification Suite
======================================================================
Connecting to PostgreSQL database: aws-0-[REGION].pooler.supabase.com:6543/postgres
 -> Connection established successfully.
 -> 001_simple_schema.sql applied cleanly to PostgreSQL.
 -> 002_seed_data.sql applied cleanly to PostgreSQL.

--- PostgreSQL Table Row Counts ---
  users                 :   6 rows
  courses               :   1 rows
  subjects              :   4 rows
  enrollments           :   3 rows
  attendance_records    :  72 rows
  examinations          :   4 rows
  marks                 :  12 rows
  fee_records           :   4 rows
  timetable_entries     :  11 rows
  notices               :   4 rows
  chat_history          :   2 rows

[PASS] PostgreSQL real database verification succeeded.
```

### 7.2 Cloud Health Probes on Render
Once deployed on Render, the backend provides two built-in health probes:

1. **Liveness Probe:** `GET /health/live`
   - Returns `200 OK` with `{"status": "alive", "service": "csic-backend"}`.
   - Verifies the process is running.
2. **Readiness Probe:** `GET /health/ready`
   - Executes `SELECT 1;` against Supabase PostgreSQL via `DATABASE_URL`.
   - Returns `200 OK` with `{"status": "ready", "database": "connected"}` when connected.
   - Returns `503 Service Unavailable` with `{"status": "degraded", "database": "unreachable"}` if the database cannot be reached.

---

## 8. AKSHIT: DO THESE NEXT

Here are your exact, immediate manual steps in the **Supabase Dashboard** and **Render Dashboard**:

### Step 1: Open Supabase SQL Editor
1. Log in to [Supabase](https://supabase.com/dashboard) and select your CSIC project.
2. Click on the **SQL Editor** tab on the left sidebar (icon with `>_`).
3. Click **New query**.

### Step 2: Run Migration 001 (Core Schema)
1. Open the file `database/migrations/001_simple_schema.sql` on your machine.
2. Copy its entire contents and paste into the Supabase SQL Editor.
3. Click **Run** (or press `Ctrl+Enter`).
4. Confirm that the result panel displays `Success. No rows returned.`

### Step 3: Run Migration 003 (Chat Sessions Schema)
1. In the Supabase SQL Editor, click **New query**.
2. Open the file `database/migrations/003_chat_sessions.sql`.
3. Copy its entire contents and paste into the editor.
4. Click **Run**.
5. Confirm that the result panel displays `Success. No rows returned.`

### Step 4: Run Migration 002 (Seed Data)
1. In the Supabase SQL Editor, click **New query**.
2. Open the file `database/migrations/002_seed_data.sql`.
3. Copy its entire contents and paste into the editor.
4. Click **Run**.
5. Confirm that the result panel displays `Success. No rows returned.`

### Step 5: Run Verification Query
1. In the Supabase SQL Editor, open a **New query**.
2. Paste and run this quick validation script:
   ```sql
   SELECT 
       (SELECT COUNT(*) FROM users) AS users,
       (SELECT COUNT(*) FROM attendance_records) AS attendance,
       (SELECT COUNT(*) FROM marks) AS marks,
       (SELECT COUNT(*) FROM fee_records) AS fees,
       (SELECT COUNT(*) FROM timetable_entries) AS timetable,
       (SELECT COUNT(*) FROM notices) AS notices;
   ```
3. Verify that the output returns:
   - `users`: **6**
   - `attendance`: **72**
   - `marks`: **12**
   - `fees`: **4**
   - `timetable`: **11**
   - `notices`: **4**

### Step 6: Copy Supavisor Pooler Connection String
1. Go to **Project Settings** (gear icon at the bottom of the left sidebar).
2. Click **Database** under Configuration.
3. Scroll down to the **Connection string** section.
4. Select the **URI** tab.
5. In the dropdown, switch from **Direct connection** to **Transaction pooler** (Port `6543`).
6. Copy the connection URI:
   ```
   postgresql://postgres.[YOUR_PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[YOUR_REGION].pooler.supabase.com:6543/postgres?sslmode=require
   ```
7. Replace `[YOUR_PASSWORD]` with your actual Supabase database password.

### Step 7: Configure Render Environment Variables
1. Go to your [Render Dashboard](https://dashboard.render.com).
2. Select your `csic-backend` Web Service.
3. Click **Environment** in the left menu.
4. Set the following variables:
   - `ENVIRONMENT`: `production`
   - `PYTHON_VERSION`: `3.12.0`
   - `DATABASE_URL`: *(Paste the Supavisor Pooler URI from Step 6)*
   - `JWT_SECRET`: *(Generate a random 32+ character secret, e.g. using `python -c "import secrets; print(secrets.token_hex(32))"`)*
   - `ALLOWED_ORIGINS`: `https://csic-portal.vercel.app,http://localhost:5173`
5. Click **Save Changes**.
6. Render will automatically deploy a new build with the Supabase connection configured.

### Step 8: Verify Deployment Readiness
Once Render finishes deploying:
1. Visit `https://<YOUR_RENDER_APP_URL>/health/ready` in your browser.
2. Confirm the response:
   ```json
   {
     "status": "ready",
     "database": "connected",
     "service": "csic-backend"
   }
   ```
3. Your CSIC backend is now fully live on PostgreSQL in Supabase!
