"""Academic examination results and grade calculation service."""
from typing import Any, List, Optional

from fastapi import HTTPException, status

from backend.app.models.marks import ExamResult, SemesterResult
from backend.app.repositories.database import get_repository


class MarksService:
    """Manages examination results and semester CGPA calculations."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_exam_results(self, student_id: str) -> List[ExamResult]:
        """Fetch all examination scores grouped by exam cycle."""
        results = self.repo.get_exam_results(student_id)
        return results

    def get_semester_results(
        self,
        student_id: str,
        semester_number: Optional[int] = None,
    ) -> List[SemesterResult]:
        """Fetch consolidated semester report card."""
        return self.repo.get_semester_results(student_id, semester_number)


marks_service = MarksService()
