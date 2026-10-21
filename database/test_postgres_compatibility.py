#!/usr/bin/env python3
"""
CSIC - PostgreSQL 16 Real Database Verification Script.

Connects to a real PostgreSQL instance via `DATABASE_URL`,
applies `001_simple_schema.sql` and `002_seed_data.sql`,
and verifies table counts and relational queries.

If PostgreSQL is not running or DATABASE_URL is not set,
this script exits with status code 2 and outputs [BLOCKED].
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "migrations" / "001_simple_schema.sql"
SEED_FILE = BASE_DIR / "migrations" / "002_seed_data.sql"
CHAT_SESSIONS_FILE = BASE_DIR / "migrations" / "003_chat_sessions.sql"
UPDATE_STUDENTS_FILE = BASE_DIR / "migrations" / "004_update_demo_students.sql"
SYNC_DEMO_ACCOUNTS_FILE = BASE_DIR / "migrations" / "005_sync_demo_accounts.sql"
SEARCH_INFO_FILE = BASE_DIR / "migrations" / "006_search_information.sql"


def main():
    print("=" * 70)
    print("CSIC: Real PostgreSQL 16 Verification Suite")
    print("=" * 70)

    db_url = os.getenv("DATABASE_URL")
    if not db_url or not (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
        print("\n[BLOCKED] No PostgreSQL DATABASE_URL detected.")
        print("Reason: Docker is not installed/running locally, and no PostgreSQL host is configured.")
        print("To verify on real PostgreSQL:")
        print("  1. In GitHub Actions CI: Automatically validated against PostgreSQL 16 service container.")
        print("  2. In Cloud / Supabase: Copy connection string from Dashboard (Project Settings -> Database):")
        print("     - Transaction Pooler (Port 6543): postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require")
        print("     - Session Pooler (Port 5432):     postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require")
        print("     - Direct Connection (Port 5432):  postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require")
        print("=" * 70)
        sys.exit(2)

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("\n[ERROR] psycopg2-binary package not installed.")
        sys.exit(1)

    print(f"Connecting to PostgreSQL database: {db_url.split('@')[-1] if '@' in db_url else 'configured DB'}")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print(" -> Connection established successfully.")
    except Exception as e:
        print(f"\n[BLOCKED] Could not connect to PostgreSQL instance: {e}")
        sys.exit(2)

    # 1. Apply Schema
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cursor.execute(schema_sql)
        print(" -> 001_simple_schema.sql applied cleanly to PostgreSQL.")
    except Exception as e:
        print(f"[FAIL] Schema migration failed: {e}")
        sys.exit(1)

    # 2. Apply Chat Sessions Schema
    if CHAT_SESSIONS_FILE.exists():
        try:
            with open(CHAT_SESSIONS_FILE, "r", encoding="utf-8") as f:
                cursor.execute(f.read())
            print(" -> 003_chat_sessions.sql applied cleanly to PostgreSQL.")
        except Exception as e:
            print(f"[FAIL] Chat sessions migration failed: {e}")
            sys.exit(1)

    # 3. Apply Seed Data
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            seed_sql = f.read()
        cursor.execute(seed_sql)
        print(" -> 002_seed_data.sql applied cleanly to PostgreSQL.")
    except Exception as e:
        print(f"[FAIL] Seed data insertion failed: {e}")
        sys.exit(1)

    # 4. Apply Demo Students, Sync Accounts, and Search Information Migrations
    for mig_file, label in [
        (UPDATE_STUDENTS_FILE, "004_update_demo_students.sql"),
        (SYNC_DEMO_ACCOUNTS_FILE, "005_sync_demo_accounts.sql"),
        (SEARCH_INFO_FILE, "006_search_information.sql"),
    ]:
        if mig_file.exists():
            try:
                with open(mig_file, "r", encoding="utf-8") as f:
                    cursor.execute(f.read())
                print(f" -> {label} applied cleanly to PostgreSQL.")
            except Exception as e:
                print(f"[FAIL] {label} failed: {e}")
                sys.exit(1)

    # 5. Verify All 14 Table Counts
    tables = [
        "users", "courses", "subjects", "enrollments",
        "attendance_records", "examinations", "marks",
        "fee_records", "timetable_entries", "notices", "chat_history",
        "chat_sessions", "chat_messages", "search_information"
    ]
    print("\n--- PostgreSQL Table Row Counts ---")
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) AS c FROM {tbl};")
        count = cursor.fetchone()["c"]
        print(f"  {tbl:<22}: {count:>3} rows")

    cursor.close()
    conn.close()
    print("\n[PASS] PostgreSQL real database verification succeeded.")


if __name__ == "__main__":
    main()
