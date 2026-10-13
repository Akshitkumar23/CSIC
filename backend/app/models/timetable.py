from typing import List
from pydantic import BaseModel


class TimetableEntry(BaseModel):
    """Classroom time-slot entry mapped to a faculty assignment."""
    id: str
    day_of_week: str  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
    start_time: str  # HH:MM:SS or HH:MM
    end_time: str    # HH:MM:SS or HH:MM
    room_number: str
    subject_code: str
    subject_name: str
    faculty_name: str


class DailySchedule(BaseModel):
    """Daily grouped schedule containing all sequential lecture entries."""
    day_of_week: str
    entries: List[TimetableEntry]
