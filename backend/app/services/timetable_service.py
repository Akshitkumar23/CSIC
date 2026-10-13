"""Course scheduling and timetable service."""
from typing import Any, List, Optional

from backend.app.models.timetable import DailySchedule
from backend.app.repositories.database import get_repository


class TimetableService:
    """Manages academic lecture schedules and classroom allotments."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_schedule(
        self,
        student_id: str,
        day_of_week: Optional[str] = None,
    ) -> List[DailySchedule]:
        """Fetch weekly or day-specific schedule for enrolled courses."""
        return self.repo.get_student_timetable(student_id, day_of_week)


timetable_service = TimetableService()
