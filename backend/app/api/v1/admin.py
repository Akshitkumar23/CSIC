from typing import List

from fastapi import APIRouter, Depends, status

from backend.app.core.security import require_admin, require_faculty
from backend.app.models.admin import AdminStats, FacultyCourseAssignmentItem, MarksInput, StudentCreate
from backend.app.models.auth import UserProfile
from backend.app.models.marks import MarkEntry
from backend.app.models.student import StudentDetail
from backend.app.services.admin_service import admin_service

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/stats", response_model=AdminStats, summary="Get administration overview metrics")
async def get_admin_stats(
    _: UserProfile = Depends(require_admin),
) -> AdminStats:
    """Consolidated institutional metrics for the administrative dashboard."""
    return admin_service.get_stats()


@router.get(
    "/faculty-assignments",
    response_model=List[FacultyCourseAssignmentItem],
    summary="Get faculty course allocations",
)
async def get_faculty_assignments(
    _: UserProfile = Depends(require_faculty),
) -> List[FacultyCourseAssignmentItem]:
    """Retrieve dynamic course-faculty allotments from the academic catalog."""
    return admin_service.get_faculty_assignments()



@router.post(
    "/students",
    response_model=StudentDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Register new student",
)
async def create_student(
    student_in: StudentCreate,
    _: UserProfile = Depends(require_admin),
) -> StudentDetail:
    """Enroll and create a new student account with course assignments."""
    return admin_service.create_student(student_in)


@router.post(
    "/marks",
    response_model=MarkEntry,
    status_code=status.HTTP_201_CREATED,
    summary="Record or update student marks",
)
async def enter_marks(
    marks_in: MarksInput,
    current_user: UserProfile = Depends(require_faculty),
) -> MarkEntry:
    """Enter or update student marks for an examination (faculty & admin only)."""
    return admin_service.enter_marks(marks_in, current_user.id)
