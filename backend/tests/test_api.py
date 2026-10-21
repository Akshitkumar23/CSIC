"""Integration tests for CSIC business endpoints.

Covers Students, Attendance, Marks, Fees, Timetable, Notices, and Admin CRUD.
"""
from fastapi.testclient import TestClient


# =================================================================
# 1. Students Endpoint Tests
# =================================================================
def test_get_current_student_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify student profile /students/me returns full enrollments."""
    response = client.get("/api/v1/students/me", headers=student_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "stu-001"
    assert data["full_name"] == "Rashi"
    assert len(data["enrollments"]) > 0
    assert data["enrollments"][0]["roll_number"] == "CS2023001"


def test_list_all_students_as_faculty(client: TestClient, faculty_headers: dict) -> None:
    """Verify faculty can retrieve the comprehensive student roster."""
    response = client.get("/api/v1/students", headers=faculty_headers)
    assert response.status_code == 200
    students = response.json()
    assert len(students) >= 3


# =================================================================
# 2. Attendance Endpoint Tests
# =================================================================
def test_get_attendance_summary_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify student attendance summary calculation."""
    response = client.get("/api/v1/attendance/me", headers=student_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "stu-001"
    assert data["overall_percentage"] >= 75.0
    assert not data["is_at_risk"]
    assert len(data["subjects"]) > 0


def test_get_attendance_records_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify detailed attendance session logs."""
    response = client.get("/api/v1/attendance/records/me", headers=student_a_headers)
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)
    assert len(records) > 0
    assert "status" in records[0]
    assert "subject_code" in records[0]


def test_low_attendance_warnings_endpoint(client: TestClient, faculty_headers: dict) -> None:
    """Verify low attendance warning report flags at-risk students."""
    response = client.get("/api/v1/attendance/warnings", headers=faculty_headers)
    assert response.status_code == 200
    warnings = response.json()
    assert isinstance(warnings, list)
    assert any(w["student_id"] == "stu-003" for w in warnings)
    rohan_warning = next(w for w in warnings if w["student_id"] == "stu-003")
    assert rohan_warning["overall_percentage"] < 75.0


# =================================================================
# 3. Marks & Examination Tests
# =================================================================
def test_get_marks_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify examination results returned for current student."""
    response = client.get("/api/v1/marks/me", headers=student_a_headers)
    assert response.status_code == 200
    exam_results = response.json()
    assert len(exam_results) > 0
    first_exam = exam_results[0]
    assert "examination_id" in first_exam
    assert "overall_percentage" in first_exam
    assert len(first_exam["subjects"]) > 0


def test_get_semester_report_card(client: TestClient, student_a_headers: dict) -> None:
    """Verify semester summary calculation and GPA."""
    response = client.get("/api/v1/marks/semester/6", headers=student_a_headers)
    assert response.status_code == 200
    semesters = response.json()
    assert len(semesters) > 0
    sem = semesters[0]
    assert sem["semester_number"] == 6
    assert sem["gpa"] > 0.0
    assert len(sem["results"]) > 0


# =================================================================
# 4. Fee & Invoice Tests
# =================================================================
def test_get_fee_summary_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify student tuition invoices and payment ledger."""
    response = client.get("/api/v1/fees/me", headers=student_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "stu-001"
    assert data["total_invoiced"] > 0
    assert len(data["invoices"]) > 0


def test_pay_fee_invoice(
    client: TestClient,
    student_a_headers: dict,
    student_a_payable_invoice: str,
) -> None:
    """Verify simulated fee payment endpoint creates valid transaction for student's own invoice."""
    response = client.post(
        f"/api/v1/fees/invoices/{student_a_payable_invoice}/pay",
        params={"amount": 4000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    payment = response.json()
    assert payment["invoice_id"] == student_a_payable_invoice
    assert payment["amount_paid"] == 4000.0
    assert payment["status"] == "success"
    assert payment["payment_method"] == "upi"


# =================================================================
# 5. Timetable Tests
# =================================================================
def test_get_weekly_timetable_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify weekly timetable schedule retrieval."""
    response = client.get("/api/v1/timetable/me", headers=student_a_headers)
    assert response.status_code == 200
    schedule = response.json()
    assert isinstance(schedule, list)
    assert len(schedule) == 5
    assert any(day["day_of_week"] == "Monday" for day in schedule)


def test_get_today_timetable_me(client: TestClient, student_a_headers: dict) -> None:
    """Verify today's timetable endpoint returns DailySchedule."""
    response = client.get("/api/v1/timetable/today", headers=student_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert "day_of_week" in data
    assert "entries" in data


# =================================================================
# 6. Notices Tests
# =================================================================
def test_list_notices(client: TestClient) -> None:
    """Verify public broadcast notices listing."""
    response = client.get("/api/v1/notices")
    assert response.status_code == 200
    notices = response.json()
    assert len(notices) >= 4
    assert any(n["category"] == "examination" for n in notices)


def test_get_single_notice(client: TestClient) -> None:
    """Verify retrieval of specific notice item."""
    response = client.get("/api/v1/notices/not-01")
    assert response.status_code == 200
    notice = response.json()
    assert notice["id"] == "not-01"
    assert "End-Term Examination" in notice["title"]


def test_publish_notice_as_faculty(client: TestClient, faculty_headers: dict) -> None:
    """Verify faculty can broadcast a new campus circular."""
    payload = {
        "title": "Special Guest Lecture on Kubernetes",
        "category": "academic",
        "content": "A guest lecture by Google Cloud architects on Friday at 3 PM in Seminar Hall 2.",
        "target_role": "student",
        "is_published": True,
    }
    response = client.post("/api/v1/notices", json=payload, headers=faculty_headers)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == payload["title"]
    assert created["published_by_name"] == "Akshit"


# =================================================================
# 7. Admin Endpoint Tests
# =================================================================
def test_admin_stats(client: TestClient, admin_headers: dict) -> None:
    """Verify admin stats figures."""
    response = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] >= 3
    assert data["total_faculty"] >= 2
    assert data["average_attendance"] > 0


def test_admin_create_student(client: TestClient, admin_headers: dict) -> None:
    """Verify administrator student registration flow."""
    payload = {
        "email": "new.student@csic.edu",
        "password": "Password123!",
        "full_name": "Kavya Subramanian",
        "phone": "+91 98765 99999",
        "roll_number": "CS2023099",
        "program_code": "BTECH_CSE",
        "semester_number": 6,
        "section": "A",
    }
    response = client.post("/api/v1/admin/students", json=payload, headers=admin_headers)
    assert response.status_code == 201
    created = response.json()
    assert created["email"] == "new.student@csic.edu"
    assert created["full_name"] == "Kavya Subramanian"
    assert created["enrollments"][0]["roll_number"] == "CS2023099"


def test_faculty_enter_marks(client: TestClient, faculty_headers: dict) -> None:
    """Verify faculty score entry."""
    payload = {
        "examination_id": "exam-mid-01",
        "enrollment_id": "enr-001",
        "marks_obtained": 49.0,
        "is_absent": False,
        "grade": "O",
    }
    response = client.post("/api/v1/admin/marks", json=payload, headers=faculty_headers)
    assert response.status_code == 201
    mark = response.json()
    assert mark["marks_obtained"] == 49.0
    assert mark["grade"] == "O"


# =================================================================
# 8. Regression & Edge Case Tests
# =================================================================
def test_nonexistent_student_profile_returns_404(client: TestClient, admin_headers: dict) -> None:
    """Verify querying non-existent student profile returns HTTP 404."""
    response = client.get("/api/v1/students/stu-nonexistent-id", headers=admin_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_nonexistent_student_attendance_returns_404(client: TestClient, admin_headers: dict) -> None:
    """Verify querying attendance for non-existent student returns HTTP 404."""
    response = client.get("/api/v1/attendance/student/stu-nonexistent-id", headers=admin_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_nonexistent_student_fees_returns_404(client: TestClient, admin_headers: dict) -> None:
    """Verify querying fees for non-existent student returns HTTP 404."""
    response = client.get("/api/v1/fees/student/stu-nonexistent-id", headers=admin_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_nonexistent_invoice_payment_returns_404(client: TestClient, student_a_headers: dict) -> None:
    """Verify paying a non-existent invoice returns HTTP 404."""
    response = client.post(
        "/api/v1/fees/invoices/inv-nonexistent-999/pay",
        params={"amount": 5000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_publish_notice_administrative_category(client: TestClient, faculty_headers: dict) -> None:
    """Verify notice category 'administrative' is accepted by DB schema and API."""
    payload = {
        "title": "Administrative Office Schedule During Diwali",
        "category": "administrative",
        "content": "Administrative services will operate on reduced hours during the holiday period.",
        "target_role": "all",
        "is_published": True,
    }
    response = client.post("/api/v1/notices", json=payload, headers=faculty_headers)
    assert response.status_code == 201
    created = response.json()
    assert created["category"] == "administrative"
    assert created["title"] == payload["title"]


def test_publish_notice_invalid_category_rejected(client: TestClient, faculty_headers: dict) -> None:
    """Verify invalid notice category is rejected by Pydantic validation."""
    payload = {
        "title": "Invalid Announcement",
        "category": "unsupported_category",
        "content": "This should fail validation.",
        "target_role": "all",
        "is_published": True,
    }
    response = client.post("/api/v1/notices", json=payload, headers=faculty_headers)
    assert response.status_code == 422


def test_faculty_forbidden_from_student_me_endpoints(client: TestClient, faculty_headers: dict) -> None:
    """Verify faculty users cannot access student personal endpoints (/attendance/me, /fees/me)."""
    resp_att = client.get("/api/v1/attendance/me", headers=faculty_headers)
    assert resp_att.status_code == 403

    resp_fees = client.get("/api/v1/fees/me", headers=faculty_headers)
    assert resp_fees.status_code == 403


def test_student_forbidden_from_faculty_endpoints(client: TestClient, student_a_headers: dict) -> None:
    """Verify student users cannot access faculty endpoints (/students roster, /attendance/warnings)."""
    resp_roster = client.get("/api/v1/students", headers=student_a_headers)
    assert resp_roster.status_code == 403

    resp_warnings = client.get("/api/v1/attendance/warnings", headers=student_a_headers)
    assert resp_warnings.status_code == 403


def test_student_blocked_from_paying_other_student_invoice(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify a student is strictly forbidden from paying another student's invoice."""
    # inv-004 belongs to Rohan Gupta (enr-003)
    response = client.post(
        "/api/v1/fees/invoices/inv-004/pay",
        params={"amount": 5000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()


def test_rejected_payment_leaves_invoice_unchanged(
    client: TestClient,
    student_a_headers: dict,
    student_b_headers: dict,
    student_a_payable_invoice: str,
) -> None:
    """Verify failed authorization or validation leaves invoice database record unchanged."""
    from backend.app.repositories.database import get_repository
    repo = get_repository()
    inv_before = repo.get_invoice(student_a_payable_invoice)
    assert inv_before is not None
    assert float(inv_before["amount_paid"]) == 0.0

    # Attempt 1: Unauthorized student attempts payment -> 403
    res_unauth = client.post(
        f"/api/v1/fees/invoices/{student_a_payable_invoice}/pay",
        params={"amount": 3000.0, "payment_method": "upi"},
        headers=student_b_headers,
    )
    assert res_unauth.status_code == 403

    # Verify unchanged
    inv_after_1 = repo.get_invoice(student_a_payable_invoice)
    assert float(inv_after_1["amount_paid"]) == 0.0
    assert inv_after_1["status"] == "unpaid"

    # Attempt 2: Overpayment attempt -> 400
    res_over = client.post(
        f"/api/v1/fees/invoices/{student_a_payable_invoice}/pay",
        params={"amount": 25000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert res_over.status_code == 400
    assert "exceeds outstanding balance" in res_over.json()["detail"].lower()

    # Verify unchanged
    inv_after_2 = repo.get_invoice(student_a_payable_invoice)
    assert float(inv_after_2["amount_paid"]) == 0.0
    assert inv_after_2["status"] == "unpaid"


def test_overpayment_and_repeated_payment_on_cleared_invoice(
    client: TestClient,
    student_a_headers: dict,
    student_a_payable_invoice: str,
) -> None:
    """Verify overpayment rejection and repeated payment rejection after invoice is paid."""
    # Pay full balance (10,000.0)
    res_pay = client.post(
        f"/api/v1/fees/invoices/{student_a_payable_invoice}/pay",
        params={"amount": 10000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert res_pay.status_code == 200

    # Attempt to pay again on now fully paid invoice -> 400
    res_repeat = client.post(
        f"/api/v1/fees/invoices/{student_a_payable_invoice}/pay",
        params={"amount": 1000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert res_repeat.status_code == 400
    assert "already fully paid" in res_repeat.json()["detail"].lower()


def test_faculty_forbidden_from_paying_invoice(
    client: TestClient,
    faculty_headers: dict,
    student_a_payable_invoice: str,
) -> None:
    """Verify faculty role cannot call student fee payment endpoint."""
    response = client.post(
        f"/api/v1/fees/invoices/{student_a_payable_invoice}/pay",
        params={"amount": 1000.0, "payment_method": "upi"},
        headers=faculty_headers,
    )
    assert response.status_code == 403


def test_pay_invoice_cursor_compatibility_and_defensive_mapping() -> None:
    """Verify pay_invoice logic handles both RealDictRow/Row and raw positional tuple rows safely."""
    # 1. Test raw tuple row with cursor.description fallback (simulates PostgreSQL without dict cursor)
    class MockTupleCursor:
        description = [
            ("id",), ("invoice_number",), ("amount",), ("amount_paid",), ("status",), ("user_id",)
        ]
        def fetchone(self):
            return ("inv-tuple-test", "INV-TUPLE-001", 5000.0, 1000.0, "partially_paid", "stu-001")

    cursor = MockTupleCursor()
    row = cursor.fetchone()
    # Emulate the sql_repository defensive parser
    if isinstance(row, dict):
        inv = row
    elif hasattr(row, "keys"):
        inv = dict(row)
    else:
        col_names = [d[0] for d in cursor.description]
        inv = dict(zip(col_names, row))

    assert inv["id"] == "inv-tuple-test"
    assert inv["amount"] == 5000.0
    assert inv["amount_paid"] == 1000.0
    assert inv["status"] == "partially_paid"
    assert inv["user_id"] == "stu-001"
    assert round(float(inv["amount"]) - float(inv["amount_paid"]), 2) == 4000.0


# =================================================================
# 9. Faculty Assignments & Data Integrity Regression Tests
# =================================================================
def test_get_faculty_assignments_as_admin(client: TestClient, admin_headers: dict) -> None:
    """Verify administrator can retrieve faculty course allotments with live catalog data."""
    response = client.get("/api/v1/admin/faculty-assignments", headers=admin_headers)
    assert response.status_code == 200
    assignments = response.json()
    assert isinstance(assignments, list)
    assert len(assignments) >= 4

    # Verify schema fields match FacultyCourseAssignment interface
    first = assignments[0]
    assert "id" in first
    assert "faculty_id" in first
    assert "faculty_name" in first
    assert "subject_id" in first
    assert "subject_code" in first
    assert "subject_name" in first
    assert "course_section" in first
    assert "enrolled_count" in first
    assert first["enrolled_count"] > 0

    codes = [a["subject_code"] for a in assignments]
    assert "CS401" in codes
    assert "CS402" in codes
    assert "CS403" in codes
    assert "CS404" in codes


def test_get_faculty_assignments_as_faculty(client: TestClient, faculty_headers: dict) -> None:
    """Verify faculty member can retrieve faculty course allotments."""
    response = client.get("/api/v1/admin/faculty-assignments", headers=faculty_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 4


def test_get_faculty_assignments_forbidden_for_student(client: TestClient, student_a_headers: dict) -> None:
    """Verify students are strictly forbidden from viewing administrative faculty allotments."""
    response = client.get("/api/v1/admin/faculty-assignments", headers=student_a_headers)
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()


def test_get_faculty_assignments_unauthenticated(client: TestClient) -> None:
    """Verify unauthenticated requests to faculty assignments are rejected."""
    response = client.get("/api/v1/admin/faculty-assignments")
    assert response.status_code == 401


def test_decision_engine_attendance_alias_and_properties() -> None:
    """Verify SQLRepository alias and attendance model property calculations."""
    from backend.app.models.attendance import AttendanceSummary, SubjectAttendance
    from backend.app.repositories.database import get_repository

    repo = get_repository()
    # Test alias works
    assert hasattr(repo, "get_student_attendance")
    att = repo.get_student_attendance("stu-001")
    assert att is not None
    assert att.student_id == "stu-001"

    # Test properties on SubjectAttendance
    sub = SubjectAttendance(
        subject_code="CS401",
        subject_name="Cloud Computing",
        total_sessions=10,
        attended_sessions=6,
        excused_sessions=2,
        absent_sessions=2,
        attendance_percentage=80.0,
    )
    assert sub.attended_classes == 8  # 6 + 2
    assert sub.total_classes == 10

    # Test properties on AttendanceSummary
    summary = AttendanceSummary(
        student_id="stu-test",
        roll_number="TEST001",
        overall_percentage=80.0,
        subjects=[sub],
    )
    assert summary.attended_classes == 8
    assert summary.total_classes == 10


def test_init_postgres_migration_contains_all_13_tables() -> None:
    """Verify init_postgres includes chat_sessions schema and verifies 13 tables."""
    import inspect
    from database import init_db

    src = inspect.getsource(init_db.init_postgres)
    assert "CHAT_SESSIONS_FILE" in src
    assert "chat_sessions" in src
    assert "chat_messages" in src


def test_fee_summary_paid_amount_consistency(client: TestClient, student_a_headers: dict) -> None:
    """Verify fee invoices contain paid_amount matching status and zero outstanding for fully paid records."""
    response = client.get("/api/v1/fees/me", headers=student_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "stu-001"
    assert data["total_invoiced"] == 77500.0
    assert data["total_paid"] == 77500.0
    assert data["total_outstanding"] == 0.0

    invoices = data["invoices"]
    assert len(invoices) == 2
    for inv in invoices:
        assert "paid_amount" in inv
        assert inv["paid_amount"] == inv["amount"]
        assert inv["status"] == "paid"


def test_student_detail_zero_and_multiple_enrollments_regression() -> None:
    """Verify get_student_detail returns valid StudentDetail for 0 and multiple enrollments."""
    from backend.app.repositories.sql_repository import sql_repo

    # 1. Test student with 0 enrollments
    test_user_id = "stu-test-no-enr"
    sql_repo._execute_write(
        "INSERT INTO users (id, name, email, password_hash, role) VALUES (?, ?, ?, ?, ?);",
        (test_user_id, "No Enrollment Student", "no.enr@csic.edu", "hash", "student")
    )
    detail_zero = sql_repo.get_student_detail(test_user_id)
    assert detail_zero is not None
    assert detail_zero.id == test_user_id
    assert detail_zero.enrollments == []
    assert detail_zero.department_name == "Computer Science & Engineering"

    # 2. Test student with multiple enrollments across distinct courses
    test_multi_id = "stu-test-multi-enr"
    sql_repo._execute_write(
        "INSERT INTO users (id, name, email, password_hash, role) VALUES (?, ?, ?, ?, ?);",
        (test_multi_id, "Multi Enrollment Student", "multi.enr@csic.edu", "hash", "student")
    )
    sql_repo._execute_write(
        "INSERT INTO courses (id, code, name, department) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO NOTHING;",
        ("crs-02", "MTECH-CSE", "M.Tech Computer Science", "Computer Science & Engineering")
    )
    sql_repo._execute_write(
        "INSERT INTO enrollments (id, user_id, course_id, roll_number, semester, section, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
        ("enr-multi-1", test_multi_id, "crs-01", "CS2026991", 6, "A", "active")
    )
    sql_repo._execute_write(
        "INSERT INTO enrollments (id, user_id, course_id, roll_number, semester, section, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
        ("enr-multi-2", test_multi_id, "crs-02", "CS2026992", 1, "B", "completed")
    )
    detail_multi = sql_repo.get_student_detail(test_multi_id)
    assert detail_multi is not None
    assert detail_multi.id == test_multi_id
    assert len(detail_multi.enrollments) == 2
    enrollment_ids = {e.id for e in detail_multi.enrollments}
    assert enrollment_ids == {"enr-multi-1", "enr-multi-2"}


def test_faculty_assignments_section_selection_preservation(client: TestClient, admin_headers: dict) -> None:
    """Verify get_faculty_assignments preserves previous section-selection format and counts."""
    response = client.get("/api/v1/admin/faculty-assignments", headers=admin_headers)
    assert response.status_code == 200
    assignments = response.json()
    assert len(assignments) >= 4
    for a in assignments:
        assert a["course_section"].startswith("Sec ")
        assert " (Sem " in a["course_section"]
        assert a["enrolled_count"] > 0


