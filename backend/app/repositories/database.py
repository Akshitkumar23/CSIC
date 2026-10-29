"""Database connectivity support and SQL repository provider."""
import logging
from typing import Any

from backend.app.core.config import settings
from backend.app.repositories.sql_repository import SQLRepository, sql_repo

logger = logging.getLogger("csic.database")


async def check_db_health() -> bool:
    """Check database health probe for /health/ready.

    Tests connectivity to active engine (PostgreSQL or self-healing SQLite).
    """
    try:
        conn = sql_repo._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        sql_repo._release_connection(conn)
        return True
    except Exception as err:
        logger.error("Database health check probe failed: %s", str(err))
        return False


def get_repository() -> SQLRepository:
    """Dependency provider returning the active production SQL repository instance."""
    return sql_repo
