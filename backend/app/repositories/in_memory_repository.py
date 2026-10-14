"""In-memory data repository loaded with synthetic academic dataset.

Implements all view-level metrics and operations corresponding to the
PostgreSQL 3NF schema and the 10 analytical views.
"""
from datetime import date, datetime, timezone
import uuid
from typing import Any, Dict, List, Optional

from backend.app.core.security import verify_password
from backend.app.models.admin import AdminStats, MarksInput, StudentCreate
from backend.app.models.attendance import AttendanceRecord, AttendanceSummary, SubjectAttendance
from backend.app.models.auth import UserProfile
from backend.app.models.fee import FeeInvoice, FeePayment, FeeSummary
from backend.app.models.marks import ExamResult, MarkEntry, SemesterResult
from backend.app.models.notice import NoticeCreate, NoticeItem
from backend.app.models.student import EnrollmentDetail, StudentDetail
from backend.app.models.timetable import DailySchedule, TimetableEntry
from backend.app.repositories.mock_data import (
    ACADEMIC_YEARS,
    ATTENDANCE_RECORDS,
    CLASS_SESSIONS,
    COURSES,
    DEPARTMENTS,
    ENROLLMENTS,
    EXAMINATIONS,
    FACULTY_ASSIGNMENTS,
    FEE_INVOICES,
    FEE_PAYMENTS,
    MARKS,
    NOTICES,
    PROFILES,
    PROGRAMS,
    SEMESTERS,
    SUBJECTS,
    TIMETABLE_ENTRIES,
)


