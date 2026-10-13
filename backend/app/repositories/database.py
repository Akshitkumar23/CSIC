"""Database connectivity support and SQL repository provider."""
import logging
from typing import Any

from backend.app.core.config import settings
from backend.app.repositories.sql_repository import SQLRepository, sql_repo

logger = logging.getLogger("csic.database")


async def check_db_health() -> bool:
    """Check database health probe for /health/ready.

    - In production: Strictly tests PostgreSQL connectivity via DATABASE_URL.
      Fails immediately (returns False) if DATABASE_URL is missing, invalid, or unreachable.
      Silent fallback to SQLite is strictly forbidden in production.
    - In local development/test: Tests connection to active engine (PostgreSQL if set, or local SQLite).
    """
    if settings.is_production:
        if not settings.DATABASE_URL or not (
            settings.DATABASE_URL.startswith("postgres://")
            or settings.DATABASE_URL.startswith("postgresql://")
        ):
            logger.error("Production health probe failed: valid PostgreSQL DATABASE_URL is required.")
            return False

        try:
            import asyncpg

            conn = await asyncpg.connect(settings.DATABASE_URL, timeout=3.0)
            await conn.execute("SELECT 1;")
            await conn.close()
            return True
        except Exception as err:
            logger.error("Production PostgreSQL database unreachable: %s", str(err))
            return False

    # Development or Test environment
    if settings.DATABASE_URL and (
        settings.DATABASE_URL.startswith("postgres://")
        or settings.DATABASE_URL.startswith("postgresql://")
    ):
        try:
            import asyncpg

            conn = await asyncpg.connect(settings.DATABASE_URL, timeout=3.0)
            await conn.execute("SELECT 1;")
            await conn.close()
            return True
        except Exception as err:
            logger.warning("PostgreSQL connection check failed in non-production: %s", str(err))
            return False

    # Local SQLite
    try:
        conn = sql_repo._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
        return True
    except Exception as err:
        logger.error("Local SQLite database probe failed: %s", str(err))
        return False


def get_repository() -> SQLRepository:
    """Dependency provider returning the active production SQL repository instance."""
    return sql_repo
