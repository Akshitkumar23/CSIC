"""Search information service for CSIC."""
from typing import Any, List, Optional

from backend.app.models.search import SearchItem
from backend.app.repositories.database import get_repository


class SearchService:
    """Manages search queries across institutional information modules."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def search(
        self,
        branch: Optional[str] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
        subject: Optional[str] = None,
        query_text: Optional[str] = None,
    ) -> List[SearchItem]:
        """Search institutional information by branch, year, category, subject, and text."""
        try:
            return self.repo.search_information(
                branch=branch,
                year=year,
                category=category,
                subject=subject,
                query_text=query_text,
            )
        except Exception:
            # Resilient fallback if database query or connection fails
            if hasattr(self.repo, "_fallback_search_records") and hasattr(self.repo, "_parse_datetime"):
                raw_items = self.repo._fallback_search_records(branch, year, category, subject, query_text)
                return [
                    SearchItem(
                        id=r["id"],
                        branch=r["branch"],
                        year=r["year"],
                        category=r["category"],
                        subject=r["subject"],
                        title=r["title"],
                        content_details=r["content_details"],
                        file_url=r["file_url"],
                        created_at=self.repo._parse_datetime(r.get("created_at")),
                    )
                    for r in raw_items
                ]
            return []


search_service = SearchService()
