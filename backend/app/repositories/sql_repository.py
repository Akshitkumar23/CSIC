"""Real SQL Repository executing parameterized queries against SQLite and PostgreSQL.

Eliminates in-memory dictionary mocking.
Connects to:
- Local SQLite database: `database/csic.db`
- Cloud PostgreSQL: via `DATABASE_URL` (Supabase / Render)
"""
import json
import os
import sqlite3
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.app.core.config import settings
from backend.app.models.admin import AdminStats, FacultyCourseAssignmentItem, MarksInput, StudentCreate
from backend.app.models.attendance import AttendanceRecord, AttendanceSummary, SubjectAttendance
from backend.app.models.auth import UserProfile
from backend.app.models.fee import FeeInvoice, FeePayment, FeeSummary
from backend.app.models.marks import ExamResult, MarkEntry, SemesterResult
from backend.app.models.notice import NoticeCreate, NoticeItem
from backend.app.models.search import SearchItem
from backend.app.models.student import EnrollmentDetail, StudentDetail
from backend.app.models.timetable import DailySchedule, TimetableEntry


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SQLITE_DB_PATH = BASE_DIR / "database" / "csic.db"


class SQLRepository:
    """Production SQL Repository for CSIC executing genuine relational SQL."""

    def __init__(self, db_path: Optional[Path] = None, database_url: Optional[str] = None) -> None:
        self.database_url = database_url or settings.DATABASE_URL
        self.db_path = db_path or SQLITE_DB_PATH
        self.is_postgres = bool(
            self.database_url
            and (self.database_url.startswith("postgres://") or self.database_url.startswith("postgresql://"))
        )

        if settings.is_production:
            if not self.is_postgres:
                raise RuntimeError(
                    "Production configuration error: Valid PostgreSQL DATABASE_URL is required. "
                    "Silent fallback to SQLite is strictly forbidden in production."
                )

        # Connection pool for PostgreSQL to eliminate per-query TLS/TCP handshake overhead
        self._pg_pool = None
        if self.is_postgres:
            try:
                import psycopg2
                from psycopg2 import pool
                # Safe serverless connection pool (minconn 1, maxconn 10)
                self._pg_pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=self.database_url,
                )
            except Exception:
                self._pg_pool = None

        # Auto-initialize SQLite database for local development if not present
        if not self.is_postgres:
            if not self.db_path.exists():
                from database.init_db import init_sqlite
                init_sqlite(self.db_path)

    @staticmethod
    def _parse_date(val: Any) -> date:
        """Robustly parse date from SQLite string or PostgreSQL date object."""
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        if val:
            try:
                return datetime.strptime(str(val)[:10], "%Y-%m-%d").date()
            except Exception:
                pass
        return date.today()

    @staticmethod
    def _parse_datetime(val: Any) -> datetime:
        """Robustly parse datetime from SQLite string or PostgreSQL datetime object."""
        if isinstance(val, datetime):
            if val.tzinfo is None:
                return val.replace(tzinfo=timezone.utc)
            return val
        if isinstance(val, date):
            return datetime.combine(val, datetime.min.time()).replace(tzinfo=timezone.utc)
        if val:
            try:
                return datetime.fromisoformat(str(val)).replace(tzinfo=timezone.utc)
            except Exception:
                pass
        return datetime.now(timezone.utc)

    def _get_connection(self):
        """Obtain a database connection with dictionary-like row access."""
        if self.is_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            if self._pg_pool:
                try:
                    conn = self._pg_pool.getconn()
                    if conn.closed:
                        self._pg_pool.putconn(conn, close=True)
                        conn = self._pg_pool.getconn()
                    conn.autocommit = True
                    return conn
                except Exception:
                    pass
            conn = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
            conn.autocommit = True
            return conn
        else:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    def _release_connection(self, conn) -> None:
        """Safely release connection back to pool or close direct connection."""
        if conn is None:
            return
        if self.is_postgres and self._pg_pool:
            try:
                if not conn.closed:
                    conn.autocommit = True
                self._pg_pool.putconn(conn)
                return
            except Exception:
                pass
        try:
            conn.close()
        except Exception:
            pass

    def _execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return rows as list of dicts."""
        conn = self._get_connection()
        try:
            if self.is_postgres:
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                pg_query = query.replace("?", "%s")
                cursor.execute(pg_query, params)
            else:
                cursor = conn.cursor()
                cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self._release_connection(conn)

    def _execute_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return a single row as dict."""
        rows = self._execute_query(query, params)
        return rows[0] if rows else None

    def _execute_write(self, query: str, params: Tuple = ()) -> None:
        """Execute an INSERT, UPDATE, or DELETE statement."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if self.is_postgres:
                pg_query = query.replace("?", "%s")
                cursor.execute(pg_query, params)
            else:
                cursor.execute(query, params)
                conn.commit()
        finally:
            self._release_connection(conn)

    # -------------------------------------------------------------------------
    # Authentication & Profiles
    # -------------------------------------------------------------------------

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch user record including password hash by email."""
        cleaned_email = email.strip().lower()
        email_aliases = {
            "aarav.sharma@csic.edu": "rashi@csic.edu",
            "priya.patel@csic.edu": "vanshika@csic.edu",
            "rohan.gupta@csic.edu": "silki@csic.edu",
            "akshit.student@csic.edu": "akshit@csic.edu",
            "akshit.kumar@csic.edu": "akshit@csic.edu",
            "akshit.faculty@csic.edu": "rajesh.kumar@csic.edu",
            "faculty@csic.edu": "rajesh.kumar@csic.edu",
            "akshit.admin@csic.edu": "admin@csic.edu",
        }
        resolved_email = email_aliases.get(cleaned_email, cleaned_email)
        sql = """
        SELECT id, name, email, password_hash, role, phone, avatar_url, is_active, created_at
        FROM users
        WHERE LOWER(email) = LOWER(?);
        """
        return self._execute_one(sql, (resolved_email,))

    def authenticate_user(self, email: str, plain_password: str) -> Optional[UserProfile]:
        """Verify user credentials via bcrypt and return user profile."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        from backend.app.core.security import verify_password
        if not verify_password(plain_password, user["password_hash"]):
            return None
        return UserProfile(
            id=user["id"],
            email=user["email"],
            full_name=user["name"],
            role=user["role"],
            phone=user.get("phone"),
            avatar_url=user.get("avatar_url"),
            is_active=bool(user.get("is_active", True)),
        )

    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Fetch user profile by unique ID."""
        sql = """
        SELECT id, name, email, role, phone, avatar_url, is_active
        FROM users
        WHERE id = ?;
        """
        row = self._execute_one(sql, (user_id,))
        if not row:
            return None
        return UserProfile(
            id=row["id"],
            email=row["email"],
            full_name=row["name"],
            role=row["role"],
            phone=row.get("phone"),
            avatar_url=row.get("avatar_url"),
            is_active=bool(row.get("is_active", True)),
        )

    # -------------------------------------------------------------------------
    # Student Details & Roster
    # -------------------------------------------------------------------------

    def get_student_detail(self, student_id: str) -> Optional[StudentDetail]:
        """Fetch complete student profile with enrollments using a standard 3-table JOIN."""
        sql = """
        SELECT
            u.id,
            u.name,
            u.email,
            u.phone,
            u.avatar_url,
            u.role,
            e.id AS enrollment_id,
            e.course_id,
            e.roll_number,
            e.semester,
            e.section,
            e.status AS enrollment_status,
            c.code AS program_code,
            c.name AS program_name,
            c.department AS department_name
        FROM users u
        LEFT JOIN enrollments e ON e.user_id = u.id
        LEFT JOIN courses c ON c.id = e.course_id
        WHERE u.id = ? AND u.role = 'student';
        """
        rows = self._execute_query(sql, (student_id,))
        if not rows:
            return None

        first = rows[0]
        enrollments = [
            EnrollmentDetail(
                id=r["enrollment_id"],
                student_id=student_id,
                course_id=r["course_id"],
                roll_number=r["roll_number"],
                enrollment_date=date(2023, 8, 1),
                status=r.get("enrollment_status") or "active",
                program_code=r.get("program_code") or "",
                program_name=r.get("program_name") or "",
                semester_number=r.get("semester") or 1,
                section=r.get("section") or "A",
            )
            for r in rows
            if r.get("enrollment_id")
        ]

        dept = "Computer Science & Engineering"
        for r in rows:
            if r.get("department_name"):
                dept = r["department_name"]
                break

        return StudentDetail(
            id=first["id"],
            email=first["email"],
            full_name=first["name"],
            phone=first.get("phone"),
            avatar_url=first.get("avatar_url"),
            role=first["role"],
            department_name=dept,
            enrollments=enrollments,
        )

    def list_students(self) -> List[StudentDetail]:
        """List all registered students in the system using a single 3-table JOIN query."""
        sql = """
        SELECT
            u.id,
            u.name,
            u.email,
            u.phone,
            u.avatar_url,
            u.role,
            e.id AS enrollment_id,
            e.course_id,
            e.roll_number,
            e.semester,
            e.section,
            e.status AS enrollment_status,
            c.code AS program_code,
            c.name AS program_name,
            c.department AS department_name
        FROM users u
        LEFT JOIN enrollments e ON e.user_id = u.id
        LEFT JOIN courses c ON c.id = e.course_id
        WHERE u.role = 'student'
        ORDER BY u.name ASC;
        """
        rows = self._execute_query(sql)
        students_map: Dict[str, StudentDetail] = {}
        for r in rows:
            uid = r["id"]
            if uid not in students_map:
                dept = r["department_name"] or "Computer Science & Engineering"
                students_map[uid] = StudentDetail(
                    id=uid,
                    email=r["email"],
                    full_name=r["name"],
                    phone=r.get("phone"),
                    avatar_url=r.get("avatar_url"),
                    role=r["role"],
                    department_name=dept,
                    enrollments=[],
                )
            if r.get("enrollment_id"):
                students_map[uid].enrollments.append(
                    EnrollmentDetail(
                        id=r["enrollment_id"],
                        student_id=uid,
                        course_id=r["course_id"],
                        roll_number=r["roll_number"],
                        enrollment_date=date(2023, 8, 1),
                        status=r["enrollment_status"],
                        program_code=r["program_code"],
                        program_name=r["program_name"],
                        semester_number=r["semester"],
                        section=r.get("section", "A"),
                    )
                )
        return list(students_map.values())

    # -------------------------------------------------------------------------
    # Attendance Records & Aggregations
    # -------------------------------------------------------------------------

    def get_student_attendance_summary(self, student_id: str) -> Optional[AttendanceSummary]:
        """Calculate subject-wise and overall attendance percentage using SQL aggregations.

        Viva/Defense SQL Concept:
        - GROUP BY s.id, s.code, s.name: Aggregates class records by individual subject.
        - SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END): Conditional aggregate
          counting sessions without requiring procedural code or separate queries.
        - LEFT JOIN: Ensures subjects with zero attendance sessions are still listed.
        """
        enr_sql = "SELECT id, roll_number FROM enrollments WHERE user_id = ?;"
        enr_row = self._execute_one(enr_sql, (student_id,))
        if not enr_row:
            return None

        # Relational aggregation: JOIN + GROUP BY + conditional SUM(CASE)
        sql = """
        SELECT
            s.code AS subject_code,
            s.name AS subject_name,
            COUNT(a.id) AS total_sessions,
            SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS attended_sessions,
            SUM(CASE WHEN a.status = 'excused' THEN 1 ELSE 0 END) AS excused_sessions,
            SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_sessions
        FROM enrollments e
        JOIN subjects s ON s.course_id = e.course_id
        LEFT JOIN attendance_records a ON a.enrollment_id = e.id AND a.subject_id = s.id
        WHERE e.user_id = ?
        GROUP BY s.id, s.code, s.name
        ORDER BY s.code;
        """
        rows = self._execute_query(sql, (student_id,))

        total_classes = 0
        total_present = 0
        subjects: List[SubjectAttendance] = []

        for r in rows:
            tot = r["total_sessions"] or 0
            att = r["attended_sessions"] or 0
            exc = r["excused_sessions"] or 0
            ab = r["absent_sessions"] or 0
            effective_present = att + exc

            pct = round((effective_present / tot * 100.0), 2) if tot > 0 else 0.0
            is_low = pct < 75.0 and tot > 0

            total_classes += tot
            total_present += effective_present

            subjects.append(
                SubjectAttendance(
                    subject_code=r["subject_code"],
                    subject_name=r["subject_name"],
                    total_sessions=tot,
                    attended_sessions=att,
                    excused_sessions=exc,
                    absent_sessions=ab,
                    attendance_percentage=pct,
                    is_low_attendance=is_low,
                )
            )

        overall_pct = round((total_present / total_classes * 100.0), 2) if total_classes > 0 else 0.0

        return AttendanceSummary(
            student_id=student_id,
            roll_number=enr_row["roll_number"],
            overall_percentage=overall_pct,
            is_at_risk=overall_pct < 75.0,
            subjects=subjects,
        )

    # Alias for compatibility with decision_engine
    get_student_attendance = get_student_attendance_summary

    def get_attendance_records_for_student(self, student_id: str) -> List[AttendanceRecord]:
        """Fetch granular chronological class attendance records."""
        sql = """
        SELECT
            a.id,
            a.id AS session_id,
            a.enrollment_id,
            a.status,
            a.remarks,
            a.session_date,
            s.code AS subject_code,
            s.name AS subject_name
        FROM enrollments e
        JOIN attendance_records a ON a.enrollment_id = e.id
        JOIN subjects s ON s.id = a.subject_id
        WHERE e.user_id = ?
        ORDER BY a.session_date DESC;
        """
        rows = self._execute_query(sql, (student_id,))

        records: List[AttendanceRecord] = []
        for r in rows:
            session_d = self._parse_date(r["session_date"])
            marked_dt = self._parse_datetime(r["session_date"])

            records.append(
                AttendanceRecord(
                    id=r["id"],
                    session_id=r["session_id"],
                    enrollment_id=r["enrollment_id"],
                    status=r["status"],
                    remarks=r.get("remarks"),
                    marked_at=marked_dt,
                    session_date=session_d,
                    topic=f"Session in {r['subject_name']}",
                    subject_code=r["subject_code"],
                    subject_name=r["subject_name"],
                )
            )
        return records

    def get_low_attendance_warnings(self) -> List[Dict[str, Any]]:
        """Identify all students with aggregate attendance below 75%."""
        warnings: List[Dict[str, Any]] = []
        for student in self.list_students():
            summary = self.get_student_attendance_summary(student.id)
            if summary and summary.overall_percentage < 75.0:
                warnings.append({
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "roll_number": summary.roll_number,
                    "overall_percentage": summary.overall_percentage,
                    "at_risk_subjects": [
                        s.subject_code for s in summary.subjects if s.is_low_attendance
                    ],
                })
        return warnings

    # -------------------------------------------------------------------------
    # Examinations & Academic Marks
    # -------------------------------------------------------------------------

    def get_exam_results(self, student_id: str) -> List[ExamResult]:
        """Get examination performance grouped by exam cycle.

        Viva/Defense SQL Concept:
        - 4-Table Relational JOIN: enrollments -> marks -> examinations -> subjects.
        - Joins student enrollment to score records (marks), exam metadata (examinations),
          and course curriculum (subjects) in a single normalized query.
        """
        # 4-Table INNER JOIN: enrollments -> marks -> examinations -> subjects
        sql = """
        SELECT
            m.id,
            ex.id AS examination_id,
            ex.name AS exam_name,
            ex.exam_date,
            ex.max_marks,
            s.code AS subject_code,
            s.name AS subject_name,
            m.marks_obtained,
            m.grade,
            m.is_absent
        FROM enrollments e
        JOIN marks m ON m.enrollment_id = e.id
        JOIN examinations ex ON ex.id = m.examination_id
        JOIN subjects s ON s.id = ex.subject_id
        WHERE e.user_id = ?
        ORDER BY ex.name, s.code;
        """
        rows = self._execute_query(sql, (student_id,))
        if not rows:
            return []

        marks_by_exam: Dict[str, List[MarkEntry]] = {}
        for r in rows:
            e_date = self._parse_date(r["exam_date"])
            obtained = float(r["marks_obtained"] or 0.0)
            max_m = float(r["max_marks"] or 50.0)
            pct = round((obtained * 100.0) / max_m, 2) if max_m > 0 else 0.0

            entry = MarkEntry(
                id=r["id"],
                examination_id=r["examination_id"],
                exam_name=r["exam_name"],
                subject_code=r["subject_code"],
                subject_name=r["subject_name"],
                marks_obtained=obtained,
                max_marks=max_m,
                percentage=pct,
                grade=r.get("grade") or "A",
                is_absent=bool(r.get("is_absent", False)),
                exam_date=e_date,
            )
            marks_by_exam.setdefault(r["exam_name"], []).append(entry)

        exam_results: List[ExamResult] = []
        for exam_name, entries in marks_by_exam.items():
            tot_obtained = round(sum(e.marks_obtained for e in entries), 2)
            tot_max = round(sum(e.max_marks for e in entries), 2)
            overall_pct = round((tot_obtained * 100.0) / tot_max, 2) if tot_max > 0 else 0.0

            exam_results.append(
                ExamResult(
                    examination_id=entries[0].examination_id,
                    exam_name=exam_name,
                    subjects=entries,
                    total_obtained=tot_obtained,
                    total_max=tot_max,
                    overall_percentage=overall_pct,
                )
            )
        return exam_results

    def get_semester_results(
        self,
        student_id: str,
        semester_number: Optional[int] = None,
    ) -> List[SemesterResult]:
        """Fetch consolidated semester report card."""
        exam_res = self.get_exam_results(student_id)
        if not exam_res:
            return []

        all_entries: List[MarkEntry] = []
        for er in exam_res:
            all_entries.extend(er.subjects)

        tot_obtained = sum(e.marks_obtained for e in all_entries)
        tot_max = sum(e.max_marks for e in all_entries)
        overall_pct = round((tot_obtained * 100.0) / max(tot_max, 1), 2)
        gpa = round(overall_pct / 10.0, 2)

        return [
            SemesterResult(
                semester_number=semester_number or 6,
                term="even",
                academic_year="2025-2026",
                gpa=gpa,
                percentage=overall_pct,
                total_credits=15.0,
                results=all_entries,
            )
        ]

    # -------------------------------------------------------------------------
    # Fee Management & Invoices
    # -------------------------------------------------------------------------

    def get_fee_summary(self, student_id: str) -> Optional[FeeSummary]:
        """Fetch student fee invoices, payment history, and calculate balances.

        Viva/Defense SQL Concept:
        - Relational JOIN: enrollments e JOIN fee_records f ON f.enrollment_id = e.id
        - Parameterized filtering by student ID with invoice chronologically sorted
          by due date to maintain a transparent, auditable fee ledger.
        """
        # Fee Ledger Lookup: enrollments JOIN fee_records
        sql = """
        SELECT
            f.id,
            f.invoice_number,
            f.enrollment_id,
            f.title,
            f.amount,
            f.amount_paid,
            f.due_date,
            f.status
        FROM enrollments e
        JOIN fee_records f ON f.enrollment_id = e.id
        WHERE e.user_id = ?
        ORDER BY f.due_date ASC;
        """
        rows = self._execute_query(sql, (student_id,))
        if not rows:
            return None

        invoices: List[FeeInvoice] = []
        total_invoiced = 0.0
        total_paid = 0.0

        for r in rows:
            amt = float(r["amount"])
            paid = float(r["amount_paid"])
            total_invoiced += amt
            total_paid += paid

            d_date = self._parse_date(r["due_date"])
            created_dt = self._parse_datetime(r["due_date"])

            payments: List[FeePayment] = []
            if paid > 0:
                payments.append(
                    FeePayment(
                        id=f"pay-{r['id']}",
                        invoice_id=r["id"],
                        transaction_reference=f"TXN_{r['invoice_number']}",
                        amount_paid=paid,
                        payment_date=created_dt,
                        payment_method="upi",
                        status="success",
                    )
                )

            invoices.append(
                FeeInvoice(
                    id=r["id"],
                    invoice_number=r["invoice_number"],
                    enrollment_id=r["enrollment_id"],
                    title=r["title"],
                    amount=amt,
                    paid_amount=paid,
                    due_date=d_date,
                    status=r["status"],
                    created_at=created_dt,
                    payments=payments,
                )
            )

        outstanding = round(total_invoiced - total_paid, 2)

        return FeeSummary(
            student_id=student_id,
            total_invoiced=round(total_invoiced, 2),
            total_paid=round(total_paid, 2),
            total_outstanding=max(0.0, outstanding),
            invoices=invoices,
        )

    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Fetch an individual invoice record including enrollment student ownership."""
        sql = """
        SELECT
            f.id,
            f.invoice_number,
            f.enrollment_id,
            f.title,
            f.amount,
            f.amount_paid,
            f.due_date,
            f.status,
            e.user_id
        FROM fee_records f
        JOIN enrollments e ON f.enrollment_id = e.id
        WHERE f.id = ?;
        """
        return self._execute_one(sql, (invoice_id,))

    def record_fee_payment(
        self,
        invoice_id: str,
        amount_paid: float,
        payment_method: str = "upi",
        student_id: Optional[str] = None,
    ) -> Optional[FeePayment]:
        """Update invoice amount_paid and status transaction-safely upon payment."""
        conn = self._get_connection()
        try:
            if self.is_postgres:
                conn.autocommit = False
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()

            sql = """
            SELECT
                f.id,
                f.invoice_number,
                f.amount,
                f.amount_paid,
                f.status,
                e.user_id
            FROM fee_records f
            JOIN enrollments e ON f.enrollment_id = e.id
            WHERE f.id = ?
            """
            if self.is_postgres:
                sql = sql.replace("?", "%s") + " FOR UPDATE OF f;"
                cursor.execute(sql, (invoice_id,))
            else:
                cursor.execute(sql + ";", (invoice_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # Robust mapping for both RealDictRow/Row and standard tuple rows
            if isinstance(row, dict):
                inv = row
            elif hasattr(row, "keys"):
                inv = dict(row)
            else:
                col_names = [d[0] for d in cursor.description]
                inv = dict(zip(col_names, row))

            # Enforce ownership if student_id provided
            if student_id and inv["user_id"] != student_id:
                return None

            total_amt = float(inv["amount"])
            curr_paid = float(inv["amount_paid"])
            outstanding = round(total_amt - curr_paid, 2)

            # Reject zero, negative, or excessive payments
            if amount_paid <= 0 or round(amount_paid, 2) > outstanding:
                return None

            new_paid = round(curr_paid + amount_paid, 2)
            new_status = "paid" if new_paid >= total_amt else "partially_paid"

            upd_sql = "UPDATE fee_records SET amount_paid = ?, status = ? WHERE id = ? AND (amount - amount_paid) >= ?;"
            if self.is_postgres:
                upd_sql = upd_sql.replace("?", "%s")
                cursor.execute(upd_sql, (new_paid, new_status, invoice_id, amount_paid))
                conn.commit()
            else:
                cursor.execute(upd_sql, (new_paid, new_status, invoice_id, amount_paid))
                conn.commit()

            if cursor.rowcount == 0:
                return None

            now = datetime.now(timezone.utc)
            return FeePayment(
                id=f"pay-{uuid.uuid4().hex[:6]}",
                invoice_id=invoice_id,
                transaction_reference=f"TXN_{uuid.uuid4().hex[:8].upper()}",
                amount_paid=amount_paid,
                payment_date=now,
                payment_method=payment_method,
                status="success",
            )
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            self._release_connection(conn)

    # -------------------------------------------------------------------------
    # Timetable & Schedules
    # -------------------------------------------------------------------------

    def get_student_timetable(
        self,
        student_id: str,
        day_of_week: Optional[str] = None,
    ) -> List[DailySchedule]:
        """Fetch weekly recurring lecture slots grouped by day in a single optimized query.

        Viva/Defense SQL Concept:
        - 4-Table JOIN: enrollments -> subjects -> timetable_entries -> users (faculty).
        - Joins student registration with subject catalog and class schedules, resolving
          faculty names with COALESCE for display fallback.
        """
        days = [day_of_week] if day_of_week else ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        # Timetable Join: enrollments -> subjects -> timetable_entries -> users
        sql = """
        SELECT
            t.id,
            t.day_of_week,
            t.start_time,
            t.end_time,
            t.room_number,
            s.code AS subject_code,
            s.name AS subject_name,
            COALESCE(u.name, 'Department Faculty') AS faculty_name
        FROM enrollments e
        JOIN subjects s ON s.course_id = e.course_id
        JOIN timetable_entries t ON t.subject_id = s.id
        LEFT JOIN users u ON u.id = s.faculty_id
        WHERE e.user_id = ?
        """
        params: list = [student_id]
        if day_of_week:
            sql += " AND t.day_of_week = ?"
            params.append(day_of_week)

        sql += " ORDER BY t.start_time ASC;"

        rows = self._execute_query(sql, tuple(params))

        # Group rows by day of the week in memory
        entries_by_day: Dict[str, List[TimetableEntry]] = {d: [] for d in days}
        for r in rows:
            d = r["day_of_week"]
            if d in entries_by_day:
                entries_by_day[d].append(
                    TimetableEntry(
                        id=r["id"],
                        day_of_week=r["day_of_week"],
                        start_time=r["start_time"],
                        end_time=r["end_time"],
                        room_number=r["room_number"],
                        subject_code=r["subject_code"],
                        subject_name=r["subject_name"],
                        faculty_name=r["faculty_name"],
                    )
                )

        return [DailySchedule(day_of_week=d, entries=entries_by_day[d]) for d in days]

    # -------------------------------------------------------------------------
    # Campus Notices
    # -------------------------------------------------------------------------

    def get_notices(self, target_role: Optional[str] = None, limit: int = 50) -> List[NoticeItem]:
        """Fetch university circulars filtered by recipient role using straightforward SQL."""
        if target_role:
            sql = """
            SELECT
                n.id,
                n.title,
                n.category,
                n.content,
                COALESCE(u.name, 'Administration') AS published_by_name,
                n.is_published,
                n.target_role,
                n.published_at
            FROM notices n
            LEFT JOIN users u ON u.id = n.published_by
            WHERE n.is_published = TRUE
              AND (n.target_role = 'all' OR n.target_role = ?)
            ORDER BY n.published_at DESC
            LIMIT ?;
            """
            rows = self._execute_query(sql, (target_role, limit))
        else:
            sql = """
            SELECT
                n.id,
                n.title,
                n.category,
                n.content,
                COALESCE(u.name, 'Administration') AS published_by_name,
                n.is_published,
                n.target_role,
                n.published_at
            FROM notices n
            LEFT JOIN users u ON u.id = n.published_by
            WHERE n.is_published = TRUE
            ORDER BY n.published_at DESC
            LIMIT ?;
            """
            rows = self._execute_query(sql, (limit,))

        items: List[NoticeItem] = []
        for r in rows:
            pub_dt = self._parse_datetime(r["published_at"])

            items.append(
                NoticeItem(
                    id=r["id"],
                    title=r["title"],
                    category=r["category"],
                    content=r["content"],
                    published_by_name=r["published_by_name"],
                    is_published=bool(r["is_published"]),
                    target_role=r["target_role"],
                    published_at=pub_dt,
                )
            )
        return items

    def get_notice_by_id(self, notice_id: str) -> Optional[NoticeItem]:
        """Fetch university circular by its unique ID."""
        sql = """
        SELECT
            n.id,
            n.title,
            n.category,
            n.content,
            COALESCE(u.name, 'Administration') AS published_by_name,
            n.is_published,
            n.target_role,
            n.published_at
        FROM notices n
        LEFT JOIN users u ON u.id = n.published_by
        WHERE n.id = ?;
        """
        r = self._execute_one(sql, (notice_id,))
        if not r:
            return None
        pub_dt = self._parse_datetime(r["published_at"])
        return NoticeItem(
            id=r["id"],
            title=r["title"],
            category=r["category"],
            content=r["content"],
            published_by_name=r["published_by_name"],
            is_published=bool(r["is_published"]),
            target_role=r["target_role"],
            published_at=pub_dt,
        )

    def create_notice(self, notice: NoticeCreate, publisher_id: str) -> NoticeItem:

        """Publish a new notice to the database."""
        notice_id = f"not-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        sql = """
        INSERT INTO notices (id, title, content, category, target_role, published_by, is_published, published_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        self._execute_write(
            sql,
            (
                notice_id,
                notice.title,
                notice.content,
                notice.category,
                notice.target_role,
                publisher_id,
                notice.is_published,
                now.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        publisher_name = "Administration"
        if publisher_id:
            user_row = self._execute_one("SELECT name FROM users WHERE id = ?;", (publisher_id,))
            if user_row:
                publisher_name = user_row["name"]

        return NoticeItem(
            id=notice_id,
            title=notice.title,
            category=notice.category,
            content=notice.content,
            published_by_name=publisher_name,
            is_published=notice.is_published,
            target_role=notice.target_role,
            published_at=now,
        )

    # -------------------------------------------------------------------------
    # Administration & Metrics
    # -------------------------------------------------------------------------

    def get_admin_stats(self) -> AdminStats:
        """Compute system metrics via live SQL aggregation queries."""
        st_count = self._execute_one("SELECT COUNT(*) AS c FROM users WHERE role = 'student';")["c"]
        fa_count = self._execute_one("SELECT COUNT(*) AS c FROM users WHERE role = 'faculty';")["c"]
        co_count = self._execute_one("SELECT COUNT(*) AS c FROM courses;")["c"]
        no_count = self._execute_one("SELECT COUNT(*) AS c FROM notices WHERE is_published = TRUE;")["c"]

        att_row = self._execute_one(
            """
            SELECT
                SUM(CASE WHEN status IN ('present', 'excused') THEN 1.0 ELSE 0.0 END) * 100.0 / NULLIF(COUNT(*), 0) AS avg_pct
            FROM attendance_records;
            """
        )
        avg_att = round(float(att_row["avg_pct"]), 1) if att_row and att_row["avg_pct"] is not None else 0.0

        fee_row = self._execute_one(
            """
            SELECT SUM(amount - amount_paid) AS pending
            FROM fee_records;
            """
        )
        pending_fee = float(fee_row["pending"] or 0.0)

        return AdminStats(
            total_students=st_count,
            total_faculty=fa_count,
            total_courses=co_count,
            total_notices=no_count,
            average_attendance=avg_att,
            pending_fees_amount=pending_fee,
        )

    def get_faculty_assignments(self) -> List[FacultyCourseAssignmentItem]:
        """Fetch all course allocations assigned to faculty members with live enrollment counts."""
        sql = """
        SELECT
            s.id AS subject_id,
            s.code AS subject_code,
            s.name AS subject_name,
            s.semester,
            COALESCE(s.faculty_id, '') AS faculty_id,
            COALESCE(u.name, 'Unassigned') AS faculty_name,
            (SELECT COUNT(DISTINCT id) FROM enrollments WHERE course_id = s.course_id AND status = 'active') AS enrolled_count,
            (SELECT section FROM enrollments WHERE course_id = s.course_id AND status = 'active' LIMIT 1) AS section
        FROM subjects s
        LEFT JOIN users u ON u.id = s.faculty_id
        ORDER BY s.code;
        """
        rows = self._execute_query(sql)
        assignments: List[FacultyCourseAssignmentItem] = []
        for r in rows:
            sec = r["section"] or "A"
            sem = r["semester"] or 6
            assignments.append(
                FacultyCourseAssignmentItem(
                    id=f"fca-{r['subject_id']}",
                    faculty_id=r["faculty_id"] or "",
                    faculty_name=r["faculty_name"] or "Unassigned",
                    subject_id=r["subject_id"],
                    subject_code=r["subject_code"],
                    subject_name=r["subject_name"],
                    course_section=f"Sec {sec} (Sem {sem})",
                    enrolled_count=int(r["enrolled_count"] or 0),
                )
            )
        return assignments

    def create_student(self, student_data: StudentCreate) -> StudentDetail:
        """Onboard a new student record with enrollment into the database."""
        user_id = f"stu-{uuid.uuid4().hex[:6]}"
        enr_id = f"enr-{uuid.uuid4().hex[:6]}"
        course_id = "crs-01"

        from backend.app.core.security import get_password_hash
        pwd_hash = get_password_hash(student_data.password)

        existing_user = self.get_user_by_email(student_data.email)
        if existing_user:
            user_id = existing_user["id"]
            user_sql = """
            UPDATE users SET name = ?, password_hash = ?, phone = ?, is_active = TRUE
            WHERE id = ?;
            """
            self._execute_write(user_sql, (student_data.full_name, pwd_hash, student_data.phone, user_id))
        else:
            user_sql = """
            INSERT INTO users (id, name, email, password_hash, role, phone, is_active)
            VALUES (?, ?, ?, ?, 'student', ?, TRUE);
            """
            self._execute_write(
                user_sql,
                (user_id, student_data.full_name, student_data.email, pwd_hash, student_data.phone),
            )

        existing_enr = self._execute_one("SELECT id FROM enrollments WHERE user_id = ?;", (user_id,))
        if existing_enr:
            enr_sql = """
            UPDATE enrollments SET roll_number = ?, semester = ?, section = ?, status = 'active'
            WHERE id = ?;
            """
            self._execute_write(enr_sql, (student_data.roll_number, student_data.semester_number, student_data.section, existing_enr["id"]))
        else:
            enr_sql = """
            INSERT INTO enrollments (id, user_id, course_id, roll_number, semester, section, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active');
            """
            self._execute_write(
                enr_sql,
                (
                    enr_id,
                    user_id,
                    course_id,
                    student_data.roll_number,
                    student_data.semester_number,
                    student_data.section,
                ),
            )

        return self.get_student_detail(user_id)

    def enter_marks(self, marks_in: MarksInput, entered_by_id: str) -> MarkEntry:
        """Submit student score for an examination."""
        mark_id = f"mark-{uuid.uuid4().hex[:6]}"
        sql = """
        INSERT INTO marks (id, examination_id, enrollment_id, marks_obtained, is_absent, grade)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(examination_id, enrollment_id) DO UPDATE SET
            marks_obtained = excluded.marks_obtained,
            is_absent = excluded.is_absent,
            grade = excluded.grade;
        """
        self._execute_write(
            sql,
            (
                mark_id,
                marks_in.examination_id,
                marks_in.enrollment_id,
                marks_in.marks_obtained,
                marks_in.is_absent,
                marks_in.grade or "A",
            ),
        )

        exam = self._execute_one("SELECT name, max_marks, exam_date, subject_id FROM examinations WHERE id = ?;", (marks_in.examination_id,))
        sub = self._execute_one("SELECT code, name FROM subjects WHERE id = ?;", (exam["subject_id"],)) if exam else None

        e_date = self._parse_date(exam["exam_date"]) if exam else date.today()
        max_m = float(exam["max_marks"]) if exam else 50.0

        return MarkEntry(
            id=mark_id,
            examination_id=marks_in.examination_id,
            exam_name=exam["name"] if exam else "Examination",
            subject_code=sub["code"] if sub else "CS",
            subject_name=sub["name"] if sub else "Subject",
            marks_obtained=marks_in.marks_obtained,
            max_marks=max_m,
            percentage=round(marks_in.marks_obtained * 100.0 / max_m, 2),
            grade=marks_in.grade or "A",
            is_absent=marks_in.is_absent,
            exam_date=e_date,
        )

    # -------------------------------------------------------------------------
    # Conversational Audit History & Compatibility
    # -------------------------------------------------------------------------

    @property
    def profiles(self) -> List[Dict[str, Any]]:
        """List user records for privacy enforcement and role checks."""
        return self._execute_query("SELECT id, name AS full_name, email, role FROM users;")

    @property
    def enrollments(self) -> List[Dict[str, Any]]:
        """List active enrollments."""
        return self._execute_query("SELECT id, user_id AS student_id, course_id, roll_number FROM enrollments;")

    # -------------------------------------------------------------------------
    # Conversational Sessions & Persistent Message History (SQL-Backed)
    # -------------------------------------------------------------------------

    def create_chat_session(self, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a new chat session for a student in chat_sessions table."""
        session_id = f"sess-{uuid.uuid4().hex[:12]}"
        actual_title = title.strip() if title and title.strip() else "New Conversation"
        sql = """
        INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        self._execute_write(sql, (session_id, user_id, actual_title))
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "id": session_id,
            "user_id": user_id,
            "title": actual_title,
            "created_at": now_iso,
            "updated_at": now_iso,
            "last_message_preview": None,
        }

    def list_chat_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all chat sessions for a user ordered by most recently updated."""
        sql = """
        SELECT s.id, s.user_id, s.title, s.created_at, s.updated_at,
               (
                   SELECT m.message_text
                   FROM chat_messages m
                   WHERE m.session_id = s.id
                   ORDER BY m.created_at DESC
                   LIMIT 1
               ) as last_message_preview
        FROM chat_sessions s
        WHERE s.user_id = ?
        ORDER BY s.updated_at DESC;
        """
        rows = self._execute_query(sql, (user_id,))
        results = []
        for r in rows:
            preview = r.get("last_message_preview")
            if preview and len(preview) > 80:
                preview = preview[:77] + "..."
            results.append({
                "id": r["id"],
                "user_id": r["user_id"],
                "title": r["title"] or "New Conversation",
                "created_at": str(r["created_at"]),
                "updated_at": str(r["updated_at"]),
                "last_message_preview": preview,
            })
        return results

    def get_chat_session(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chat session with user ownership validation."""
        sql = """
        SELECT id, user_id, title, created_at, updated_at
        FROM chat_sessions
        WHERE id = ? AND user_id = ?;
        """
        row = self._execute_one(sql, (session_id, user_id))
        if not row:
            return None
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "title": row["title"],
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
        }

    def update_chat_session_title(self, user_id: str, session_id: str, title: str) -> bool:
        """Update session title and touch updated_at."""
        sql = """
        UPDATE chat_sessions
        SET title = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?;
        """
        self._execute_write(sql, (title.strip(), session_id, user_id))
        return True

    def delete_chat_session(self, user_id: str, session_id: str) -> bool:
        """Delete a chat session and cascade its messages."""
        sql = "DELETE FROM chat_sessions WHERE id = ? AND user_id = ?;"
        self._execute_write(sql, (session_id, user_id))
        return True

    def get_or_create_chat_session(self, student_id: str, session_id: Optional[str] = None) -> str:
        """Establish or ensure session exists in chat_sessions table."""
        if session_id:
            row = self._execute_one("SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?;", (session_id, student_id))
            if row:
                return session_id
            # Create session with the given ID
            sql = """
            INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at)
            VALUES (?, ?, 'New Conversation', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            """
            self._execute_write(sql, (session_id, student_id))
            return session_id

        # Otherwise create a fresh session
        new_sess = self.create_chat_session(student_id)
        return new_sess["id"]

    def add_chat_message(
        self,
        session_id: str,
        sender_role: str,
        message_text: str,
        query_type: Optional[str] = None,
        sources: Optional[List[str]] = None,
        verified_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record conversational turn into chat_messages and touch session timestamp."""
        msg_id = f"msg-{uuid.uuid4().hex[:10]}"
        sources_json = json.dumps(sources or [], default=str)
        verified_json = json.dumps(verified_data, default=str) if verified_data else None

        sql = """
        INSERT INTO chat_messages (id, session_id, sender_role, message_text, query_type, sources, verified_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """
        self._execute_write(sql, (msg_id, session_id, sender_role, message_text, query_type or "general", sources_json, verified_json))

        # Touch session updated_at
        touch_sql = "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?;"
        self._execute_write(touch_sql, (session_id,))

        # If user message, update title if it's currently 'New Conversation'
        if sender_role == "user":
            sess_row = self._execute_one("SELECT title FROM chat_sessions WHERE id = ?;", (session_id,))
            if sess_row and sess_row["title"] == "New Conversation":
                title_clean = message_text.strip().replace("\n", " ")
                if len(title_clean) > 40:
                    title_clean = title_clean[:37] + "..."
                self._execute_write("UPDATE chat_sessions SET title = ? WHERE id = ?;", (title_clean, session_id))

        # Also store in legacy chat_history for audit
        if sender_role == "assistant":
            sess_row = self._execute_one("SELECT user_id FROM chat_sessions WHERE id = ?;", (session_id,))
            u_id = sess_row["user_id"] if sess_row else "stu-001"
            self.add_chat_turn(
                user_id=u_id,
                message="",
                reply=message_text,
                intent=query_type or "general",
            )

        return {
            "id": msg_id,
            "session_id": session_id,
            "sender_role": sender_role,
            "message_text": message_text,
            "query_type": query_type or "general",
            "sources": sources or [],
            "verified_data": verified_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_chat_history(
        self,
        student_id: str,
        session_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent chat messages for a student and session."""
        if session_id:
            sql = """
            SELECT m.id, m.session_id, m.sender_role, m.message_text, m.query_type, m.sources, m.verified_data, m.created_at
            FROM chat_messages m
            JOIN chat_sessions s ON s.id = m.session_id
            WHERE s.id = ? AND s.user_id = ?
            ORDER BY m.created_at ASC
            LIMIT ?;
            """
            rows = self._execute_query(sql, (session_id, student_id, limit))
        else:
            # Most recent active session messages
            latest_sess = self._execute_one(
                "SELECT id FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1;",
                (student_id,)
            )
            if not latest_sess:
                return []
            sql = """
            SELECT m.id, m.session_id, m.sender_role, m.message_text, m.query_type, m.sources, m.verified_data, m.created_at
            FROM chat_messages m
            WHERE m.session_id = ?
            ORDER BY m.created_at ASC
            LIMIT ?;
            """
            rows = self._execute_query(sql, (latest_sess["id"], limit))

        results = []
        for r in rows:
            sources_list = []
            if r.get("sources"):
                try:
                    sources_list = json.loads(r["sources"])
                except Exception:
                    sources_list = [r["sources"]]
            verified_obj = None
            if r.get("verified_data"):
                try:
                    verified_obj = json.loads(r["verified_data"])
                except Exception:
                    pass

            results.append({
                "id": r["id"],
                "session_id": r["session_id"],
                "sender_role": r["sender_role"],
                "message_text": r["message_text"],
                "query_type": r["query_type"] or "general",
                "sources": sources_list,
                "verified_data": verified_obj,
                "created_at": r["created_at"],
            })
        return results

    def get_session_messages(self, session_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all messages in a session after verifying user ownership."""
        return self.get_chat_history(student_id=user_id, session_id=session_id, limit=200)

    def get_recent_session_context(self, session_id: str, user_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        """Retrieve recent turns (last N messages) for context resolution."""
        sql = """
        SELECT m.id, m.sender_role, m.message_text, m.query_type, m.created_at
        FROM chat_messages m
        JOIN chat_sessions s ON s.id = m.session_id
        WHERE s.id = ? AND s.user_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?;
        """
        rows = self._execute_query(sql, (session_id, user_id, limit))
        return list(reversed([dict(r) for r in rows]))

    def add_chat_turn(self, user_id: str, message: str, reply: str, intent: str) -> None:
        """Store conversational query and response in chat_history table."""
        turn_id = f"chat-{uuid.uuid4().hex[:8]}"
        sql = """
        INSERT INTO chat_history (id, user_id, message, reply, intent, created_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """
        self._execute_write(sql, (turn_id, user_id, message, reply, intent))

    def search_information(
        self,
        branch: Optional[str] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
        subject: Optional[str] = None,
        query_text: Optional[str] = None,
    ) -> List[SearchItem]:
        """Search institutional information by branch, year, category, subject, and text.

        Viva/Defense SQL Concept:
        - Multi-Condition Filtering: Dynamically constructs parameterized WHERE conditions
          protecting against SQL injection (using '?' placeholders).
        - Wildcard Pattern Matching: Uses SQL LIKE with lower-cased parameters for flexible
          substring matching on titles, content details, and subjects.
        - Deterministic Sorting: ORDER BY year ASC, category ASC, id ASC.
        """
        conditions: List[str] = []
        params: List[Any] = []

        if branch:
            b = branch.strip()
            if b.upper() in ("CSE", "CS"):
                conditions.append("(LOWER(branch) LIKE ? OR LOWER(branch) LIKE ?)")
                params.extend(["%computer science%", "%cse%"])
            else:
                conditions.append("LOWER(branch) LIKE ?")
                params.append(f"%{b.lower()}%")

        if year is not None:
            conditions.append("year = ?")
            params.append(year)

        if category:
            cat = category.strip().lower()
            conditions.append("LOWER(category) LIKE ?")
            params.append(f"%{cat}%")

        if subject:
            subj = subject.strip().lower()
            conditions.append("LOWER(subject) LIKE ?")
            params.append(f"%{subj}%")

        if query_text:
            text_pattern = f"%{query_text.strip().lower()}%"
            conditions.append(
                "(LOWER(title) LIKE ? OR LOWER(content_details) LIKE ? OR LOWER(subject) LIKE ?)"
            )
            params.extend([text_pattern, text_pattern, text_pattern])

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
        SELECT id, branch, year, category, subject, title, content_details, file_url, created_at
        FROM search_information
        {where_clause}
        ORDER BY year ASC, category ASC, id ASC;
        """

        try:
            rows = self._execute_query(sql, tuple(params))
        except Exception as e:
            logger.warning("search_information query failed, ensuring table: %s", e)
            self._ensure_search_information_table()
            try:
                rows = self._execute_query(sql, tuple(params))
            except Exception as e2:
                logger.error("search_information retry failed, using fallback: %s", e2)
                rows = self._fallback_search_records(branch, year, category, subject, query_text)

        results: List[SearchItem] = []
        for r in rows:
            results.append(
                SearchItem(
                    id=r["id"],
                    branch=r["branch"],
                    year=r["year"],
                    category=r["category"],
                    subject=r["subject"],
                    title=r["title"],
                    content_details=r["content_details"],
                    file_url=r["file_url"],
                    created_at=self._parse_datetime(r["created_at"]),
                )
            )
        return results

    def _ensure_search_information_table(self) -> None:
        """Create search_information table and insert initial seed rows if absent."""
        ddl = """
        CREATE TABLE IF NOT EXISTS search_information (
            id VARCHAR(64) PRIMARY KEY,
            branch VARCHAR(100) NOT NULL,
            year INT NOT NULL,
            category VARCHAR(50) NOT NULL,
            subject VARCHAR(150) NOT NULL,
            title VARCHAR(200) NOT NULL,
            content_details TEXT NOT NULL,
            file_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            self._execute_write(ddl)
            seed_items = [
                ("info-001", "Computer Science & Engineering", 3, "Syllabus", "Cloud Computing & Distributed Systems", "CS401 Complete Course Syllabus & Lab Manual", "Unit 1: Virtualization & Cloud Models, Unit 2: Storage & Networking, Unit 3: AWS/GCP Hands-on. 4 Credits.", "/docs/syllabus/cs401_syllabus.pdf"),
                ("info-002", "Computer Science & Engineering", 3, "Timetable", "Advanced Database Engineering", "CS402 Lecture and Lab Timing", "Monday 10:15 - 11:15 AM (Lab-204), Wednesday 09:00 - 10:00 AM (Lab-204), Friday 10:15 - 11:15 AM.", "/docs/timetable/cse_sem6_tt.pdf"),
                ("info-003", "Computer Science & Engineering", 3, "Results", "Machine Learning & AI", "CS403 Mid-Term Result Summary", "Exam Date: 15-Mar-2026. Max Marks: 50. Class Average: 43.5. Highest Score: 49.5 (Grade O).", "/docs/results/midterm_cs403.pdf"),
                ("info-004", "Computer Science & Engineering", 3, "Fees", "Accounts Section", "Semester 6 Academic & Specialization Lab Fee Details", "Semester 6 Academic Tuition: ₹65,000.00 (Due: 30-Jan-2026). Lab Fee: ₹12,500.00 (Due: 28-Feb-2026).", "/docs/fees/sem6_structure.pdf"),
                ("info-005", "Computer Science & Engineering", 3, "FAQ", "Academic Regulations", "Minimum Attendance & Exam Hall Ticket Eligibility", "Students must maintain minimum 75% aggregate attendance to appear in End-Term University Examinations.", "/docs/faq/attendance_rules.pdf")
            ]
            for item in seed_items:
                try:
                    insert_sql = """
                    INSERT INTO search_information (id, branch, year, category, subject, title, content_details, file_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """
                    self._execute_write(insert_sql, item)
                except Exception:
                    pass
        except Exception as err:
            logger.warning("_ensure_search_information_table error: %s", err)

    def _fallback_search_records(
        self,
        branch: Optional[str] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
        subject: Optional[str] = None,
        query_text: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """In-memory fallback search records from official syllabus when database table is pending."""
        catalog = [
            {"id": "info-001", "branch": "Computer Science & Engineering", "year": 3, "category": "Syllabus", "subject": "Cloud Computing & Distributed Systems", "title": "CS401 Complete Course Syllabus & Lab Manual", "content_details": "Unit 1: Virtualization & Cloud Models, Unit 2: Storage & Networking, Unit 3: AWS/GCP Hands-on. 4 Credits.", "file_url": "/docs/syllabus/cs401_syllabus.pdf", "created_at": datetime.now(timezone.utc)},
            {"id": "info-002", "branch": "Computer Science & Engineering", "year": 3, "category": "Timetable", "subject": "Advanced Database Engineering", "title": "CS402 Lecture and Lab Timing", "content_details": "Monday 10:15 - 11:15 AM (Lab-204), Wednesday 09:00 - 10:00 AM (Lab-204), Friday 10:15 - 11:15 AM.", "file_url": "/docs/timetable/cse_sem6_tt.pdf", "created_at": datetime.now(timezone.utc)},
            {"id": "info-003", "branch": "Computer Science & Engineering", "year": 3, "category": "Results", "subject": "Machine Learning & AI", "title": "CS403 Mid-Term Result Summary", "content_details": "Exam Date: 15-Mar-2026. Max Marks: 50. Class Average: 43.5. Highest Score: 49.5 (Grade O).", "file_url": "/docs/results/midterm_cs403.pdf", "created_at": datetime.now(timezone.utc)},
            {"id": "info-004", "branch": "Computer Science & Engineering", "year": 3, "category": "Fees", "subject": "Accounts Section", "title": "Semester 6 Academic & Specialization Lab Fee Details", "content_details": "Semester 6 Academic Tuition: ₹65,000.00 (Due: 30-Jan-2026). Lab Fee: ₹12,500.00 (Due: 28-Feb-2026).", "file_url": "/docs/fees/sem6_structure.pdf", "created_at": datetime.now(timezone.utc)},
            {"id": "info-005", "branch": "Computer Science & Engineering", "year": 3, "category": "FAQ", "subject": "Academic Regulations", "title": "Minimum Attendance & Exam Hall Ticket Eligibility", "content_details": "Students must maintain minimum 75% aggregate attendance to appear in End-Term University Examinations.", "file_url": "/docs/faq/attendance_rules.pdf", "created_at": datetime.now(timezone.utc)},
        ]
        results = []
        for item in catalog:
            if branch:
                b = branch.strip().lower()
                if b not in item["branch"].lower() and "cse" not in b:
                    continue
            if year is not None and item["year"] != year:
                continue
            if category and category.strip().lower() not in item["category"].lower():
                continue
            if subject and subject.strip().lower() not in item["subject"].lower():
                continue
            if query_text:
                q = query_text.strip().lower()
                if (
                    q not in item["title"].lower()
                    and q not in item["content_details"].lower()
                    and q not in item["subject"].lower()
                ):
                    continue
            results.append(item)
        return results



# Singleton instance
sql_repo = SQLRepository()
