"""Pytest fixtures and configuration for CSIC backend test suite."""
import sys
from pathlib import Path
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on python path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.core.security import create_access_token
from backend.app.main import app
from backend.app.repositories import sql_repository
from backend.app.repositories.sql_repository import sql_repo
from database.init_db import init_sqlite


@pytest.fixture(scope="session", autouse=True)
def isolated_test_database(tmp_path_factory: pytest.TempPathFactory) -> Generator[Path, None, None]:
    """Isolate all test database interactions into a temporary SQLite database.

    Initializes a fresh SQLite database using the official CSIC migration chain
    (001-006) and seed data in a pytest-managed temporary directory. Points the
    global SQL repository singleton to this isolated database, guaranteeing that
    no test run mutates the real development or demo database (`database/csic.db`).
    Restores original database configuration upon test session teardown.
    """
    # 1. Allocate isolated temp file in pytest temporary directory
    test_dir = tmp_path_factory.mktemp("csic_test_db")
    test_db_path = test_dir / "csic_test.db"

    # 2. Run migrations (001-006) and seed data
    init_sqlite(test_db_path)

    # 3. Preserve original repository and module state
    orig_db_path = sql_repo.db_path
    orig_is_postgres = sql_repo.is_postgres
    orig_database_url = sql_repo.database_url
    orig_module_db_path = sql_repository.SQLITE_DB_PATH

    # 4. Redirect repository and module default path to isolated test DB
    sql_repo.db_path = test_db_path
    sql_repo.is_postgres = False
    sql_repo.database_url = None
    sql_repository.SQLITE_DB_PATH = test_db_path

    try:
        yield test_db_path
    finally:
        # 5. Restore original configuration cleanly
        sql_repo.db_path = orig_db_path
        sql_repo.is_postgres = orig_is_postgres
        sql_repo.database_url = orig_database_url
        sql_repository.SQLITE_DB_PATH = orig_module_db_path


@pytest.fixture(scope="session")
def client(isolated_test_database: Path) -> Generator[TestClient, None, None]:
    """TestClient instance for synchronous endpoint testing."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def student_a_headers() -> Dict[str, str]:
    """JWT Bearer headers for Student A (stu-001 - Rashi)."""
    token = create_access_token({
        "sub": "stu-001",
        "user_id": "stu-001",
        "email": "rashi@csic.edu",
        "role": "student",
        "full_name": "Rashi",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_b_headers() -> Dict[str, str]:
    """JWT Bearer headers for Student B (stu-002 - Vanshika)."""
    token = create_access_token({
        "sub": "stu-002",
        "user_id": "stu-002",
        "email": "vanshika@csic.edu",
        "role": "student",
        "full_name": "Vanshika",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def faculty_headers() -> Dict[str, str]:
    """JWT Bearer headers for Faculty Instructor (fac-001 - Akshit)."""
    token = create_access_token({
        "sub": "fac-001",
        "user_id": "fac-001",
        "email": "rajesh.kumar@csic.edu",
        "role": "faculty",
        "full_name": "Akshit",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers() -> Dict[str, str]:
    """JWT Bearer headers for Institutional Administrator (admin-001 - Akshit)."""
    token = create_access_token({
        "sub": "admin-001",
        "user_id": "admin-001",
        "email": "admin@csic.edu",
        "role": "admin",
        "full_name": "Akshit",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_a_payable_invoice() -> Generator[str, None, None]:
    """Temporary test invoice for Student A (stu-001 / enr-001) with clean teardown."""
    import uuid
    from backend.app.repositories.database import get_repository
    repo = get_repository()
    inv_id = f"test-inv-{uuid.uuid4().hex[:8]}"
    sql = """
    INSERT INTO fee_records (id, invoice_number, enrollment_id, title, amount, amount_paid, due_date, status)
    VALUES (?, ?, 'enr-001', 'Temporary Test Lab Fee', 10000.00, 0.00, '2026-12-31', 'unpaid');
    """
    repo._execute_write(sql, (inv_id, f"INV-TEST-{inv_id}"))
    try:
        yield inv_id
    finally:
        try:
            repo._execute_write("DELETE FROM fee_records WHERE id = ?;", (inv_id,))
        except Exception:
            pass
