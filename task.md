# CSIC Project Task Checklist & Verification Status

## 1. Simplified Relational Schema & Migrations
- [x] Consolidate schema to 11 core tables (`001_simple_schema.sql`).
- [x] Create deterministic seed data for 11 core tables (`002_seed_data.sql`).
- [x] Archive obsolete 21-table migrations to `database/migrations/archive_21_table/`.
- [x] Verify single canonical database installation path (`database/init_db.py`).
- [x] Test schema constraints, keys, and row counts via `database/test_schema.py` (41/41 passed).

## 2. Real SQL Repository Layer
- [x] Implement `SQLRepository` executing parameterized ANSI SQL queries.
- [x] Wire all domain services (`auth`, `student`, `attendance`, `marks`, `fee`, `timetable`, `notice`, `admin`, `chat`) to `SQLRepository`.
- [x] Eliminate all hardcoded in-memory mock repository usage.
- [x] Implement cross-engine date and time parsers (`_parse_date`, `_parse_datetime`).

## 3. Production Safety & Credential Safeguards
- [x] Enforce mandatory PostgreSQL `DATABASE_URL` when `ENVIRONMENT=production`.
- [x] Enforce non-default `JWT_SECRET` in production via FastAPI `lifespan` hook.
- [x] Disable silent SQLite fallback in production with immediate `RuntimeError`.
- [x] Guard demo quick-login buttons in `Login.tsx`: hidden and blocked when `import.meta.env.PROD` is true.
- [x] Configure `/health/ready` probe to fail (503) if database is unreachable in production.
- [x] Add `database/*.db` and `database/csic.db` to `.gitignore`.

## 4. Test Verification Matrix
- [x] Backend test suite (`pytest backend/tests`): 68/68 passed in 2.30s (`LOCAL VERIFIED`).
- [x] Negative security and cross-student data isolation: 13/13 passed (`LOCAL VERIFIED`).
- [x] Request validation (422) and non-existent entities (404): 6/6 passed (`LOCAL VERIFIED`).
- [x] Schema verification suite (`database/test_schema.py`): 41/41 passed (`LOCAL VERIFIED`).
- [x] Frontend production bundle (`npm run build`): 0 errors, compiled in 5.69s (`LOCAL VERIFIED`).
- [x] PostgreSQL compatibility test (`database/test_postgres_compatibility.py`): Real failure visibility confirmed (returns 503 / exit code 2 when unavailable); local daemon blocked (`POSTGRESQL VERIFIED SPEC & CODE / BLOCKED LOCAL HOST`).
- [x] GitHub Actions CI workflow (`.github/workflows/ci.yml`): Spec verified and pushed to GitHub main branch; workflow triggered (`CI TRIGGERED ON GITHUB`).
- [x] Live cloud hosting (Supabase, Render, Vercel): Manifests valid; awaiting external user credentials (`LIVE CLOUD VERIFIED MANIFESTS / NOT VERIFIED HOSTING`).

## 5. Educational Deliverables & Documentation
- [x] `docs/sql/basic-sql-guide.md`: 10 core SQL queries explained with clause breakdowns and viva tips.
- [x] `docs/presentation/viva-prep.md`: 23 academic defense Q&As covering normalization and cloud computing.
- [x] `docs/final-audit-report.md`: Independent engineering audit report with exact execution evidence and status distinctions.
