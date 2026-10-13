"""Attendance records and warning analytics endpoints."""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from backend.app.core.security import (
    get_current_user,
    require_faculty,
    require_student,
    verify_student_access,
)
from backend.app.models.attendance import AttendanceRecord, AttendanceSummary
from backend.app.models.auth import UserProfile
from backend.app.services.attendance_service import attendance_service

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/me", response_model=AttendanceSummary, summary="Get current student attendance")
async def get_my_attendance_summary(
    current_user: UserProfile = Depends(require_student),
) -> AttendanceSummary:
    """Fetch aggregated subject-wise and overall attendance percentage."""
    return attendance_service.get_summary(current_user.id)


@router.get("/records/me", response_model=List[AttendanceRecord], summary="Get current student session logs")
async def get_my_attendance_records(
    current_user: UserProfile = Depends(require_student),
) -> List[AttendanceRecord]:
    """Fetch detailed class-by-class attendance history."""
    return attendance_service.get_records(current_user.id)


@router.get("/student/{student_id}", response_model=AttendanceSummary, summary="Get student attendance by ID")
async def get_student_attendance(
    student_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> AttendanceSummary:
    """Fetch attendance summary for a specific student ID with negative authorization protection."""
    verify_student_access(current_user, student_id)
    return attendance_service.get_summary(student_id)


@router.get("/records/{student_id}", response_model=List[AttendanceRecord], summary="Get student session logs by ID")
async def get_student_attendance_records(
    student_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> List[AttendanceRecord]:
    """Fetch session records for a specific student ID."""
    verify_student_access(current_user, student_id)
    return attendance_service.get_records(student_id)


@router.get("/warnings", response_model=List[Dict[str, Any]], summary="Get low attendance warning roster")
async def get_low_attendance_warnings(
    _: UserProfile = Depends(require_faculty),
) -> List[Dict[str, Any]]:
    """List students with attendance below 75% (implements v_low_attendance_warnings)."""
    return attendance_service.get_warnings()
