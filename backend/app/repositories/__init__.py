"""Repository package exposing repository provider and singleton instance."""
from backend.app.repositories.database import check_db_health, get_repository

__all__ = [
    "check_db_health",
    "get_repository",
]
