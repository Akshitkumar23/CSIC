# Cloud-Based Student Information Chatbot (CSIC)

[![CSIC CI/CD Pipeline](https://github.com/Akshitkumar23/CSIC/actions/workflows/ci.yml/badge.svg)](https://github.com/Akshitkumar23/CSIC/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.1-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5.3-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql)](https://www.postgresql.org)

An institutional cloud-ready student information portal and intelligent conversational chatbot for colleges and universities. CSIC features a normalized 13-table relational SQL database architecture, OAuth2 role-based authorization, academic performance tracking, and a grounded AI assistant.

---

## 🏛️ System Architecture

- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons (Route-level code splitting)
- **Backend:** FastAPI, Python 3.12, OAuth2 Bearer JWT Authentication, Pydantic v2
- **Database:** Normalized 13-table relational SQL architecture (`users`, `courses`, `subjects`, `enrollments`, `attendance_records`, `examinations`, `marks`, `fee_records`, `timetable_entries`, `notices`, `chat_history`, `chat_sessions`, `chat_messages`)
  - **Local Development:** SQLite with foreign keys enforced (`database/csic.db`)
  - **Cloud Production:** PostgreSQL 16 (Supabase / Render) with connection pooling
- **AI Assistant:** Retrieval-Augmented Generation (RAG) with policy citations and deterministic routing to verified database queries
- **CI/CD & Cloud:** GitHub Actions, Vercel Multi-Service (`vercel.json`), Render Blueprint (`render.yaml`)

---

## 🚀 Key Features

1. **Student Dashboard (`/dashboard`):**
   - Real-time attendance ring with subject-wise drill-down and low-attendance warnings (< 75%).
   - Examination marks, semester results, and subject grades.
   - Institutional fee ledger with transparent demo settlement simulation.
   - Weekly timetable schedule and room allocations.
   - Categorized institutional circulars and notices.
   - Conversational AI assistant drawer for student queries.

2. **Faculty Portal (`/faculty`):**
   - At-risk attendance roster highlighting students below 75% threshold.
   - Enrolled student directory.
   - Campus circular broadcast tool.

3. **Administrator Control Panel (`/admin`):**
   - High-level academic metrics (total students, active circulars).
   - Student roster management and new student enrollment.
   - Campus notice publication and removal.

4. **Security & Boundary Isolation:**
   - Role-Based Access Control (`student`, `faculty`, `admin`).
   - Cross-student data isolation: Students cannot query or pay other students' invoices.
   - Production guards: Missing PostgreSQL `DATABASE_URL` or default `JWT_SECRET` halts startup in production mode.

---

## 📋 Institutional Demo Accounts

| Role | Name | Email | Password |
|---|---|---|---|
| **Student** | Rashi | `rashi@csic.edu` | `1234` |
| **Student** | Vanshika | `vanshika@csic.edu` | `1234` |
| **Student** | Silki | `silki@csic.edu` | `1234` |
| **Student** | Akshit | `akshit@csic.edu` | `1234` |
| **Faculty** | Akshit | `rajesh.kumar@csic.edu` | `1234` |
| **Faculty** | Prof. Anita Deshmukh | `anita.deshmukh@csic.edu` | `1234` |
| **Administrator** | Akshit | `admin@csic.edu` | `1234` |

---

## 🛠️ Quickstart & Local Setup

### Prerequisites
- Python 3.12+
- Node.js 20+

### Option A: One-Click Development Launcher (Windows)
Double-click `run_dev.bat` or run:
```powershell
.\run_dev.ps1
```
This initializes the local database, launches the FastAPI backend at `http://localhost:8000`, and starts the Vite frontend at `http://localhost:5173`.

### Option B: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Akshitkumar23/CSIC.git
   cd CSIC
   ```

2. **Initialize Backend:**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate | Unix: source venv/bin/activate
   pip install -r backend/requirements.txt
   python database/init_db.py
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Initialize Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application:**
   - Web App: `http://localhost:5173`
   - Interactive API Docs (Swagger): `http://localhost:8000/docs`

---

## 🧪 Verification & Test Suite

Run the full automated test suite locally:

```bash
# 1. Backend API, Security & AI tests (95 tests)
python -m pytest backend/tests -v

# 2. Database schema, constraints & analytical queries (50 tests)
python database/test_schema.py

# 3. Frontend production compilation & TypeScript checks
cd frontend && npm run build
```

---

## 📁 Repository Structure

```text
CSIC/
├── .github/workflows/ci.yml       # GitHub Actions CI workflow (PostgreSQL 16, Python 3.12, Node 20)
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── api/v1/                # Modular REST API endpoints (auth, students, attendance, marks, fees, etc.)
│   │   ├── core/                  # Configuration & security (JWT, RBAC)
│   │   ├── models/                # Pydantic v2 schemas
│   │   ├── repositories/          # ANSI SQL parameterized repository layer
│   │   ├── services/              # Domain services & AI RAG pipeline
│   │   └── main.py                # Application entrypoint & lifespan hooks
│   ├── requirements.txt           # Pinned backend dependencies
│   └── tests/                     # Comprehensive Pytest suite (95 tests)
├── database/                      # SQL schema & migrations
│   ├── migrations/                # Canonical 13-table schema and deterministic seed scripts
│   ├── init_db.py                 # Single database initialization script
│   ├── test_schema.py             # Schema integrity and constraint test suite
│   └── test_postgres_compatibility.py # PostgreSQL real-database verification
├── docs/                          # Architecture, presentation & viva documentation
│   ├── architecture/              # System, database, and cloud architecture specifications
│   ├── presentation/              # Viva defense prep & 5-minute live demo script
│   ├── sql/                       # SQL demonstration guides & query breakdowns
│   └── CSIC_PROJECT_AUDIT.md      # Comprehensive technical audit & system status report
├── frontend/                      # React 18 + TypeScript + Vite SPA
│   ├── src/
│   │   ├── components/            # UI components (AttendanceCard, FeeSummaryCard, etc.)
│   │   ├── pages/                 # Role-based pages (StudentDashboard, FacultyDashboard, AdminDashboard, Login)
│   │   ├── services/              # API client and authentication token management
│   │   └── types/                 # TypeScript interfaces
│   ├── package.json
│   ├── vercel.json                # Frontend legacy fallback routing
│   └── vite.config.ts
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── render.yaml                    # Render cloud deployment blueprint
├── run_dev.bat                    # Windows development launcher
├── run_dev.ps1                    # PowerShell development launcher
├── vercel.json                    # Canonical root Vercel multi-service routing
└── README.md                      # Project documentation
```

---

## 📄 License

Educational open-source project developed for the Cloud-Based Student Information Chatbot (CSIC) capstone presentation.
