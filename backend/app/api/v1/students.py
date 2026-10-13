"""Student profile and registration endpoints."""
from typing import List

from fastapi import APIRouter, Depends

from backend.app.core.security import (
    get_current_user,
    require_faculty,
    require_student,
    verify_student_access,
)
from backend.app.models.auth import UserProfile
from backend.app.models.student import StudentDetail
from backend.app.services.student_service import student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me", response_model=StudentDetail, summary="Get current student profile")
async def get_current_student_profile(
    current_user: UserProfile = Depends(require_student),
) -> StudentDetail:
    """Retrieve full enrollment profile for the authenticated student."""
    return student_service.get_student(current_user.id)


@router.get("", response_model=List[StudentDetail], summary="List all students")
async def list_students(
    _: UserProfile = Depends(require_faculty),
) -> List[StudentDetail]:
    """List all registered students (restricted to faculty and administration)."""
    return student_service.list_students()


@router.get("/{student_id}", response_model=StudentDetail, summary="Get student by ID")
async def get_student_by_id(
    student_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> StudentDetail:
    """Retrieve student profile by ID.

    Students are strictly restricted from inspecting other students' records.
    """
    verify_student_access(current_user, student_id)
    return student_service.get_student(student_id)
