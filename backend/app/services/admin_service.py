"""Institutional administration business logic service."""
from typing import Any, Optional

from backend.app.models.admin import AdminStats, MarksInput, StudentCreate
from backend.app.models.marks import MarkEntry
from backend.app.models.student import StudentDetail
from backend.app.repositories.database import get_repository


class AdminService:
    """Manages administrative statistics, student onboarding, and marks entry."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_stats(self) -> AdminStats:
        """Fetch consolidated high-level institutional metrics."""
        return self.repo.get_admin_stats()

    def create_student(self, student_in: StudentCreate) -> StudentDetail:
        """Register a new student."""
        return self.repo.create_student(student_in)

    def enter_marks(self, marks_in: MarksInput, entered_by_id: str) -> MarkEntry:
        """Submit student score for an examination."""
        return self.repo.enter_marks(marks_in, entered_by_id)


admin_service = AdminService()
