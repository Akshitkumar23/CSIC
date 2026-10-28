"""Campus broadcast notices and circulars endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.core.security import get_current_user, require_faculty
from backend.app.models.auth import UserProfile
from backend.app.models.notice import NoticeCreate, NoticeItem
from backend.app.services.notice_service import notice_service

router = APIRouter(prefix="/notices", tags=["Notices & Circulars"])


@router.get("", response_model=List[NoticeItem], summary="List published notices")
async def list_notices(
    target_role: Optional[str] = Query(None, description="Optional audience filter: student, faculty, all"),
    limit: int = Query(50, ge=1, le=100),
) -> List[NoticeItem]:
    """Retrieve campus broadcasts categorized by urgency and academic domain."""
    return notice_service.get_notices(target_role=target_role, limit=limit)


@router.get("/{notice_id}", response_model=NoticeItem, summary="Get notice by ID")
async def get_notice_by_id(notice_id: str) -> NoticeItem:
    """Retrieve detailed notice item by ID."""
    notice = notice_service.get_notice_by_id(notice_id)
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notice '{notice_id}' not found",
        )
    return notice



@router.post("", response_model=NoticeItem, status_code=status.HTTP_201_CREATED, summary="Publish new notice")
async def publish_notice(
    notice_in: NoticeCreate,
    current_user: UserProfile = Depends(require_faculty),
) -> NoticeItem:
    """Publish a new campus notice (restricted to faculty and administration)."""
    return notice_service.publish_notice(notice_in, current_user.id)


@router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete notice")
async def delete_notice(
    notice_id: str,
    current_user: UserProfile = Depends(require_faculty),
) -> None:
    """Delete a campus notice (restricted to faculty and administration)."""
    success = notice_service.delete_notice(notice_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notice '{notice_id}' not found",
        )
