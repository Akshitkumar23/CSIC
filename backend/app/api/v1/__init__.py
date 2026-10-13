"""API v1 router registration."""
from fastapi import APIRouter

from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.attendance import router as attendance_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.fees import router as fees_router
from backend.app.api.v1.marks import router as marks_router
from backend.app.api.v1.notices import router as notices_router
from backend.app.api.v1.students import router as students_router
from backend.app.api.v1.timetable import router as timetable_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(students_router)
api_router.include_router(attendance_router)
api_router.include_router(marks_router)
api_router.include_router(fees_router)
api_router.include_router(timetable_router)
api_router.include_router(notices_router)
api_router.include_router(admin_router)
api_router.include_router(chat_router)

__all__ = ["api_router"]
