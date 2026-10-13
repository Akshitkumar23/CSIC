from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class MarkEntry(BaseModel):
    """Subject examination score achieved by an enrolled student."""
    id: str
    examination_id: str
    exam_name: str
    subject_code: str
    subject_name: str
    marks_obtained: float = Field(..., ge=0.0)
    max_marks: float = Field(..., gt=0.0)
    percentage: float = Field(..., ge=0.0, le=100.0)
    grade: Optional[str] = None
    is_absent: bool = False
    exam_date: date


class ExamResult(BaseModel):
    """Aggregated results across all subjects for a specific exam cycle."""
    examination_id: str
    exam_name: str
    subjects: List[MarkEntry] = Field(default_factory=list)
    total_obtained: float = Field(..., ge=0.0)
    total_max: float = Field(..., gt=0.0)
    overall_percentage: float = Field(..., ge=0.0, le=100.0)


class SemesterResult(BaseModel):
    """Semester-level academic performance record with GPA calculation."""
    semester_number: int
    term: str
    academic_year: str
    gpa: float = Field(..., ge=0.0, le=10.0)
    percentage: float = Field(..., ge=0.0, le=100.0)
    total_credits: float = Field(..., ge=0.0)
    results: List[MarkEntry] = Field(default_factory=list)
