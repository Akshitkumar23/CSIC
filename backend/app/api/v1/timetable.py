"""Lecture timetables and scheduling endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from backend.app.core.security import (
    get_current_user,
    require_student,
    verify_student_access,
)
from backend.app.models.auth import UserProfile
from backend.app.models.timetable import DailySchedule
from backend.app.services.timetable_service import timetable_service

router = APIRouter(prefix="/timetable", tags=["Timetable & Scheduling"])


@router.get("/me", response_model=List[DailySchedule], summary="Get current student weekly schedule")
async def get_my_timetable(
    day_of_week: Optional[str] = Query(None, description="Optional filter by day of week"),
    current_user: UserProfile = Depends(require_student),
) -> List[DailySchedule]:
    """Fetch complete weekly or day-specific schedule for enrolled lectures."""
    return timetable_service.get_schedule(current_user.id, day_of_week)


@router.get("/today", response_model=DailySchedule, summary="Get current day's lecture schedule")
async def get_today_timetable(
    current_user: UserProfile = Depends(require_student),
) -> DailySchedule:
    """Fetch current day's lecture timetable."""
    today_name = datetime.now().strftime("%A")
    schedules = timetable_service.get_schedule(current_user.id, today_name)
    if schedules:
        return schedules[0]
    return DailySchedule(day_of_week=today_name, entries=[])


@router.get("/week", response_model=List[DailySchedule], summary="Get 5-day week lecture schedule")
async def get_week_timetable(
    current_user: UserProfile = Depends(require_student),
) -> List[DailySchedule]:
    """Fetch 5-day full academic schedule (Monday to Friday)."""
    return timetable_service.get_schedule(current_user.id)


@router.get("/student/{student_id}", response_model=List[DailySchedule], summary="Get student timetable by ID")
async def get_student_timetable(
    student_id: str,
    day_of_week: Optional[str] = Query(None),
    current_user: UserProfile = Depends(get_current_user),
) -> List[DailySchedule]:
    """Fetch timetable for student ID enforcing authorization rules."""
    verify_student_access(current_user, student_id)
    return timetable_service.get_schedule(student_id, day_of_week)
