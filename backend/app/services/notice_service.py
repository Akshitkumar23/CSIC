"""Campus notices and announcements service."""
from typing import Any, List, Optional

from backend.app.models.notice import NoticeCreate, NoticeItem
from backend.app.repositories.database import get_repository


class NoticeService:
    """Manages publishing, listing, and filtering campus circulars."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def get_notices(
        self,
        target_role: Optional[str] = None,
        limit: int = 50,
    ) -> List[NoticeItem]:
        """Fetch published notices filtered by audience role."""
        return self.repo.get_notices(target_role=target_role, limit=limit)

    def get_notice_by_id(self, notice_id: str) -> Optional[NoticeItem]:
        """Fetch published notice by unique ID."""
        return self.repo.get_notice_by_id(notice_id)


    def publish_notice(
        self,
        notice: NoticeCreate,
        publisher_id: str,
    ) -> NoticeItem:
        """Create and publish a new campus notice."""
        return self.repo.create_notice(notice, publisher_id)

    def delete_notice(self, notice_id: str) -> bool:
        """Delete notice by unique ID."""
        return self.repo.delete_notice(notice_id)


notice_service = NoticeService()
