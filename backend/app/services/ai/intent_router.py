"""Dual-Source Intent Router for CSIC AI Chatbot.

Classifies student inquiries into structured database queries vs. unstructured
policy document RAG queries vs. general conversational intents.
Guarantees ZERO raw SQL generated or executed by the LLM.
"""
from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status

from backend.app.models.attendance import AttendanceSummary, SubjectAttendance
from backend.app.models.fee import FeeSummary
from backend.app.models.marks import ExamResult, SemesterResult
from backend.app.models.timetable import DailySchedule


class QueryIntent(str, Enum):
    ATTENDANCE = "attendance"
    MARKS = "marks"
    FEES = "fees"
    TIMETABLE = "timetable"
    NOTICES = "notices"
    POLICY_DOCUMENT = "policy_document"
    GENERAL = "general"


# Keywords indicating policy/institutional regulation queries
POLICY_KEYWORDS = [
    "policy",
    "regulations",
    "regulation",
    "code of conduct",
    "handbook",
    "guidelines",
    "rules",
    "rule",
    "medical leave",
    "condonation",
    "detention",
    "detained",
    "passing marks",
    "passing criteria",
    "passing rule",
    "passing percentage",
    "minimum passing",
    "minimum attendance",
    "attendance threshold",
    "75% attendance",
    "attendance rule",
    "attendance criteria",
    "grading criteria",
    "grading system",
    "grading scale",
    "sgpa calculated",
    "cgpa calculated",
    "grade point",
    "letter grade",
    "refund policy",
    "late fee fine",
    "late fee policy",
    "penalty for late",
    "suspension",
    "malpractice",
    "cheating",
    "disciplinary",
    "grievance",
    "appeal",
]

# Keywords indicating structured academic queries
ATTENDANCE_KEYWORDS = [
    "attendance",
    "attended",
    "classes missed",
    "classes did i miss",
    "classes attended",
    "sessions attended",
    "how many classes",
    "classes miss",
    "missed",
    "miss",
    "present",
    "absent",
    "absence",
    "absences",
    "bunk",
    "shortage",
    "at risk",
    "low attendance",
    "percentage in",
]

MARKS_KEYWORDS = [
    "mark",
    "marks",
    "grade",
    "grades",
    "score",
    "scores",
    "result",
    "results",
    "gpa",
    "sgpa",
    "cgpa",
    "exam score",
    "mid-term",
    "internal marks",
    "report card",
]

FEES_KEYWORDS = [
    "fee",
    "fees",
    "invoice",
    "invoices",
    "tuition",
    "due",
    "dues",
    "balance",
    "owe",
    "payment",
    "paid",
    "receipt",
    "pending fee",
    "amount due",
]

TIMETABLE_KEYWORDS = [
    "timetable",
    "schedule",
    "class today",
    "classes today",
    "lecture",
    "lectures",
    "next class",
    "routine",
    "slot",
    "classroom",
    "when is class",
    "daily schedule",
    "weekly timetable",
]

NOTICES_KEYWORDS = [
    "notice",
    "notices",
    "circular",
    "circulars",
    "announcement",
    "announcements",
    "bulletin",
    "broadcast",
    "latest circular",
    "recent circular",
]

GENERAL_KEYWORDS = [
    "hello",
    "hi",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "who are you",
    "what are you",
    "what can you do",
    "help",
    "thanks",
    "thank you",
    "bye",
    "goodbye",
]


