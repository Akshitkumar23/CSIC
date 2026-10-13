# Living Implementation Task Checklist

This checklist tracks the implementation progress, verification evidence, and status across all phases of the Cloud-Based Student Information Chatbot project.

## Legend
- `[ ]` Pending
- `[-]` In Progress
- `[x]` Completed & Verified

---

## Phase 0: Research, Specification & Repository Audit
- [x] Initial repository audit (empty directory detected; Python 3.12, Node v20, Git available on workstation).
- [x] Official documentation research (PostgreSQL, Supabase RLS, Render, Vercel, Gemini GenAI).
- [x] Create Architecture Decision Log (`docs/architecture/decision-log.md`).
- [x] Create Research Sources Log (`docs/architecture/research-sources.md`).
- [x] Create System Design Specification (`docs/architecture/system-design.md`).
- [x] Create Database Design Specification (`docs/architecture/database-design.md`).
- [x] Create Cloud Deployment Guide (`docs/architecture/cloud-deployment.md`).
- [x] Create Implementation Plan (`docs/implementation/implementation-plan.md`).
- [x] Create Living Checklist (`docs/implementation/task.md`).

---

## Phase 1: Project Foundation & Baseline Tooling
- [x] Initialize Git repository with proper `.gitignore` (ignoring `.env`, `node_modules`, `__pycache__`, `dist`).
- [x] Set up Backend workspace structure (`backend/` with `requirements.txt`, FastAPI app, modular router layout).
- [x] Set up Frontend workspace structure (`frontend/` with Vite + React + TypeScript + Tailwind CSS).
- [x] Implement backend health probes (`/health/live` and `/health/ready`).
- [x] Implement backend configuration loader (`backend/app/core/config.py`) using Pydantic Settings.
- [x] Verify baseline builds and startup commands locally (pytest 46/46 passed and npm run build clean).

---

## Phase 2: PostgreSQL Engineering & Advanced SQL
- [x] Write sequential SQL migration files (`database/migrations/001_initial_schema.sql`).
- [x] Implement table definitions for all 21 core entities with explicit `CHECK`, `UNIQUE`, `NOT NULL`, and referential constraints.
- [x] Implement 10 required reporting database views (`v_student_attendance`, `v_low_attendance_warnings`, etc.).
- [x] Implement database indexes (composite indexes on session/attendance, marks, timetable, pgvector HNSW).
- [x] Create deterministic synthetic seed data (`database/migrations/003_seed_data.sql`) with realistic departments, students, faculty, attendance records, exam marks, fees, and timetable entries.
- [x] Create dedicated SQL concepts demonstration guide (`docs/sql/demonstrations.md`) covering Joins, CTEs, Window functions, Aggregations, Transactions, and Query Plans.
- [x] Write automated database tests (`database/test_schema.py`) verifying schema constraints, views calculation, and query accuracy (90/90 tests passed).

---

## Phase 3: Authentication & Database Row-Level Security (RLS)
- [-] Create RLS security migration (`migrations/004_rls_policies.sql`) enabling RLS on all sensitive tables.
- [x] Implement policies for Student role: access only own profile, attendance, marks, invoices, timetable, and chats.
- [x] Implement policies for Faculty role: access only assigned courses, class sessions, and student marks entry.
- [x] Implement policies for Admin role: full administrative privileges.
- [x] Implement backend JWT authentication dependency with role extraction (`backend/app/core/security.py`).
- [x] Write negative security test suite verifying denied cross-student access (Student A cannot read Student B records: 403 Forbidden) and blocked privilege escalation (`backend/tests/test_security.py`).

---

## Phase 4: Student Portal & Admin Dashboard
- [x] Implement REST API endpoints:
  - `/api/v1/auth` (Login, profile info, logout)
  - `/api/v1/students` (Student profile, enrolled courses)
  - `/api/v1/attendance` (Attendance overview, subject-wise drill-down)
  - `/api/v1/marks` (Exam results, semester summaries)
  - `/api/v1/fees` (Invoices, payment history)
  - `/api/v1/timetable` (Weekly schedule, room allocations)
  - `/api/v1/notices` (Published announcements, categorized filters)
  - `/api/v1/admin` (Student management, notice publishing, timetable authoring)
