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
        return self.repo.search_information(
            branch=branch,
            year=year,
            category=category,
            subject=subject,
            query_text=query_text,
        )


search_service = SearchService()
