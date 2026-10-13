"""Student domain management service."""
from typing import Any, List, Optional

from fastapi import HTTPException, status

from backend.app.models.student import StudentDetail
from backend.app.repositories.database import get_repository


class StudentService:
    """Manages student profile retrieval and registry queries."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_student(self, student_id: str) -> StudentDetail:
        """Retrieve complete student profile by ID."""
        detail = self.repo.get_student_detail(student_id)
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{student_id}' not found",
            )
        return detail

    def list_students(self) -> List[StudentDetail]:
        """List all active students."""
        return self.repo.list_students()


student_service = StudentService()
