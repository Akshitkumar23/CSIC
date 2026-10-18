#!/usr/bin/env python3
"""
CSIC - Simplified 11-Table Schema & Migrations Verification Test Suite
Verifies SQL syntax, table schemas, foreign keys, CHECK constraints,
seed data integrity, and analytical SQL aggregations using SQLite.
"""

import datetime
import os
import sqlite3
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"
SCHEMA_SQL = MIGRATIONS_DIR / "001_simple_schema.sql"
SEED_SQL = MIGRATIONS_DIR / "002_seed_data.sql"
CHAT_SESSIONS_SQL = MIGRATIONS_DIR / "003_chat_sessions.sql"
UPDATE_STUDENTS_SQL = MIGRATIONS_DIR / "004_update_demo_students.sql"
SYNC_ACCOUNTS_SQL = MIGRATIONS_DIR / "005_sync_demo_accounts.sql"

EXPECTED_TABLES = [
    "users",
    "courses",
    "subjects",
    "enrollments",
    "attendance_records",
    "examinations",
    "marks",
    "fee_records",
    "timetable_entries",
    "notices",
    "chat_history",
    "chat_sessions",
    "chat_messages",
]


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_true(self, condition, test_name, detail=""):
        if condition:
            self.passed += 1
            print(f"  [PASS] {test_name}")
        else:
            self.failed += 1
            msg = f"  [FAIL] {test_name}: {detail}"
            print(msg)
            self.errors.append(msg)

    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            print(f"  [PASS] {test_name}")
        else:
            self.failed += 1
            msg = f"  [FAIL] {test_name}: Expected '{expected}', got '{actual}'"
            print(msg)
            self.errors.append(msg)