class IntentRouter:
    """Classifies user inquiries and safely dispatches structured queries."""

    def classify_intent(self, query: str) -> QueryIntent:
        """Categorize student inquiry into structured, policy, or general intent."""
        query_clean = query.strip().lower()

        # Check for policy/regulations first (e.g. "What is the attendance policy?")
        for kw in POLICY_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.POLICY_DOCUMENT

        # Check structured intents
        for kw in ATTENDANCE_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.ATTENDANCE

        for kw in MARKS_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.MARKS

        for kw in FEES_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.FEES

        for kw in TIMETABLE_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.TIMETABLE

        for kw in NOTICES_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.NOTICES

        # Check general conversational greetings
        for kw in GENERAL_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_clean):
                return QueryIntent.GENERAL

        # Default fallback: Route unclassified queries to policy document RAG.
        return QueryIntent.POLICY_DOCUMENT

    def execute_structured_query(
        self,
        intent: QueryIntent,
        query: str,
        user_id: str,
        user_role: str,
        repo: Any,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Dispatch structured queries to strictly authorized backend repository methods.

        ZERO raw SQL generated or executed. Enforces strict student data isolation.
        """
        self._enforce_student_privacy(query, user_id, user_role, repo)

        if intent == QueryIntent.ATTENDANCE:
            return self._handle_attendance(query, user_id, repo)
        elif intent == QueryIntent.MARKS:
            return self._handle_marks(query, user_id, repo)
        elif intent == QueryIntent.FEES:
            return self._handle_fees(query, user_id, repo)
        elif intent == QueryIntent.TIMETABLE:
            return self._handle_timetable(query, user_id, repo)
        elif intent == QueryIntent.NOTICES:
            return self._handle_notices(query, repo)
        else:
            raise ValueError(f"Intent '{intent}' is not a structured academic intent")

    def _enforce_student_privacy(
        self,
        query: str,
        user_id: str,
        user_role: str,
        repo: Any,
    ) -> None:
        """Prevent Student A from attempting to access Student B's records."""
        if user_role != "student":
            return

        query_lower = query.lower()

        for profile in repo.profiles:
            if profile["role"] == "student" and profile["id"] != user_id:
                other_id = profile["id"].lower()
                other_name = profile["full_name"].lower()
                first_name = other_name.split()[0]

                if other_id in query_lower or other_name in query_lower or (len(first_name) > 3 and first_name in query_lower):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Forbidden: Access denied to other student records. You may only query your own academic data.",
                    )

    def _handle_attendance(
        self,
        query: str,
        user_id: str,
        repo: Any,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve attendance from verified v_student_attendance view."""
        summary = repo.get_student_attendance_summary(user_id)
        if not summary:
            return (
                "No attendance records were found for your student profile.",
                ["Institutional Database (v_student_attendance)"],
                {},
            )

        query_lower = query.lower()
        matched_sub: Optional[SubjectAttendance] = None
        for sub in summary.subjects:
            if sub.subject_code.lower() in query_lower or any(word in sub.subject_name.lower() for word in query_lower.split() if len(word) > 4):
                matched_sub = sub
                break

        if matched_sub:
            status_desc = "⚠️ Below 75% threshold!" if matched_sub.is_low_attendance else "✅ In good standing."
            reply = (
                f"### Verified Attendance: {matched_sub.subject_name} ({matched_sub.subject_code})\n\n"
                f"- **Attendance**: **{matched_sub.attendance_percentage}%** ({status_desc})\n"
                f"- **Sessions Attended**: {matched_sub.attended_sessions} / {matched_sub.total_sessions} conducted\n"
                f"- **Excused Sessions**: {matched_sub.excused_sessions}\n"
                f"- **Absences**: {matched_sub.absent_sessions}"
            )
            return reply, ["Institutional Database (v_student_attendance)"], summary.model_dump()

        risk_text = (
            "⚠️ **Warning**: Your aggregate attendance is below the mandatory 75% threshold. You are at risk of exam debarment."
            if summary.is_at_risk
            else "✅ Your attendance is in good standing (75% or above)."
        )
        sub_lines = []
        for s in summary.subjects:
            flag = "⚠️ Low" if s.is_low_attendance else "✅ OK"
            sub_lines.append(f"- **{s.subject_code} - {s.subject_name}**: {s.attendance_percentage}% ({s.attended_sessions}/{s.total_sessions} sessions) [{flag}]")

        reply = (
            f"### Verified Attendance Summary (Roll No: {summary.roll_number})\n\n"
            f"- **Overall Aggregate**: **{summary.overall_percentage}%**\n"
            f"- **Standing**: {risk_text}\n\n"
            f"**Subject-wise Breakdown**:\n"
            + "\n".join(sub_lines)
        )
        return reply, ["Institutional Database (v_student_attendance)"], summary.model_dump()

    def _handle_marks(
        self,
        query: str,
        user_id: str,
        repo: Any,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve examination results and semester GPAs."""
        exam_results = repo.get_exam_results(user_id)
        semester_results = repo.get_semester_results(user_id)

        if not exam_results and not semester_results:
            return (
                "No examination records or grade cards were found for your student profile.",
                ["Institutional Database (examinations & marks)"],
                {},
            )

        sections = []
        if semester_results:
            sections.append("### Semester Performance")
            for sr in semester_results:
                sections.append(f"- **Semester {sr.semester_number}**: GPA **{sr.gpa}** | Total Credits: {sr.total_credits} | Aggregate: {sr.percentage}%")

        if exam_results:
            sections.append("\n### Examination Results")
            for er in exam_results:
                sections.append(f"#### {er.exam_name} - Aggregate: {er.overall_percentage}% ({er.total_obtained}/{er.total_max})")
                for m in er.subjects:
                    sections.append(f"- **{m.subject_code} - {m.subject_name}**: {m.marks_obtained}/{m.max_marks} (Grade: **{m.grade or 'A'}**)")

        reply = "\n".join(sections)
        verified_data = {
            "semester_results": [sr.model_dump() for sr in semester_results],
            "exam_results": [er.model_dump() for er in exam_results],
        }
        return reply, ["Institutional Database (examinations & marks)"], verified_data

    def _handle_fees(
        self,
        query: str,
        user_id: str,
        repo: Any,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve fee invoices and outstanding balance."""
        summary = repo.get_fee_summary(user_id)
        if not summary:
            return (
                "No fee records or invoices were found for your student profile.",
                ["Institutional Database (fee_invoices)"],
                {},
            )

        is_cleared = summary.total_outstanding <= 0.0
        status_flag = "✅ All tuition invoices are cleared." if is_cleared else f"⚠️ Outstanding balance: **₹{summary.total_outstanding:,.2f}**"
        invoice_lines = []
        for inv in summary.invoices:
            badge = "PAID" if inv.status == "paid" else f"DUE (Due: {inv.due_date})"
            invoice_lines.append(
                f"- **{inv.invoice_number} ({inv.title})**: ₹{inv.amount:,.2f} | Status: **{inv.status.upper()}** [{badge}]"
            )

        reply = (
            f"### Verified Fee & Tuition Account\n\n"
            f"- **Total Invoiced**: ₹{summary.total_invoiced:,.2f}\n"
            f"- **Total Paid**: ₹{summary.total_paid:,.2f}\n"
            f"- **Current Balance Due**: **₹{summary.total_outstanding:,.2f}**\n"
            f"- **Account Status**: {status_flag}\n\n"
            f"**Invoices**:\n" + "\n".join(invoice_lines)
        )
        return reply, ["Institutional Database (fee_invoices)"], summary.model_dump()

    def _handle_timetable(
        self,
        query: str,
        user_id: str,
        repo: Any,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve daily or weekly class schedule."""
        query_lower = query.lower()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        target_day = None

        if "today" in query_lower:
            target_day = datetime.now().strftime("%A")
        else:
            for d in days:
                if d in query_lower:
                    target_day = d.capitalize()
                    break

        schedules = repo.get_student_timetable(user_id, day_of_week=target_day)
        if not schedules:
            return (
                f"No lecture sessions scheduled{' for ' + target_day if target_day else ''}.",
                ["Institutional Database (timetable_entries)"],
                {},
            )

        lines = []
        if target_day:
            lines.append(f"### Verified Schedule for {target_day}")
        else:
            lines.append("### Verified Weekly Schedule")

        for ds in schedules:
            lines.append(f"\n**{ds.day_of_week}**:")
            for slot in ds.entries:
                lines.append(
                    f"- **{slot.start_time} - {slot.end_time}**: {slot.subject_code} - {slot.subject_name} | Room: **{slot.room_number}** | Faculty: {slot.faculty_name}"
                )

        reply = "\n".join(lines)
        verified_data = {"schedules": [ds.model_dump() for ds in schedules]}
        return reply, ["Institutional Database (timetable_entries)"], verified_data

    def _handle_notices(
        self,
        query: str,
        repo: Any,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve published campus circulars."""
        notices = repo.get_notices(target_role="student", limit=5)
        if not notices:
            return (
                "There are no active circulars or announcements posted currently.",
                ["Institutional Database (campus_notices)"],
                {},
            )

        lines = ["### Recent Campus Circulars & Announcements\n"]
        for n in notices:
            lines.append(
                f"- **[{n.category.upper()}] {n.title}** (Published: {n.published_at.strftime('%Y-%m-%d')})\n"
                f"  {n.content}"
            )

        reply = "\n".join(lines)
        verified_data = {"notices": [n.model_dump() for n in notices]}
        return reply, ["Institutional Database (campus_notices)"], verified_data


intent_router = IntentRouter()
