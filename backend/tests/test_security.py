"""Security and authorization boundary tests.

Verifies:
1. Student cannot access another student's private data (HTTP 403 Forbidden).
2. Unauthenticated requests are rejected (HTTP 401 Unauthorized).
3. Role-based access control enforces student, faculty, and admin privileges.
"""
from fastapi.testclient import TestClient


def test_unauthenticated_requests_return_401(client: TestClient) -> None:
    """Verify unauthenticated requests to protected routes return HTTP 401."""
    protected_endpoints = [
        "/api/v1/students/me",
        "/api/v1/attendance/me",
        "/api/v1/marks/me",
        "/api/v1/fees/me",
        "/api/v1/timetable/me",
        "/api/v1/admin/stats",
    ]
    for url in protected_endpoints:
        response = client.get(url)
        assert response.status_code == 401, f"Expected 401 for {url}, got {response.status_code}"


def test_malformed_token_returns_401(client: TestClient) -> None:
    """Verify invalid or corrupted bearer tokens return HTTP 401."""
    headers = {"Authorization": "Bearer malformed.invalid.token"}
    response = client.get("/api/v1/students/me", headers=headers)
    assert response.status_code == 401


def test_negative_security_student_cannot_access_other_student_profile(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify Student A cannot inspect Student B's profile (HTTP 403)."""
    # Student A (stu-001) attempting to access Student B (stu-002)
    response = client.get("/api/v1/students/stu-002", headers=student_a_headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_negative_security_student_cannot_access_other_student_attendance(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify Student A cannot inspect Student B's attendance metrics (HTTP 403)."""
    response = client.get("/api/v1/attendance/student/stu-002", headers=student_a_headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_negative_security_student_cannot_access_other_student_marks(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify Student A cannot inspect Student B's examination marks (HTTP 403)."""
    response = client.get("/api/v1/marks/student/stu-002", headers=student_a_headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_negative_security_student_cannot_access_other_student_fees(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify Student A cannot inspect Student B's fee invoices (HTTP 403)."""
    response = client.get("/api/v1/fees/student/stu-002", headers=student_a_headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_negative_security_student_cannot_access_other_student_timetable(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify Student A cannot inspect Student B's timetable (HTTP 403)."""
    response = client.get("/api/v1/timetable/student/stu-002", headers=student_a_headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_student_can_access_own_data_by_id(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify Student A can access their own data via parameterized endpoints."""
    response = client.get("/api/v1/students/stu-001", headers=student_a_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "stu-001"


def test_faculty_can_access_any_student_data(
    client: TestClient,
    faculty_headers: dict,
) -> None:
    """Verify Faculty instructor can access any student's records."""
    response = client.get("/api/v1/students/stu-001", headers=faculty_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "stu-001"


def test_admin_can_access_any_student_data(
    client: TestClient,
    admin_headers: dict,
) -> None:
    """Verify Administrator can access any student's records."""
    response = client.get("/api/v1/students/stu-002", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "stu-002"


def test_student_forbidden_from_admin_endpoints(
    client: TestClient,
    student_a_headers: dict,
) -> None:
    """Verify regular student receives HTTP 403 on admin endpoints."""
    response = client.get("/api/v1/admin/stats", headers=student_a_headers)
    assert response.status_code == 403


def test_faculty_forbidden_from_admin_stats(
    client: TestClient,
    faculty_headers: dict,
) -> None:
    """Verify faculty member cannot access admin stats."""
    response = client.get("/api/v1/admin/stats", headers=faculty_headers)
    assert response.status_code == 403


def test_admin_authorized_for_admin_endpoints(
    client: TestClient,
    admin_headers: dict,
) -> None:
    """Verify administrator succeeds on admin endpoints."""
    response = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "pending_fees_amount" in data