- [x] Build Frontend UI:
  - Responsive Navigation & Role Switcher/Login screen (`frontend/src/pages/Login.tsx`)
  - Student Dashboard (Attendance cards, low attendance warnings, marks summary, timetable, fee status in `frontend/src/pages/StudentDashboard.tsx`)
  - Admin Dashboard (Student roster, notices manager, marks entry in `frontend/src/pages/AdminDashboard.tsx`)
  - Loading skeletons, accessible form controls, and error states.
  - Verified production asset bundling with `npm run build` (0 TypeScript errors).

---

## Phase 5: AI Chatbot & Document RAG Pipeline
- [x] Implement Chatbot Backend Router (`/api/v1/chat/message`).
- [x] Build Deterministic Structured Intent Classifier (routes questions about attendance, marks, fees, and timetables to authorized backend service queries).
- [x] Implement Document RAG Ingestion & Chunking pipeline (`backend/app/services/rag_service.py`).
- [x] Integrate Google GenAI SDK (`gemini-2.5-flash` and embedding model).
- [x] Implement safe prompt synthesis with strict untrusted context boundaries and source citations.
- [x] Implement graceful fallback and development mock mode when `GEMINI_API_KEY` is not provided.
- [x] Build conversational frontend Chatbot drawer with quick suggested prompts, markdown rendering, and source badges.
- [x] Write chatbot evaluation tests covering structured data queries and ungrounded questions.

---

## Phase 6: Cloud Deployment & CI/CD Configuration
- [x] Create `render.yaml` infrastructure specification for FastAPI backend deployment (verified Python 3.12, dynamic $PORT, /health/ready probe, zero-secret config).
- [x] Create `frontend/vercel.json` for client-side SPA routing (verified rewrite rule /(.*) -> /index.html and security headers).
- [x] Configure GitHub Actions workflow (`.github/workflows/ci.yml`) testing frontend builds, backend pytest, and linting.
- [x] Author comprehensive Academic Viva Guide (`docs/presentation/viva-prep.md`) and Live Demonstration Script (`docs/presentation/demo-script.md`).
- [x] Document exact deployment runbooks and environment configuration checklists.

---

## Phase 7: Verification, Viva Preparation & Final Deliverables
- [x] Run full automated test suites:
  - Database & Migrations: 90/90 tests passed (`database/test_schema.py`)
  - FastAPI Backend & Security & AI Chat: 62/62 tests passed (`pytest backend/tests`)
  - Frontend TypeScript & Production Bundler: 0 errors (`npm run build` -> `frontend/dist/`)
- [x] Conduct security audit and verify zero leaked credentials (git audited, `.env` gitignored, zero secrets in frontend code).
- [x] Create Academic Project Report & Presentation assets (`docs/presentation/demo-script.md`, `docs/presentation/viva-prep.md`).
- [x] Create SQL Viva Questions & Cloud Computing Viva Guide (`docs/presentation/viva-prep.md`).
- [x] Generate comprehensive final delivery summary.

---

## Phase 8: Independent Final Engineering Audit
- [x] Full project inspection & subagent claims verification.
- [x] Discrepancy analysis: verified 62 backend tests (46 initial + 16 chat/RAG tests) and 90 database schema tests.
- [x] Fixed 5 audit findings:
  1. Frontend auth fallback masking 401/403 errors in `frontend/src/services/api.ts`.
  2. SQL anti-pattern `SUM(DISTINCT fi.amount)` fixed in `database/migrations/002_reporting_views.sql`.
  3. GitHub Actions CI updated to `pgvector/pgvector:pg16` in `.github/workflows/ci.yml`.
  4. Simulation mode explicitly labeled `[Development Simulation Mode]` in `backend/app/services/ai/chatbot_service.py`.
  5. Login screen demo accounts synchronized with backend seed accounts in `frontend/src/pages/Login.tsx`.
- [x] Generated Independent Final Engineering Audit Report (`docs/final-audit-report.md`).
