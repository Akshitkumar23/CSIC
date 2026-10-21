"""Search information endpoints for CSIC."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from backend.app.core.security import get_current_user
from backend.app.models.auth import UserProfile
from backend.app.models.search import SearchItem
from backend.app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search Information"])


@router.get("", response_model=List[SearchItem], summary="Search institutional academic information")
async def search_information(
    branch: Optional[str] = Query(None, description="Branch/Department name filter (e.g. Computer Science & Engineering, CSE)"),
    year: Optional[int] = Query(None, ge=1, le=4, description="Academic year (1-4)"),
    category: Optional[str] = Query(None, description="Category filter (Syllabus, Timetable, Results, Fees, FAQ)"),
    subject: Optional[str] = Query(None, description="Course subject name filter"),
    q: Optional[str] = Query(None, description="Full-text / keyword search query"),
    current_user: UserProfile = Depends(get_current_user),
) -> List[SearchItem]:
    """Search institutional records by branch, year, category, subject, and keyword."""
    return search_service.search(
        branch=branch,
        year=year,
        category=category,
        subject=subject,
        query_text=q,
    )
