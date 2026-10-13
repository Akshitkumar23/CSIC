"""Attendance business logic and low attendance calculation service."""
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from backend.app.models.attendance import AttendanceRecord, AttendanceSummary
from backend.app.repositories.database import get_repository


class AttendanceService:
    """Manages attendance calculations, warnings, and history."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_summary(self, student_id: str) -> AttendanceSummary:
        """Fetch subject-wise and overall attendance percentage."""
        summary = self.repo.get_student_attendance_summary(student_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance records not found for student '{student_id}'",
            )
        return summary

    def get_records(self, student_id: str) -> List[AttendanceRecord]:
        """Fetch individual session records for a student."""
        return self.repo.get_attendance_records_for_student(student_id)

    def get_warnings(self) -> List[Dict[str, Any]]:
        """Fetch all students with attendance below 75%."""
        return self.repo.get_low_attendance_warnings()


attendance_service = AttendanceService()
