from typing import Optional
from pydantic import BaseModel, Field


class AdminStats(BaseModel):
    """Key metric figures for the institutional administration dashboard."""
    total_students: int
    total_faculty: int
    total_courses: int
    total_notices: int
    average_attendance: float
    pending_fees_amount: float


class StudentCreate(BaseModel):
    """Admin registration payload for onboarding a new student."""
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=150)
    phone: Optional[str] = None
    roll_number: str = Field(..., min_length=3, max_length=30)
    program_code: str = Field(..., description="E.g., CSE, ECE, MECH")
    semester_number: int = Field(1, ge=1, le=8)
    section: str = Field("A", max_length=5)


class MarksInput(BaseModel):
    """Payload for faculty/admin to submit or update student exam score."""
    examination_id: str
    enrollment_id: str
    marks_obtained: float = Field(..., ge=0.0)
    is_absent: bool = False
    grade: Optional[str] = None
