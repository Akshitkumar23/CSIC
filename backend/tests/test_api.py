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
    assert data["full_name"] == "Aarav Sharma"
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


def test_pay_fee_invoice(client: TestClient, student_a_headers: dict) -> None:
    """Verify simulated fee payment endpoint creates valid transaction."""
    response = client.post(
        "/api/v1/fees/invoices/inv-003/pay",
        params={"amount": 15000.0, "payment_method": "upi"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    payment = response.json()
    assert payment["invoice_id"] == "inv-003"
    assert payment["amount_paid"] == 15000.0
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
    assert created["published_by_name"] == "Dr. Rajesh Kumar"


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
