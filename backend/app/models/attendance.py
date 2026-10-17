from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AttendanceRecord(BaseModel):
    """Granular attendance record for an individual student class session."""
    id: str
    session_id: str
    enrollment_id: str
    status: str  # present, absent, excused, late
    remarks: Optional[str] = None
    marked_at: datetime
    session_date: date
    topic: Optional[str] = None
    subject_code: str
    subject_name: str


class SubjectAttendance(BaseModel):
    """Aggregated attendance metrics for a specific subject course offering."""
    subject_code: str
    subject_name: str
    total_sessions: int
    attended_sessions: int
    excused_sessions: int
    absent_sessions: int
    attendance_percentage: float = Field(..., ge=0.0, le=100.0)
    is_low_attendance: bool = False  # Flagged if percentage < 75.0%

    @property
    def attended_classes(self) -> int:
        """Effective attended classes including institutional/medical excused leaves."""
        return self.attended_sessions + self.excused_sessions

    @property
    def total_classes(self) -> int:
        """Total conducted class sessions."""
        return self.total_sessions


class AttendanceSummary(BaseModel):
    """Consolidated student attendance dashboard metrics."""
    student_id: str
    roll_number: str
    overall_percentage: float = Field(..., ge=0.0, le=100.0)
    is_at_risk: bool = False  # Warning if overall attendance < 75.0%
    subjects: List[SubjectAttendance] = Field(default_factory=list)

    @property
    def attended_classes(self) -> int:
        """Total effective attended sessions across all subjects."""
        return sum(s.attended_sessions + s.excused_sessions for s in self.subjects)

    @property
    def total_classes(self) -> int:
        """Total conducted class sessions across all subjects."""
        return sum(s.total_sessions for s in self.subjects)

