"""Services layer exports."""
from backend.app.services.admin_service import admin_service
from backend.app.services.attendance_service import attendance_service
from backend.app.services.auth_service import auth_service
from backend.app.services.fee_service import fee_service
from backend.app.services.marks_service import marks_service
from backend.app.services.notice_service import notice_service
from backend.app.services.student_service import student_service
from backend.app.services.timetable_service import timetable_service
from backend.app.services.ai.chatbot_service import chatbot_service
from backend.app.services.ai.intent_router import intent_router
from backend.app.services.ai.rag_service import rag_service

__all__ = [
    "admin_service",
    "attendance_service",
    "auth_service",
    "chatbot_service",
    "fee_service",
    "intent_router",
    "marks_service",
    "notice_service",
    "rag_service",
    "student_service",
    "timetable_service",
]
