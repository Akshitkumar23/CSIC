"""Examinations and grading evaluation endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from backend.app.core.security import (
    get_current_user,
    require_student,
    verify_student_access,
)
from backend.app.models.auth import UserProfile
from backend.app.models.marks import ExamResult, SemesterResult
from backend.app.services.marks_service import marks_service

router = APIRouter(prefix="/marks", tags=["Marks & Examinations"])


@router.get("/me", response_model=List[ExamResult], summary="Get current student examination scores")
async def get_my_exam_results(
    current_user: UserProfile = Depends(require_student),
) -> List[ExamResult]:
    """Fetch examination scores grouped by cycle for the active student."""
    return marks_service.get_exam_results(current_user.id)


@router.get("/student/{student_id}", response_model=List[ExamResult], summary="Get exam results by student ID")
async def get_student_exam_results(
    student_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> List[ExamResult]:
    """Fetch exam results for a specified student ID (enforcing authorization boundaries)."""
    verify_student_access(current_user, student_id)
    return marks_service.get_exam_results(student_id)


@router.get("/semester/{semester_number}", response_model=List[SemesterResult], summary="Get current student semester card")
async def get_my_semester_results(
    semester_number: int,
    current_user: UserProfile = Depends(require_student),
) -> List[SemesterResult]:
    """Fetch cumulative GPA and subject performance for a specific semester."""
    return marks_service.get_semester_results(current_user.id, semester_number)


@router.get(
    "/student/{student_id}/semester/{semester_number}",
    response_model=List[SemesterResult],
    summary="Get student semester card by ID",
)
async def get_student_semester_results(
    student_id: str,
    semester_number: int,
    current_user: UserProfile = Depends(get_current_user),
) -> List[SemesterResult]:
    """Fetch semester result report card for a specified student ID."""
    verify_student_access(current_user, student_id)
    return marks_service.get_semester_results(student_id, semester_number)