class InMemoryRepository:
    """In-memory repository caching and serving relational student data."""

    def __init__(self) -> None:
        # Load mutable deep copies of seed structures
        self.profiles: List[Dict[str, Any]] = [dict(p) for p in PROFILES]
        self.departments: List[Dict[str, Any]] = [dict(d) for d in DEPARTMENTS]
        self.programs: List[Dict[str, Any]] = [dict(p) for p in PROGRAMS]
        self.courses: List[Dict[str, Any]] = [dict(c) for c in COURSES]
        self.subjects: List[Dict[str, Any]] = [dict(s) for s in SUBJECTS]
        self.faculty_assignments: List[Dict[str, Any]] = [dict(fa) for fa in FACULTY_ASSIGNMENTS]
        self.enrollments: List[Dict[str, Any]] = [dict(e) for e in ENROLLMENTS]
        self.class_sessions: List[Dict[str, Any]] = [dict(cs) for cs in CLASS_SESSIONS]
        self.attendance_records: List[Dict[str, Any]] = [dict(ar) for ar in ATTENDANCE_RECORDS]
        self.examinations: List[Dict[str, Any]] = [dict(ex) for ex in EXAMINATIONS]
        self.marks: List[Dict[str, Any]] = [dict(m) for m in MARKS]
        self.fee_invoices: List[Dict[str, Any]] = [dict(fi) for fi in FEE_INVOICES]
        self.fee_payments: List[Dict[str, Any]] = [dict(fp) for fp in FEE_PAYMENTS]
        self.timetable_entries: List[Dict[str, Any]] = [dict(te) for te in TIMETABLE_ENTRIES]
        self.notices: List[Dict[str, Any]] = [dict(n) for n in NOTICES]
        self.chat_sessions: List[Dict[str, Any]] = []
        self.chat_messages: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # Authentication & User Profiles
    # -------------------------------------------------------------
    def authenticate_user(self, email: str, password: str) -> Optional[UserProfile]:
        """Authenticate user by email and cleartext password."""
        email_clean = email.strip().lower()
        user_record = next(
            (p for p in self.profiles if p["email"].lower() == email_clean),
            None,
        )
        if not user_record:
            return None

        # Verify password directly or through bcrypt
        stored_pwd = user_record.get("password", "")
        if stored_pwd == password or verify_password(password, stored_pwd):
            return UserProfile(
                id=user_record["id"],
                email=user_record["email"],
                role=user_record["role"],
                full_name=user_record["full_name"],
                phone=user_record.get("phone"),
                avatar_url=user_record.get("avatar_url"),
                is_active=user_record.get("is_active", True),
                created_at=user_record.get("created_at"),
                updated_at=user_record.get("updated_at"),
            )
        return None

    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile by ID."""
        user = next((p for p in self.profiles if p["id"] == user_id), None)
        if not user:
            return None
        return UserProfile(
            id=user["id"],
            email=user["email"],
            role=user["role"],
            full_name=user["full_name"],
            phone=user.get("phone"),
            avatar_url=user.get("avatar_url"),
            is_active=user.get("is_active", True),
            created_at=user.get("created_at"),
            updated_at=user.get("updated_at"),
        )

    # -------------------------------------------------------------
    # Student & Enrollment Management
    # -------------------------------------------------------------
    def get_student_detail(self, student_id: str) -> Optional[StudentDetail]:
        """Get student details with active enrollments."""
        user = next((p for p in self.profiles if p["id"] == student_id and p["role"] == "student"), None)
        if not user:
            return None

        student_enrollments = [
            EnrollmentDetail(
                id=e["id"],
                student_id=e["student_id"],
                course_id=e["course_id"],
                roll_number=e["roll_number"],
                enrollment_date=e["enrollment_date"],
                status=e["status"],
                program_code=e["program_code"],
                program_name=e["program_name"],
                semester_number=e["semester_number"],
                section=e["section"],
            )
            for e in self.enrollments
            if e["student_id"] == student_id
        ]

        return StudentDetail(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user.get("phone"),
            avatar_url=user.get("avatar_url"),
            role=user["role"],
            department_name="Computer Science & Engineering",
            enrollments=student_enrollments,
        )

    def list_students(self) -> List[StudentDetail]:
        """List all registered students in the system."""
        students: List[StudentDetail] = []
        for p in self.profiles:
            if p["role"] == "student":
                det = self.get_student_detail(p["id"])
                if det:
                    students.append(det)
        return students

    # -------------------------------------------------------------
    # Attendance Engine & Reporting Views
    # -------------------------------------------------------------
    def get_student_attendance_summary(self, student_id: str) -> Optional[AttendanceSummary]:
        """Calculate subject-wise and overall attendance percentage (v_student_attendance)."""
        enr = next((e for e in self.enrollments if e["student_id"] == student_id), None)
        if not enr:
            return None

        enrollment_id = enr["id"]
        roll_number = enr["roll_number"]

        # Map sessions to subjects
        fa_map = {fa["id"]: fa["subject_id"] for fa in self.faculty_assignments}
        sub_map = {s["id"]: s for s in self.subjects}
        sess_map = {cs["id"]: cs for cs in self.class_sessions if cs["status"] == "conducted"}

        # Collect attendance per subject
        stats_by_sub: Dict[str, Dict[str, Any]] = {
            s["id"]: {
                "code": s["code"],
                "name": s["name"],
                "total": 0,
                "attended": 0,
                "excused": 0,
                "absent": 0,
            }
            for s in self.subjects
        }

        for ar in self.attendance_records:
            if ar["enrollment_id"] != enrollment_id:
                continue
            sess = sess_map.get(ar["session_id"])
            if not sess:
                continue
            sub_id = fa_map.get(sess["faculty_assignment_id"])
            if not sub_id or sub_id not in stats_by_sub:
                continue

            stats_by_sub[sub_id]["total"] += 1
            if ar["status"] == "present":
                stats_by_sub[sub_id]["attended"] += 1
            elif ar["status"] == "excused":
                stats_by_sub[sub_id]["excused"] += 1
            elif ar["status"] == "absent":
                stats_by_sub[sub_id]["absent"] += 1

        subject_attendances: List[SubjectAttendance] = []
        total_conducted = 0
        total_attended_or_excused = 0

        for sub_id, stat in stats_by_sub.items():
            tot = stat["total"]
            att = stat["attended"]
            exc = stat["excused"]
            ab = stat["absent"]

            pct = round(((att + exc) * 100.0) / max(tot, 1), 2) if tot > 0 else 100.0
            is_low = pct < 75.0

            total_conducted += tot
            total_attended_or_excused += (att + exc)

            subject_attendances.append(
                SubjectAttendance(
                    subject_code=stat["code"],
                    subject_name=stat["name"],
                    total_sessions=tot,
                    attended_sessions=att,
                    excused_sessions=exc,
                    absent_sessions=ab,
                    attendance_percentage=pct,
                    is_low_attendance=is_low,
                )
            )

        overall_pct = (
            round((total_attended_or_excused * 100.0) / max(total_conducted, 1), 2)
            if total_conducted > 0
            else 100.0
        )

        return AttendanceSummary(
            student_id=student_id,
            roll_number=roll_number,
            overall_percentage=overall_pct,
            is_at_risk=(overall_pct < 75.0),
            subjects=subject_attendances,
        )

    def get_attendance_records_for_student(self, student_id: str) -> List[AttendanceRecord]:
        """Fetch granular attendance logs for a student."""
        enr = next((e for e in self.enrollments if e["student_id"] == student_id), None)
        if not enr:
            return []

        enrollment_id = enr["id"]
        fa_map = {fa["id"]: fa["subject_id"] for fa in self.faculty_assignments}
        sub_map = {s["id"]: s for s in self.subjects}
        sess_map = {cs["id"]: cs for cs in self.class_sessions}

        records: List[AttendanceRecord] = []
        for ar in self.attendance_records:
            if ar["enrollment_id"] != enrollment_id:
                continue
            sess = sess_map.get(ar["session_id"])
            if not sess:
                continue
            sub_id = fa_map.get(sess["faculty_assignment_id"])
            subject = sub_map.get(sub_id, {"code": "GEN", "name": "General"})

            records.append(
                AttendanceRecord(
                    id=ar["id"],
                    session_id=ar["session_id"],
                    enrollment_id=ar["enrollment_id"],
                    status=ar["status"],
                    remarks=ar.get("remarks"),
                    marked_at=ar["marked_at"],
                    session_date=sess["session_date"],
                    topic=sess.get("topic"),
                    subject_code=subject["code"],
                    subject_name=subject["name"],
                )
            )

        records.sort(key=lambda r: r.session_date, reverse=True)
        return records

    def get_low_attendance_warnings(self) -> List[Dict[str, Any]]:
        """Implementation of view `v_low_attendance_warnings` (< 75.0% threshold)."""
        warnings = []
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

    # -------------------------------------------------------------
    # Examinations & Academic Marks
    # -------------------------------------------------------------
    def get_exam_results(self, student_id: str) -> List[ExamResult]:
        """Get examination performance grouped by exam cycle."""
        enr = next((e for e in self.enrollments if e["student_id"] == student_id), None)
        if not enr:
            return []

        enrollment_id = enr["id"]
        sub_map = {s["id"]: s for s in self.subjects}
        exam_map = {ex["id"]: ex for ex in self.examinations}

        # Group marks by examination
        marks_by_exam: Dict[str, List[MarkEntry]] = {}
        for m in self.marks:
            if m["enrollment_id"] != enrollment_id:
                continue
            ex = exam_map.get(m["examination_id"])
            if not ex:
                continue
            subject = sub_map.get(ex["subject_id"], {"code": "GEN", "name": "General"})
            obtained = float(m["marks_obtained"])
            max_m = float(ex["max_marks"])
            pct = round((obtained * 100.0) / max_m, 2) if max_m > 0 else 0.0

            entry = MarkEntry(
                id=m["id"],
                examination_id=m["examination_id"],
                exam_name=ex["name"],
                subject_code=subject["code"],
                subject_name=subject["name"],
                marks_obtained=obtained,
                max_marks=max_m,
                percentage=pct,
                grade=m.get("grade", "A"),
                is_absent=m.get("is_absent", False),
                exam_date=ex["exam_date"],
            )
            exam_name = ex["name"]
            marks_by_exam.setdefault(exam_name, []).append(entry)

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
        """Implementation of view `v_semester_result_summary`."""
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

    # -------------------------------------------------------------
    # Fee Management & Invoices
    # -------------------------------------------------------------
    def get_fee_summary(self, student_id: str) -> Optional[FeeSummary]:
        """Implementation of view `v_fee_outstanding_summary`."""
        enr = next((e for e in self.enrollments if e["student_id"] == student_id), None)
        if not enr:
            return None

        enrollment_id = enr["id"]
        invoices: List[FeeInvoice] = []
        total_invoiced = 0.0
        total_paid = 0.0

        for inv in self.fee_invoices:
            if inv["enrollment_id"] != enrollment_id:
                continue
            inv_id = inv["id"]
            amount = float(inv["amount"])
            total_invoiced += amount

            # Match payments
            payments = [
                FeePayment(
                    id=p["id"],
                    invoice_id=p["invoice_id"],
                    transaction_reference=p["transaction_reference"],
                    amount_paid=float(p["amount_paid"]),
                    payment_date=p["payment_date"],
                    payment_method=p["payment_method"],
                    status=p["status"],
                )
                for p in self.fee_payments
                if p["invoice_id"] == inv_id and p["status"] == "success"
            ]
            paid_for_inv = sum(p.amount_paid for p in payments)
            total_paid += paid_for_inv

            # Determine invoice status
            st = "unpaid"
            if paid_for_inv >= amount:
                st = "paid"
            elif paid_for_inv > 0:
                st = "partially_paid"

            invoices.append(
                FeeInvoice(
                    id=inv["id"],
                    invoice_number=inv["invoice_number"],
                    enrollment_id=inv["enrollment_id"],
                    title=inv["title"],
                    amount=amount,
                    due_date=inv["due_date"],
                    status=st,
                    created_at=inv["created_at"],
                    payments=payments,
                )
            )

        total_outstanding = max(0.0, total_invoiced - total_paid)

        return FeeSummary(
            student_id=student_id,
            total_invoiced=round(total_invoiced, 2),
            total_paid=round(total_paid, 2),
            total_outstanding=round(total_outstanding, 2),
            invoices=invoices,
        )

    def record_fee_payment(
        self,
        invoice_id: str,
        amount_paid: float,
        payment_method: str = "upi",
    ) -> Optional[FeePayment]:
        """Process and record an online fee installment payment."""
        inv = next((i for i in self.fee_invoices if i["id"] == invoice_id), None)
        if not inv:
            return None

        payment_id = f"pay-{uuid.uuid4().hex[:8]}"
        txn_ref = f"TXN_{payment_method.upper()}_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)

        payment_record = {
            "id": payment_id,
            "invoice_id": invoice_id,
            "transaction_reference": txn_ref,
            "amount_paid": amount_paid,
            "payment_date": now,
            "payment_method": payment_method,
            "status": "success",
        }
        self.fee_payments.append(payment_record)

        # Update invoice status
        existing_paid = sum(
            p["amount_paid"]
            for p in self.fee_payments
            if p["invoice_id"] == invoice_id and p["status"] == "success"
        )
        if existing_paid >= inv["amount"]:
            inv["status"] = "paid"
        else:
            inv["status"] = "partially_paid"

        return FeePayment(
            id=payment_id,
            invoice_id=invoice_id,
            transaction_reference=txn_ref,
            amount_paid=amount_paid,
            payment_date=now,
            payment_method=payment_method,
            status="success",
        )

    # -------------------------------------------------------------
    # Timetable & Scheduling
    # -------------------------------------------------------------
    def get_student_timetable(
        self,
        student_id: str,
        day_of_week: Optional[str] = None,
    ) -> List[DailySchedule]:
        """Fetch weekly lecture schedules for enrolled courses."""
        fa_map = {fa["id"]: fa for fa in self.faculty_assignments}
        sub_map = {s["id"]: s for s in self.subjects}
        prof_map = {p["id"]: p["full_name"] for p in self.profiles}

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if day_of_week and day_of_week in days:
            days = [day_of_week]

        schedule: List[DailySchedule] = []
        for day in days:
            entries: List[TimetableEntry] = []
            for te in self.timetable_entries:
                if te["day_of_week"] != day:
                    continue
                fa = fa_map.get(te["faculty_assignment_id"])
                if not fa:
                    continue
                sub = sub_map.get(fa["subject_id"], {"code": "GEN", "name": "General"})
                fac_name = prof_map.get(fa["faculty_id"], "Faculty Instructor")

                entries.append(
                    TimetableEntry(
                        id=te["id"],
                        day_of_week=day,
                        start_time=te["start_time"],
                        end_time=te["end_time"],
                        room_number=te["room_number"],
                        subject_code=sub["code"],
                        subject_name=sub["name"],
                        faculty_name=fac_name,
                    )
                )
            entries.sort(key=lambda x: x.start_time)
            schedule.append(DailySchedule(day_of_week=day, entries=entries))

        return schedule

    # -------------------------------------------------------------
    # Notices & Broadcasts
    # -------------------------------------------------------------
    def get_notices(
        self,
        target_role: Optional[str] = None,
        limit: int = 50,
    ) -> List[NoticeItem]:
        """List published institutional notices filtered by audience role."""
        prof_map = {p["id"]: p["full_name"] for p in self.profiles}
        items: List[NoticeItem] = []

        for n in self.notices:
            if not n.get("is_published", True):
                continue
            if target_role and target_role != "admin":
                if n.get("target_role") not in ("all", target_role):
                    continue
            items.append(
                NoticeItem(
                    id=n["id"],
                    title=n["title"],
                    category=n["category"],
                    content=n["content"],
                    published_by_name=prof_map.get(n.get("published_by"), "Dean of Academics"),
                    is_published=n.get("is_published", True),
                    target_role=n.get("target_role", "all"),
                    published_at=n["published_at"],
                )
            )

        items.sort(key=lambda x: x.published_at, reverse=True)
        return items[:limit]

    def create_notice(
        self,
        notice: NoticeCreate,
        publisher_id: str,
    ) -> NoticeItem:
        """Create and publish a new campus circular."""
        new_id = f"not-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        record = {
            "id": new_id,
            "title": notice.title,
            "category": notice.category,
            "content": notice.content,
            "published_by": publisher_id,
            "is_published": notice.is_published,
            "target_role": notice.target_role,
            "published_at": now,
        }
        self.notices.insert(0, record)

        publisher = self.get_user_by_id(publisher_id)
        pub_name = publisher.full_name if publisher else "Administrator"

        return NoticeItem(
            id=new_id,
            title=notice.title,
            category=notice.category,
            content=notice.content,
            published_by_name=pub_name,
            is_published=notice.is_published,
            target_role=notice.target_role,
            published_at=now,
        )

    # -------------------------------------------------------------
    # Administrative Actions & Analytics
    # -------------------------------------------------------------
    def get_admin_stats(self) -> AdminStats:
        """Compute system-wide dashboard administrative statistics."""
        total_students = sum(1 for p in self.profiles if p["role"] == "student")
        total_faculty = sum(1 for p in self.profiles if p["role"] == "faculty")
        total_courses = len(self.courses)
        total_notices = len(self.notices)

        # Average attendance across all students
        percentages = [
            summary.overall_percentage
            for s in self.list_students()
            if (summary := self.get_student_attendance_summary(s.id)) is not None
        ]
        avg_att = round(sum(percentages) / max(len(percentages), 1), 2)

        # Total pending fees
        total_invoiced = sum(i["amount"] for i in self.fee_invoices)
        total_paid = sum(
            p["amount_paid"] for p in self.fee_payments if p["status"] == "success"
        )
        pending_fees = round(max(0.0, total_invoiced - total_paid), 2)

        return AdminStats(
            total_students=total_students,
            total_faculty=total_faculty,
            total_courses=total_courses,
            total_notices=total_notices,
            average_attendance=avg_att,
            pending_fees_amount=pending_fees,
        )

    def create_student(self, student_in: StudentCreate) -> StudentDetail:
        """Register a new student and create enrollment in Course Section."""
        new_id = f"stu-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        # Create Profile
        profile_record = {
            "id": new_id,
            "email": student_in.email,
            "password": student_in.password,
            "role": "student",
            "full_name": student_in.full_name,
            "phone": student_in.phone,
            "avatar_url": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        self.profiles.append(profile_record)

        # Create Enrollment
        enr_id = f"enr-{uuid.uuid4().hex[:8]}"
        enrollment_record = {
            "id": enr_id,
            "student_id": new_id,
            "course_id": "crs-01",
            "roll_number": student_in.roll_number,
            "enrollment_date": now.date(),
            "status": "active",
            "program_code": student_in.program_code,
            "program_name": "B.Tech Computer Science & Engineering",
            "semester_number": student_in.semester_number,
            "section": student_in.section,
        }
        self.enrollments.append(enrollment_record)

        # Return full detail
        return self.get_student_detail(new_id)  # type: ignore

    def enter_marks(self, marks_in: MarksInput, entered_by_id: str) -> MarkEntry:
        """Record or update student examination score."""
        ex = next((e for e in self.examinations if e["id"] == marks_in.examination_id), None)
        if not ex:
            # Create a mock examination if not existing
            ex = {
                "id": marks_in.examination_id,
                "name": "Class Assessment",
                "max_marks": 50.0,
                "exam_date": date.today(),
                "subject_id": "sub-01",
            }
            self.examinations.append(ex)

        sub = next((s for s in self.subjects if s["id"] == ex.get("subject_id")), {"code": "CS401", "name": "Subject"})

        mark_id = f"mark-{uuid.uuid4().hex[:8]}"
        mark_rec = {
            "id": mark_id,
            "examination_id": marks_in.examination_id,
            "enrollment_id": marks_in.enrollment_id,
            "marks_obtained": marks_in.marks_obtained,
            "is_absent": marks_in.is_absent,
            "grade": marks_in.grade or "A",
            "entered_by": entered_by_id,
        }
        self.marks.append(mark_rec)

        pct = round((marks_in.marks_obtained * 100.0) / max(float(ex["max_marks"]), 1), 2)

        return MarkEntry(
            id=mark_id,
            examination_id=marks_in.examination_id,
            exam_name=ex["name"],
            subject_code=sub["code"],
            subject_name=sub["name"],
            marks_obtained=marks_in.marks_obtained,
            max_marks=float(ex["max_marks"]),
            percentage=pct,
            grade=marks_in.grade or "A",
            is_absent=marks_in.is_absent,
            exam_date=ex["exam_date"],
        )

    # -------------------------------------------------------------
    # AI Chatbot History & Sessions
    # -------------------------------------------------------------
    def get_or_create_chat_session(self, student_id: str, session_id: Optional[str] = None) -> str:
        """Retrieve existing session ID for student or create a new one."""
        if session_id:
            existing = next((s for s in self.chat_sessions if s["id"] == session_id and s["student_id"] == student_id), None)
            if existing:
                return existing["id"]

        new_id = f"sess-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        self.chat_sessions.append({
            "id": new_id,
            "student_id": student_id,
            "title": "New Conversation",
            "created_at": now,
            "updated_at": now,
        })
        return new_id

    def add_chat_message(
        self,
        session_id: str,
        sender_role: str,
        message_text: str,
        query_type: Optional[str] = None,
        sources: Optional[List[str]] = None,
        verified_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record conversational turn into chat message storage."""
        msg_id = f"msg-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        msg_record = {
            "id": msg_id,
            "session_id": session_id,
            "sender_role": sender_role,
            "message_text": message_text,
            "query_type": query_type or "general",
            "sources": sources or [],
            "verified_data": verified_data,
            "created_at": now,
        }
        self.chat_messages.append(msg_record)
        return msg_record

    def get_chat_history(
        self,
        student_id: str,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve historical chat turns for an authenticated student."""
        valid_session_ids = {s["id"] for s in self.chat_sessions if s["student_id"] == student_id}
        if session_id:
            if session_id in valid_session_ids:
                return [m for m in self.chat_messages if m["session_id"] == session_id]
            return []

        return [m for m in self.chat_messages if m["session_id"] in valid_session_ids]


# Global singleton instance of repository
in_memory_repo = InMemoryRepository()
