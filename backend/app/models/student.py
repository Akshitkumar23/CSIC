from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class EnrollmentDetail(BaseModel):
    """Academic enrollment linking student to a program course section."""
    id: str
    student_id: str
    course_id: str
    roll_number: str
    enrollment_date: date
    status: str = "active"  # active, completed, dropped, suspended
    program_code: str
    program_name: str
    semester_number: int
    section: str = "A"


class StudentDetail(BaseModel):
    """Detailed student profile including active and past enrollments."""
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "student"
    department_name: Optional[str] = None
    enrollments: List[EnrollmentDetail] = Field(default_factory=list)
