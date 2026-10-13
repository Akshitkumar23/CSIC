# Architecture Decision Log (ADR)

## ADR-001: Architecture Style — Modular Monolith over Microservices
- **Status:** Accepted
- **Context:** The project is a final-year BTech CSE capstone and cloud computing training deliverable. It requires demonstrating practical cloud architecture, advanced SQL, secure auth, robust APIs, and an AI chatbot.
- **Decision:** Use a single cohesive repository containing a clean **Modular Monolith** backend (`backend/`) and modern Single Page Application frontend (`frontend/`).
- **Rationale:** Microservices introduce distributed transaction complexity, network latency, multiple container deployments, and deployment overhead that detract from core relational database engineering and clean cloud operations. A modular monolith allows strict separation of concerns (Routers -> Services -> Repositories -> Database) while preserving single-database ACID guarantees and simplified CI/CD.

## ADR-002: Technology Stack Selection
- **Status:** Accepted
- **Frontend:** React 18+ with TypeScript, Vite, Tailwind CSS, Lucide React icons, and React Router v6. Provides instantaneous build times, strict typing, responsive accessible UI, and seamless Vercel deployment.
- **Backend:** Python 3.12 with FastAPI, Pydantic v2, and asyncpg/psycopg database client. Asynchronous I/O handles concurrent student traffic efficiently with automated OpenAPI documentation (`/docs`).
- **Database:** PostgreSQL 16+ hosted on Supabase with native Row-Level Security (RLS) and Auth engine.
- **Cloud Infrastructure:** Vercel (Frontend static edge), Render (FastAPI web service), Supabase (Managed Postgres & Auth), and GitHub Actions (Automated CI/CD).

## ADR-003: Database Access & Multi-Tenant Authorization Model
- **Status:** Accepted
- **Context:** Students must only access their own private records (attendance, marks, invoices, chats). Faculty must access only assigned courses/sessions. Admins have broad academic management authority.
- **Decision:** Implement defense-in-depth authorization:
  1. **Application Layer (FastAPI):** Every incoming request is authenticated by verifying the Supabase Auth JWT and extracting `user_id` and role claims. Endpoints validate ownership before dispatching queries.
  2. **Database Layer (PostgreSQL RLS):** All tables have Row-Level Security enabled (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY;`). Policies reference `auth.uid()` and an authorized roles mapping function `app.current_user_role()`.
  3. **Privileged Backend Connection:** When the backend connects using a service or pooling connection, it executes `SET LOCAL request.jwt.claim.sub = :user_id; SET LOCAL request.jwt.claim.role = :role;` within transactions to ensure PostgreSQL RLS rules are actively evaluated.

## ADR-004: Dual-Source Chatbot Architecture (Deterministic SQL vs. Semantic RAG)
- **Status:** Accepted
- **Context:** An AI chatbot must answer both quantitative student inquiries ("What is my attendance in Operating Systems?") and unstructured institutional questions ("What is the college attendance policy for medical leave?").
- **Decision:** Strictly decouple into two independent data retrieval pipelines:
  - **Pipeline 1 — Deterministic Authorized Student Queries:** Natural language intent is classified into structured parametric API calls (e.g., `get_student_attendance(student_id, semester)`). The query runs against tested, verified SQL database views. The LLM is NEVER permitted to generate or execute raw SQL queries against production student tables.
  - **Pipeline 2 — College Document RAG:** Unstructured policies, syllabi, and circulars are parsed, chunked, embedded, and retrieved via cosine similarity search. The retrieved text is passed as untrusted context with citations.
- **Fallback / Safety Rule:** If evidence is missing or query intent cannot be authenticated, the system returns an explicit failure message rather than generating ungrounded facts.

## ADR-005: Database Migration & Schema Versioning Strategy
- **Status:** Accepted
- **Context:** All database objects (tables, constraints, views, indexes, RLS policies, seed data) must be reproducible across local development, CI test runners, and production Supabase instances.
- **Decision:** Schema changes will be written as numbered SQL migration scripts in `supabase/migrations/` (or `database/migrations/`). Migrations will be executed deterministically in alphabetical/chronological order. Raw ad-hoc dashboard SQL is strictly prohibited.

## ADR-006: SQL Simplification & Pragmatic Scope (Basic-to-Intermediate Relational SQL)
- **Status:** Accepted
- **Context:** The project aims to demonstrate practical cloud computing and basic-to-intermediate SQL suitable for undergraduate CSE capstones. Unnecessarily complex SQL abstractions (such as multi-stage CTE pipelines, window functions, and dynamic triggers) obscure core business logic without improving runtime correctness or security.
- **Decision:** Restrict core runtime queries and reporting views strictly to readable, robust Basic-to-Intermediate ANSI SQL constructs:
  - Standard multi-table `INNER JOIN` and `LEFT JOIN`.
  - Core aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`) paired with `GROUP BY` and `HAVING`.
  - Conditional aggregations using `COUNT(CASE WHEN ... THEN 1 END)` with `NULLIF(..., 0)` to guarantee zero-division safety.
  - Reusable reporting views for clean API decoupling.
  - Basic composite indexes justified directly by query filter patterns.
- **Preserved Invariants:** The complete 21-table 3NF normalized schema, primary/foreign key cascading constraints, check constraints, and Row-Level Security policies are strictly maintained without any weakening of data integrity.
