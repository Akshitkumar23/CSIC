"""Dual-Source Intent Router for CSIC AI Chatbot.

Classifies student inquiries into structured database queries vs. unstructured
policy document RAG queries vs. general conversational intents.
Guarantees ZERO raw SQL generated or executed by the LLM.
"""
from datetime import datetime, timezone
from enum import Enum
import math
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

    def resolve_context_and_intent(
        self,
        query: str,
        recent_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[QueryIntent, Dict[str, Any]]:
        """Resolve query intent taking conversational memory and follow-up context into account."""
        query_clean = query.strip()
        query_lower = query_clean.lower()
        context_data: Dict[str, Any] = {}

        # 1. Extract potential subject code from query (e.g., CS401, CS-401, CS 401, CS402, etc.)
        subject_match = re.search(r"\b(CS\s*[-]?\s*\d{3})\b", query_clean, re.IGNORECASE)
        target_subject = subject_match.group(1).replace(" ", "").replace("-", "").upper() if subject_match else None
        if target_subject:
            context_data["target_subject"] = target_subject

        # 2. Extract potential examination name
        if "mid-term" in query_lower or "mid term" in query_lower or "internal" in query_lower:
            context_data["target_exam"] = "Mid-Term Examination"

        # 3. Check for follow-up indicators
        is_follow_up = bool(
            re.search(
                r"\b(what about|how about|why|how many classes|how many to reach|how to recover|can i recover|how to improve|when is it due|what if i pay late|can i get medical leave|recover attendance|attendance shortage)\b",
                query_lower,
            )
            or (target_subject and len(query_clean.split()) <= 4)
        )

        # 4. If follow up and we have recent turns, inspect previous turns
        previous_intent = None
        previous_subject = None
        if recent_history:
            # Look backwards for the most recent structured intent
            for turn in reversed(recent_history):
                q_type = turn.get("query_type")
                if q_type and q_type in [i.value for i in QueryIntent]:
                    previous_intent = QueryIntent(q_type)
                    break
            # Look for mentioned subjects in prior turns
            for turn in reversed(recent_history):
                txt = turn.get("message_text", "")
                prev_sub = re.search(r"\b(CS\s*[-]?\s*\d{3})\b", txt, re.IGNORECASE)
                if prev_sub:
                    previous_subject = prev_sub.group(1).replace(" ", "").replace("-", "").upper()
                    break

        if target_subject is None and previous_subject:
            context_data["target_subject"] = previous_subject

        # 5. Local Statistical NLP Pipeline Classification
        from backend.app.services.ai.nlp.classifier import classifier_instance
        pred = classifier_instance.classify(query_clean)

        # Merge extracted entities
        if pred.entities.get("subject") and not context_data.get("target_subject"):
            context_data["target_subject"] = pred.entities["subject"]
        if pred.entities.get("exam"):
            context_data["target_exam"] = pred.entities["exam"]
        if pred.entities.get("day"):
            context_data["target_day"] = pred.entities["day"]
        if pred.entities.get("target"):
            context_data["target_percentage"] = pred.entities["target"]
        context_data["is_hinglish"] = pred.is_hinglish

        # Policy priority keywords check
        for kw in POLICY_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", query_lower):
                return QueryIntent.POLICY_DOCUMENT, context_data

        # Follow-up inheritance
        if (is_follow_up or pred.intent == "follow_up") and previous_intent:
            if previous_intent in (QueryIntent.ATTENDANCE, QueryIntent.MARKS, QueryIntent.FEES, QueryIntent.TIMETABLE):
                return previous_intent, context_data

        # Map classified intent
        if pred.intent in ("attendance_lookup", "attendance_advice", "academic_calculation"):
            return QueryIntent.ATTENDANCE, context_data
        elif pred.intent == "marks_explanation":
            return QueryIntent.MARKS, context_data
        elif pred.intent == "fee_status":
            return QueryIntent.FEES, context_data
        elif pred.intent == "timetable":
            return QueryIntent.TIMETABLE, context_data
        elif pred.intent == "notices":
            return QueryIntent.NOTICES, context_data
        elif pred.intent == "greeting":
            return QueryIntent.GENERAL, context_data
        elif pred.intent == "policy_lookup":
            return QueryIntent.POLICY_DOCUMENT, context_data
        elif context_data.get("target_subject"):
            return QueryIntent.ATTENDANCE, context_data

        return QueryIntent.POLICY_DOCUMENT, context_data

    def classify_intent(self, query: str) -> QueryIntent:
        """Categorize student inquiry into structured, policy, or general intent (backward compatible)."""
        intent, _ = self.resolve_context_and_intent(query)
        return intent

    def execute_structured_query(
        self,
        intent: QueryIntent,
        query: str,
        user_id: str,
        user_role: str,
        repo: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Dispatch structured queries to strictly authorized backend repository methods.

        ZERO raw SQL generated or executed. Enforces strict student data isolation.
        """
        self._enforce_student_privacy(query, user_id, user_role, repo)

        ctx = context or {}
        if intent == QueryIntent.ATTENDANCE:
            return self._handle_attendance(query, user_id, repo, ctx)
        elif intent == QueryIntent.MARKS:
            return self._handle_marks(query, user_id, repo, ctx)
        elif intent == QueryIntent.FEES:
            return self._handle_fees(query, user_id, repo, ctx)
        elif intent == QueryIntent.TIMETABLE:
            return self._handle_timetable(query, user_id, repo, ctx)
        elif intent == QueryIntent.NOTICES:
            return self._handle_notices(query, repo, ctx)
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
                        detail="Forbidden: Access denied to other student records. You may only query your own academic data.",
                    )

    def _handle_attendance(
        self,
        query: str,
        user_id: str,
        repo: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve attendance from verified v_student_attendance view with recovery calculation."""
        summary = repo.get_student_attendance_summary(user_id)
        if not summary:
            return (
                "No attendance records were found for your student profile.",
                ["Institutional Database (v_student_attendance)"],
                {},
            )

        query_lower = query.lower()
        target_subject = (context or {}).get("target_subject")
        matched_sub: Optional[SubjectAttendance] = None

        for sub in summary.subjects:
            if target_subject and sub.subject_code.upper() == target_subject.upper():
                matched_sub = sub
                break
            if sub.subject_code.lower() in query_lower or any(word in sub.subject_name.lower() for word in query_lower.split() if len(word) > 4):
                matched_sub = sub
                break

        if matched_sub:
            total = matched_sub.total_sessions
            attended = matched_sub.attended_sessions
            excused = matched_sub.excused_sessions
            effective_attended = attended + excused
            pct = matched_sub.attendance_percentage

            if matched_sub.is_low_attendance:
                classes_needed = math.ceil((0.75 * total - effective_attended) / 0.25)
                if classes_needed < 1:
                    classes_needed = 1
                status_header = "⚠️ **ATTENDANCE WARNING: BELOW MANDATORY 75% THRESHOLD**"
                why_matters = (
                    "**Why this matters:** Under University Academic Regulations (Section 4.1), "
                    "a minimum of 75.0% attendance in each registered course is mandatory to be eligible for End-Semester Examinations. "
                    "Falling below 75% results in examination debarment unless an authorized medical condonation (up to 10%) is formally granted by the Dean."
                )
                action_plan = (
                    f"**Action Plan & Recovery Calculation:**\n"
                    f"- Current deficit: You have attended **{attended} of {total}** conducted sessions"
                    + (f" (**+{excused}** approved excused absences)" if excused > 0 else "")
                    + f" (**{pct}%**).\n"
                    f"- **Recovery Requirement:** You must attend the next **{classes_needed} consecutive classes** without missing any session to recover your attendance back to 75.0%.\n"
                    f"- *Caution:* Missing even 1 additional class will increase the recovery requirement by 4 classes."
                )
            else:
                buffer_classes = math.floor((effective_attended - 0.75 * total) / 0.75) if (effective_attended - 0.75 * total) > 0 else 0
                status_header = "✅ **ATTENDANCE STANDING: GOOD**"
                why_matters = (
                    "**Why this matters:** Your attendance meets the university's 75% requirement. You are eligible for regular exam hall-ticket issuance."
                )
                action_plan = (
                    f"**Current Status:**\n"
                    f"- Attended: **{attended} of {total}** conducted sessions"
                    + (f" (**+{excused}** approved excused absences)" if excused > 0 else "")
                    + f" (**{pct}%**).\n"
                    f"- Safety Margin: You can miss at most **{buffer_classes} class{'es' if buffer_classes != 1 else ''}** while still remaining at or above the 75% boundary."
                )

            reply = (
                f"### {status_header}\n\n"
                f"**Course:** {matched_sub.subject_code} - {matched_sub.subject_name}\n"
                f"- **Attendance:** **{pct}%** ({attended}/{total} sessions attended, {matched_sub.absent_sessions} absences, {matched_sub.excused_sessions} excused)\n\n"
                f"{why_matters}\n\n"
                f"{action_plan}\n\n"
                f"👉 **[View Full Subject Attendance Breakdown](/attendance)**"
            )
            return reply, ["Institutional Database (v_student_attendance)", "University Regulations (Section 4.1)"], summary.model_dump()

        # Aggregate Summary
        if summary.is_at_risk:
            risk_header = "⚠️ **ATTENDANCE WARNING: AGGREGATE SHORTAGE DETECTED**"
            risk_text = (
                "**Why this matters:** Your aggregate attendance is below the mandatory 75% threshold. "
                "Students with aggregate attendance below 75% are ineligible to receive examination admit cards without formal condonation."
            )
        else:
            risk_header = "✅ **ATTENDANCE STANDING: SATISFACTORY**"
            risk_text = (
                "**Why this matters:** Your overall aggregate attendance satisfies institutional eligibility rules (>= 75.0%)."
            )

        sub_lines = []
        low_subjects = []
        for s in summary.subjects:
            effective_s_att = s.attended_sessions + s.excused_sessions
            if s.is_low_attendance:
                req = math.ceil((0.75 * s.total_sessions - effective_s_att) / 0.25)
                sub_lines.append(f"- ⚠️ **{s.subject_code} - {s.subject_name}**: **{s.attendance_percentage}%** ({s.attended_sessions}/{s.total_sessions} classes) — *Need {max(1, req)} consecutive classes to recover*")
                low_subjects.append(s.subject_code)
            else:
                sub_lines.append(f"- ✅ **{s.subject_code} - {s.subject_name}**: **{s.attendance_percentage}%** ({s.attended_sessions}/{s.total_sessions} classes)")

        reply = (
            f"### {risk_header} (Roll No: {summary.roll_number})\n\n"
            f"- **Overall Aggregate Attendance**: **{summary.overall_percentage}%**\n\n"
            f"{risk_text}\n\n"
            f"**Subject-wise Breakdown**:\n"
            + "\n".join(sub_lines)
            + "\n\n"
        )

        if low_subjects:
            reply += (
                f"💡 **Recommended Next Step:** Focus immediately on classes in {', '.join(low_subjects)}. "
                "If you missed classes due to hospitalization or official college representation, submit a medical condonation request.\n\n"
            )

        reply += "👉 **[Open Complete Attendance Portal](/attendance)**"
        return reply, ["Institutional Database (v_student_attendance)", "University Regulations (Section 4.1)"], summary.model_dump()

    def _handle_marks(
        self,
        query: str,
        user_id: str,
        repo: Any,
        context: Optional[Dict[str, Any]] = None,
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

        sections = ["### 📊 Verified Examination & Academic Performance\n"]
        if semester_results:
            sections.append("#### Semester Performance Summary")
            for sr in semester_results:
                sections.append(f"- **Semester {sr.semester_number}**: GPA **{sr.gpa}** | Total Credits: {sr.total_credits} | Aggregate: **{sr.percentage}%**")
            sections.append("")

        if exam_results:
            sections.append("#### Examination Breakdown")
            for er in exam_results:
                sections.append(f"**{er.exam_name}** (Aggregate: **{er.overall_percentage}%** — {er.total_obtained}/{er.total_max} marks):")
                for m in er.subjects:
                    status_emoji = "✅" if m.marks_obtained >= (m.max_marks * 0.4) else "⚠️"
                    sections.append(f"- {status_emoji} **{m.subject_code} - {m.subject_name}**: **{m.marks_obtained}**/{m.max_marks} (Grade: **{m.grade or 'A'}**)")
                sections.append("")

        sections.append(
            "**Why this matters:** Under Examination Regulations (Section 5.3), a minimum of 40% in internal assessments "
            "and 50% semester aggregate is required for course clearance without backlogs.\n\n"
            "👉 **[Open Marks & Grade Cards](/marks)**"
        )

        reply = "\n".join(sections)
        verified_data = {
            "semester_results": [sr.model_dump() for sr in semester_results],
            "exam_results": [er.model_dump() for er in exam_results],
        }
        return reply, ["Institutional Database (examinations & marks)", "Examination Code (Section 5.3)"], verified_data

    def _handle_fees(
        self,
        query: str,
        user_id: str,
        repo: Any,
        context: Optional[Dict[str, Any]] = None,
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
        status_flag = "✅ **Account Cleared:** No outstanding fee dues." if is_cleared else f"⚠️ **Payment Required:** Outstanding balance of **₹{summary.total_outstanding:,.2f}**"
        invoice_lines = []
        for inv in summary.invoices:
            badge = "PAID" if inv.status == "paid" else f"DUE (Due: {inv.due_date})"
            invoice_lines.append(
                f"- **{inv.invoice_number} ({inv.title})**: ₹{inv.amount:,.2f} | Status: **{inv.status.upper()}** [{badge}]"
            )

        why_matters = (
            "**Why this matters:** Under College Fee Regulations (Section 2.4), invoices must be paid within 15 days of the due date. "
            "A late surcharge of ₹500 is assessed after the due date, and uncleared dues will temporarily withhold semester admit card generation."
            if not is_cleared
            else "**Why this matters:** Your tuition fee account is in good standing. You are cleared for course registration and hall ticket release."
        )

        reply = (
            f"### 💳 Verified Fee & Tuition Account\n\n"
            f"- **Account Status**: {status_flag}\n"
            f"- **Total Invoiced**: ₹{summary.total_invoiced:,.2f}\n"
            f"- **Total Paid**: ₹{summary.total_paid:,.2f}\n"
            f"- **Current Balance Due**: **₹{summary.total_outstanding:,.2f}**\n\n"
            f"{why_matters}\n\n"
            f"**Invoice Ledger**:\n" + "\n".join(invoice_lines) + "\n\n"
            f"👉 **[Open Fee & Payment Portal](/fees)**"
        )
        return reply, ["Institutional Database (fee_invoices)", "Fee Regulations (Section 2.4)"], summary.model_dump()

    def _handle_timetable(
        self,
        query: str,
        user_id: str,
        repo: Any,
        context: Optional[Dict[str, Any]] = None,
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
            lines.append(f"### 🗓️ Verified Schedule for {target_day}")
        else:
            lines.append("### 🗓️ Verified Weekly Schedule")

        for ds in schedules:
            lines.append(f"\n**{ds.day_of_week}**:")
            for slot in ds.entries:
                lines.append(
                    f"- **{slot.start_time} - {slot.end_time}**: **{slot.subject_code} - {slot.subject_name}** | Room: **{slot.room_number}** | Faculty: {slot.faculty_name}"
                )

        lines.append("\n👉 **[Open Complete Timetable Schedule](/timetable)**")
        reply = "\n".join(lines)
        verified_data = {"schedules": [ds.model_dump() for ds in schedules]}
        return reply, ["Institutional Database (timetable_entries)"], verified_data

    def _handle_notices(
        self,
        query: str,
        repo: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """Resolve published campus circulars."""
        notices = repo.get_notices(target_role="student", limit=5)
        if not notices:
            return (
                "There are no active circulars or announcements posted currently.",
                ["Institutional Database (campus_notices)"],
                {},
            )

        lines = ["### 📢 Recent Campus Circulars & Announcements\n"]
        for n in notices:
            lines.append(
                f"- **[{n.category.upper()}] {n.title}** (Published: {n.published_at.strftime('%Y-%m-%d')})\n"
                f"  {n.content}\n"
            )

        lines.append("👉 **[Open Campus Notices](/notices)**")
        reply = "\n".join(lines)
        verified_data = {"notices": [n.model_dump() for n in notices]}
        return reply, ["Institutional Database (campus_notices)"], verified_data


intent_router = IntentRouter()

