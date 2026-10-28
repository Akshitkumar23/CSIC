<div align="center">

# 🎓 CSIC — Cloud Student Information Chatbot

**An institutional student information portal powered by a grounded conversational AI assistant.**

[![Live Demo](https://img.shields.io/badge/Demo-csic--orpin.vercel.app-2563EB?style=for-the-badge&logo=vercel&logoColor=white)](https://csic-orpin.vercel.app)
[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/Akshitkumar23/CSIC/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/Akshitkumar23/CSIC/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

<p align="center">
  <a href="#-about-the-project">About</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-demo-credentials">Demo Accounts</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-verification">Testing</a> •
  <a href="#-repository-structure">Architecture</a>
</p>

</div>

---

## 📖 About the Project

**CSIC (Cloud-Based Student Information Chatbot)** is a modern, unified academic management portal designed for universities and colleges. It bridges traditional Enterprise Resource Planning (ERP) databases with an intuitive, conversational AI interface.

Instead of navigating complex nested menus, students can query attendance, exam grades, fee balances, and institutional circulars in natural language. Queries are processed through a deterministic RAG (Retrieval-Augmented Generation) pipeline backed by SQL verification—guaranteeing zero hallucinations and real-time accuracy.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Grounded AI Assistant** | ChatGPT-style clean conversational UI. Automatically classifies intents, queries normalized SQL tables, and cites verified institutional policies. |
| 📊 **Attendance Tracker** | Real-time percentage rings, subject-level breakdowns, and automatic warnings for subjects below the mandatory 75% threshold. |
| 📝 **Examinations & Marks** | Semester-wise grade distribution, marks transcripts, and GPA summaries. |
| 💳 **Fee Management** | Clear digital fee invoices with transparent transaction history and simulated instant fee settlement. |
| 🗓️ **Dynamic Timetable** | Day-by-day weekly schedule with real-time highlights for current day and lecture venues. |
| 📢 **Notice Circulars** | Categorized official circulars (Examinations, Academic, Urgent, Events) with search filtering. |
| 🛡️ **Role-Based Portals (RBAC)** | Dedicated, isolated dashboards for **Students**, **Faculty** (at-risk rosters), and **Administrators** (user enrollment). |
| ⚡ **Performance Optimized** | SWR in-memory caching with promise deduplication for sub-100ms instant page loads and zero layout shift. |

---

## 🛠️ Tech Stack

```text
Frontend   │ React 18 • TypeScript 5.5 • Tailwind CSS • Vite • Lucide Icons
Backend    │ FastAPI (Python 3.12) • OAuth2 / JWT • Pydantic v2 • Uvicorn
Database   │ PostgreSQL 16 (Cloud / Supabase) • SQLite (Local Zero-Config Dev)
AI & RAG   │ Hybrid TF-IDF Intent Classifier • Direct SQL Grounding • Policy RAG
Cloud & CI │ Vercel Multi-Service • Render Cloud • GitHub Actions CI/CD
```

---

## 👥 Demo Credentials

The login page features **1-Click Quick Login** buttons for instant access, or you can use these verified accounts:

| Role | Name | Email | Password | Access Scope |
|---|---|---|---|---|
| **Student** | Akshit | `akshit@csic.edu` | `1234` | Personal dashboard, attendance, marks, fees & chatbot |
| **Student** | Rashi | `rashi@csic.edu` | `1234` | Full student records & circulars |
| **Student** | Vanshika | `vanshika@csic.edu` | `1234` | Full student records & circulars |
| **Student** | Silki | `silki@csic.edu` | `1234` | Full student records & circulars |
| **Faculty** | Rajesh Kumar | `rajesh.kumar@csic.edu` | `1234` | At-risk student monitoring & notices |
| **Admin** | Administrator | `admin@csic.edu` | `1234` | System analytics, student roster & announcements |

---

## 🚀 Quickstart

### Prerequisites
- **Python 3.12+**
- **Node.js 20+**

### ⚡ Option A: 1-Click Launcher (Windows)
Double-click `run_dev.bat` or run in PowerShell:
```powershell
.\run_dev.ps1
```
> *This automatically seeds the local SQLite database, starts the FastAPI backend at `http://localhost:8000`, and launches the Vite frontend at `http://localhost:5173`.*

---

### 💻 Option B: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Akshitkumar23/CSIC.git
   cd CSIC
   ```

2. **Start Backend:**
   ```bash
   # Create virtual environment & install dependencies
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt

   # Initialize database & run FastAPI
   python database/init_db.py
   uvicorn backend.app.main:app --reload --port 8000
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Open in Browser:**
   - 🌐 **Web Portal:** `http://localhost:5173`
   - 📑 **API Documentation (Swagger UI):** `http://localhost:8000/docs`

---

## 🧪 Verification

Run the automated test and build verification suite locally:

```bash
# 1. Backend API, Security & AI tests (111 tests)
python -m pytest backend/tests -v

# 2. Database schema initialization & table verification
python database/init_db.py

# 3. Frontend production build & type checks
cd frontend && npm.cmd run build
```

---

## 📁 Repository Structure

```text
CSIC/
├── .github/workflows/ci.yml    # Automated CI/CD pipeline (PostgreSQL 16, Python 3.12, Node 20)
├── api/index.py                # Serverless entrypoint for Vercel backend
├── backend/
│   ├── app/
│   │   ├── api/v1/             # Modular REST endpoints (auth, students, attendance, fees, etc.)
│   │   ├── core/               # Security, JWT auth, CORS & configuration
│   │   ├── models/             # Pydantic v2 schemas
│   │   ├── repositories/       # Parameterized ANSI SQL repository layer
│   │   └── services/           # Domain logic, NLP classifier & RAG chatbot service
│   ├── tests/                  # 111-test automated Pytest suite
│   ├── main.py                 # Isolated container entrypoint
│   └── requirements.txt        # Backend dependencies
├── database/
│   ├── migrations/             # Sequential SQL migrations (001 to 006)
│   ├── init_db.py              # Zero-dependency database initialiser & seed runner
│   └── modules_schema.sql      # 4-Module conceptual reference schema
├── docs/                       # Architecture diagrams, viva prep & SQL demonstration guides
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI widgets (AttendanceCard, FeeSummaryCard, etc.)
│   │   ├── pages/              # Portal views (StudentDashboard, ChatPage, Admin, Faculty)
│   │   ├── services/           # SWR in-memory caching & deduplicated API client
│   │   └── types/              # Strict TypeScript domain interfaces
│   ├── package.json            # Frontend dependencies
│   ├── tailwind.config.js      # Styling & typography tokens
│   └── vite.config.ts          # Build configuration & code splitting
├── render.yaml                 # Render cloud deployment blueprint
├── vercel.json                 # Vercel multi-service routing
├── run_dev.bat                 # Windows CMD launcher
├── run_dev.ps1                 # PowerShell launcher
└── README.md                   # Project documentation
```

---

## 📄 License

Developed as an open-source educational capstone project for the **Cloud-Based Student Information Chatbot (CSIC)** presentation.
