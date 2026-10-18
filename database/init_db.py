"""Database initialization and seeding script for CSIC.

Supports:
- Local SQLite database file: `database/csic.db`
- Cloud PostgreSQL database: via `DATABASE_URL` environment variable
"""
import os
import sqlite3
import sys
from pathlib import Path

# Paths to migrations
BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "migrations" / "001_simple_schema.sql"
SEED_FILE = BASE_DIR / "migrations" / "002_seed_data.sql"
CHAT_SESSIONS_FILE = BASE_DIR / "migrations" / "003_chat_sessions.sql"
UPDATE_DEMO_STUDENTS_FILE = BASE_DIR / "migrations" / "004_update_demo_students.sql"
SYNC_DEMO_ACCOUNTS_FILE = BASE_DIR / "migrations" / "005_sync_demo_accounts.sql"
SQLITE_DB_PATH = BASE_DIR / "csic.db"


def init_sqlite(db_path: Path = SQLITE_DB_PATH) -> None:
    """Initialize SQLite database with simplified schema and seed data."""
    print(f"[SQLite] Initializing database at: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print(" -> Schema executed successfully.")

    if CHAT_SESSIONS_FILE.exists():
        with open(CHAT_SESSIONS_FILE, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print(" -> Chat sessions schema executed successfully.")

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed_sql = f.read()
    cursor.executescript(seed_sql)

    if UPDATE_DEMO_STUDENTS_FILE.exists():
        with open(UPDATE_DEMO_STUDENTS_FILE, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print(" -> Update demo students script executed successfully.")

    if SYNC_DEMO_ACCOUNTS_FILE.exists():
        with open(SYNC_DEMO_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print(" -> Sync demo accounts script (005) executed successfully.")

    conn.commit()
    print(" -> Seed data inserted successfully.")

    # Verification query
    tables = [
        "users", "courses", "subjects", "enrollments",
        "attendance_records", "examinations", "marks",
        "fee_records", "timetable_entries", "notices", "chat_history",
        "chat_sessions", "chat_messages"
    ]
    print("\n--- Verification: Row Counts in Core Tables ---")
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        count = cursor.fetchone()[0]
        print(f"  {tbl:<22}: {count:>3} rows")

    conn.close()
    print("[SQLite] Initialization complete.\n")


def init_postgres(database_url: str) -> None:
    """Initialize PostgreSQL database with simplified schema and seed data."""
    print(f"[PostgreSQL] Initializing database via DATABASE_URL...")
    import psycopg2

    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.execute(schema_sql)
    print(" -> Schema executed successfully.")

    if CHAT_SESSIONS_FILE.exists():
        with open(CHAT_SESSIONS_FILE, "r", encoding="utf-8") as f:
            cursor.execute(f.read())
        print(" -> Chat sessions schema executed successfully.")

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed_sql = f.read()
    cursor.execute(seed_sql)
    print(" -> Seed data inserted successfully.")

    if UPDATE_DEMO_STUDENTS_FILE.exists():
        with open(UPDATE_DEMO_STUDENTS_FILE, "r", encoding="utf-8") as f:
            cursor.execute(f.read())
        print(" -> Update demo students script executed successfully.")

    if SYNC_DEMO_ACCOUNTS_FILE.exists():
        with open(SYNC_DEMO_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            cursor.execute(f.read())
        print(" -> Sync demo accounts script (005) executed successfully.")

    tables = [
        "users", "courses", "subjects", "enrollments",
        "attendance_records", "examinations", "marks",
        "fee_records", "timetable_entries", "notices", "chat_history",
        "chat_sessions", "chat_messages"
    ]
    print("\n--- Verification: Row Counts in Core Tables ---")
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        count = cursor.fetchone()[0]
        print(f"  {tbl:<22}: {count:>3} rows")

    cursor.close()
    conn.close()
    print("[PostgreSQL] Initialization complete.\n")


def main() -> None:
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        init_postgres(db_url)
    else:
        init_sqlite()


if __name__ == "__main__":
    main()