def main():
    print("=" * 70)
    print("CSIC: Simplified 11-Table Schema Verification Test Suite")
    print("=" * 70)

    runner = TestRunner()

    # 1. Verify migration files exist
    runner.assert_true(SCHEMA_SQL.exists(), "Schema file exists (001_simple_schema.sql)")
    runner.assert_true(SEED_SQL.exists(), "Seed data file exists (002_seed_data.sql)")
    runner.assert_true(CHAT_SESSIONS_SQL.exists(), "Chat sessions migration exists (003_chat_sessions.sql)")
    runner.assert_true(SYNC_ACCOUNTS_SQL.exists(), "Sync demo accounts migration exists (005_sync_demo_accounts.sql)")

    # 2. Test in-memory SQLite initialization
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
            schema_content = f.read()
        cursor.executescript(schema_content)
        runner.assert_true(True, "Executed 001_simple_schema.sql cleanly")
    except Exception as e:
        runner.assert_true(False, "Executed 001_simple_schema.sql cleanly", str(e))

    try:
        with open(CHAT_SESSIONS_SQL, "r", encoding="utf-8") as f:
            chat_sessions_content = f.read()
        cursor.executescript(chat_sessions_content)
        runner.assert_true(True, "Executed 003_chat_sessions.sql cleanly")
    except Exception as e:
        runner.assert_true(False, "Executed 003_chat_sessions.sql cleanly", str(e))

    try:
        with open(SEED_SQL, "r", encoding="utf-8") as f:
            seed_content = f.read()
        cursor.executescript(seed_content)
        if UPDATE_STUDENTS_SQL.exists():
            with open(UPDATE_STUDENTS_SQL, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
        if SYNC_ACCOUNTS_SQL.exists():
            with open(SYNC_ACCOUNTS_SQL, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
        conn.commit()
        runner.assert_true(True, "Executed 002_seed_data.sql cleanly")
    except Exception as e:
        runner.assert_true(False, "Executed 002_seed_data.sql cleanly", str(e))

    # 3. Verify all 13 tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    for table in EXPECTED_TABLES:
        runner.assert_true(table in existing_tables, f"Table '{table}' exists in database")

    runner.assert_equal(len(existing_tables), 13, "Exactly 13 core tables created")

    # 4. Verify seed data row counts
    expected_counts = {
        "users": 7,
        "courses": 1,
        "subjects": 4,
        "enrollments": 4,
        "attendance_records": 96,
        "examinations": 4,
        "marks": 16,
        "fee_records": 5,
        "timetable_entries": 11,
        "notices": 4,
        "chat_history": 2,
    }

    print("\n--- Row Count Verification ---")
    for tbl, exp_cnt in expected_counts.items():
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        cnt = cursor.fetchone()[0]
        runner.assert_equal(cnt, exp_cnt, f"Table '{tbl}' has {exp_cnt} seeded rows")

    # 5. Referential Integrity & Foreign Key Tests
    print("\n--- Referential Integrity & Constraint Verification ---")
    
    # Test User roles
    cursor.execute("SELECT DISTINCT role FROM users;")
    roles = {r[0] for r in cursor.fetchall()}
    runner.assert_true(roles.issubset({"student", "faculty", "admin"}), "Users have valid roles")

    # Test UNIQUE constraint on users.email
    try:
        cursor.execute(
            "INSERT INTO users (id, name, email, password_hash, role) VALUES ('dup-1', 'Dup', 'rashi@csic.edu', 'hash', 'student');"
        )
        runner.assert_true(False, "UNIQUE constraint on users.email enforced")
    except sqlite3.IntegrityError:
        runner.assert_true(True, "UNIQUE constraint on users.email enforced")

    # Test UNIQUE constraint on enrollments.roll_number
    try:
        cursor.execute(
            "INSERT INTO enrollments (id, user_id, course_id, roll_number, semester) VALUES ('dup-e', 'fac-001', 'crs-01', 'CS2023001', 6);"
        )
        runner.assert_true(False, "UNIQUE constraint on enrollments.roll_number enforced")
    except sqlite3.IntegrityError:
        runner.assert_true(True, "UNIQUE constraint on enrollments.roll_number enforced")

    # Test Attendance UNIQUE constraint: (enrollment_id, subject_id, session_date)
    try:
        cursor.execute(
            "INSERT INTO attendance_records (id, enrollment_id, subject_id, session_date, status) VALUES ('dup-att', 'enr-001', 'sub-01', '2026-02-02', 'present');"
        )
        runner.assert_true(False, "UNIQUE constraint on attendance (enrollment, subject, date) enforced")
    except sqlite3.IntegrityError:
        runner.assert_true(True, "UNIQUE constraint on attendance (enrollment, subject, date) enforced")

    # Test Notice category CHECK constraint
    try:
        cursor.execute(
            "INSERT INTO notices (id, title, content, category, target_role, published_by) VALUES ('cat-test-admin', 'Admin Circular', 'Details', 'administrative', 'all', 'admin-001');"
        )
        cursor.execute(
            "INSERT INTO notices (id, title, content, category, target_role, published_by) VALUES ('cat-test-fee', 'Fee Circular', 'Details', 'fees', 'all', 'admin-001');"
        )
        runner.assert_true(True, "Notice categories 'administrative' and 'fees' accepted by CHECK constraint")
    except sqlite3.IntegrityError as e:
        runner.assert_true(False, "Notice categories 'administrative' and 'fees' accepted", str(e))

    try:
        cursor.execute(
            "INSERT INTO notices (id, title, content, category, target_role, published_by) VALUES ('cat-test-inv', 'Invalid Circular', 'Details', 'invalid_cat_xyz', 'all', 'admin-001');"
        )
        runner.assert_true(False, "Invalid notice category rejected by CHECK constraint")
    except sqlite3.IntegrityError:
        runner.assert_true(True, "Invalid notice category rejected by CHECK constraint")

    # Test Foreign Key on delete cascade (subjects -> courses)
    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    runner.assert_equal(len(fk_violations), 0, "Zero foreign key violations across seeded database")

    # 6. Core SQL Business Logic Aggregation Tests
    print("\n--- Analytical Query Verification ---")

    # Attendance query verification
    cursor.execute("""
        SELECT 
            u.name,
            ROUND(CAST(SUM(CASE WHEN a.status IN ('present', 'excused') THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(a.id), 1) AS pct
        FROM enrollments e
        JOIN users u ON u.id = e.user_id
        JOIN attendance_records a ON a.enrollment_id = e.id
        GROUP BY u.id, u.name
        ORDER BY u.name;
    """)
    attendance_results = dict(cursor.fetchall())
    
    runner.assert_true(attendance_results["Rashi"] >= 75.0, f"Rashi attendance is {attendance_results['Rashi']}% (>= 75%)")
    runner.assert_true(attendance_results["Vanshika"] >= 75.0, f"Vanshika attendance is {attendance_results['Vanshika']}% (>= 75%)")
    runner.assert_true(attendance_results["Silki"] < 75.0, f"Silki attendance is {attendance_results['Silki']}% (< 75% warning trigger)")
    runner.assert_true(attendance_results["Akshit"] >= 75.0, f"Akshit attendance is {attendance_results['Akshit']}% (>= 75%)")

    # Fee balance query verification
    cursor.execute("""
        SELECT 
            u.name,
            SUM(f.amount) as invoiced,
            SUM(f.amount_paid) as paid,
            SUM(f.amount - f.amount_paid) as balance
        FROM enrollments e
        JOIN users u ON u.id = e.user_id
        JOIN fee_records f ON f.enrollment_id = e.id
        GROUP BY u.id, u.name
        ORDER BY u.name;
    """)
    fee_results = {r[0]: (r[1], r[2], r[3]) for r in cursor.fetchall()}
    runner.assert_equal(fee_results["Rashi"][2], 0.0, "Rashi fee balance is 0.0 (paid in full)")
    runner.assert_equal(fee_results["Vanshika"][2], 30000.0, "Vanshika fee balance is 30,000.0 (partially paid)")
    runner.assert_equal(fee_results["Silki"][2], 65000.0, "Silki fee balance is 65,000.0 (unpaid)")
    runner.assert_equal(fee_results["Akshit"][2], 0.0, "Akshit fee balance is 0.0 (paid in full)")

    # Marks query verification
    cursor.execute("""
        SELECT 
            u.name,
            ROUND(AVG(m.marks_obtained), 1) as avg_marks
        FROM enrollments e
        JOIN users u ON u.id = e.user_id
        JOIN marks m ON m.enrollment_id = e.id
        GROUP BY u.id, u.name
        ORDER BY u.name;
    """)
    marks_results = dict(cursor.fetchall())
    runner.assert_true(marks_results["Rashi"] > marks_results["Silki"], "Rashi average marks exceed Silki")

    # Timetable entries count by day
    cursor.execute("SELECT day_of_week, COUNT(*) FROM timetable_entries GROUP BY day_of_week;")
    tt_days = dict(cursor.fetchall())
    runner.assert_true("Monday" in tt_days and tt_days["Monday"] == 3, "Monday has 3 scheduled lecture slots")
    runner.assert_true("Tuesday" in tt_days and tt_days["Tuesday"] == 2, "Tuesday has 2 scheduled lecture slots")

    conn.close()

    print("\n" + "=" * 70)
    print(f"Results: {runner.passed} Passed, {runner.failed} Failed")
    print("=" * 70)

    if runner.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
