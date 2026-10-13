"""Pydantic V2 schemas for CSIC application."""
from backend.app.models.auth import Token, TokenData, LoginRequest, UserProfile
from backend.app.models.student import StudentDetail, EnrollmentDetail
from backend.app.models.attendance import SubjectAttendance, AttendanceSummary, AttendanceRecord
from backend.app.models.marks import ExamResult, MarkEntry, SemesterResult
from backend.app.models.fee import FeeInvoice, FeePayment, FeeSummary
from backend.app.models.timetable import TimetableEntry, DailySchedule
from backend.app.models.notice import NoticeItem, NoticeCreate
from backend.app.models.admin import AdminStats, StudentCreate, MarksInput
from backend.app.models.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryItem,
    ChatSuggestionsResponse,
)

__all__ = [
    "Token",
    "TokenData",
    "LoginRequest",
    "UserProfile",
    "StudentDetail",
    "EnrollmentDetail",
    "SubjectAttendance",
    "AttendanceSummary",
    "AttendanceRecord",
    "ExamResult",
    "MarkEntry",
    "SemesterResult",
    "FeeInvoice",
    "FeePayment",
    "FeeSummary",
    "TimetableEntry",
    "DailySchedule",
    "NoticeItem",
    "NoticeCreate",
    "AdminStats",
    "StudentCreate",
    "MarksInput",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryItem",
    "ChatSuggestionsResponse",
]
