"""Validation error response tests (HTTP 422 Unprocessable Entity)."""
from fastapi.testclient import TestClient


def test_login_validation_error_empty_body(client: TestClient) -> None:
    """Verify missing required fields in login returns HTTP 422."""
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Pydantic validation errors detail
    field_errors = [err["loc"][-1] for err in data["detail"]]
    assert "email" in field_errors
    assert "password" in field_errors


def test_admin_create_student_invalid_email(client: TestClient, admin_headers: dict) -> None:
    """Verify invalid email string fails Pydantic schema validation with 422."""
    payload = {
        "email": "not-an-email",
        "password": "validPassword123",
        "full_name": "Test User",
        "roll_number": "CS9999",
        "program_code": "BTECH_CSE",
    }
    response = client.post("/api/v1/admin/students", json=payload, headers=admin_headers)
    assert response.status_code == 422
    data = response.json()
    assert any("email" in err["loc"] for err in data["detail"])


def test_admin_create_student_short_password(client: TestClient, admin_headers: dict) -> None:
    """Verify password shorter than minimum length fails with 422."""
    payload = {
        "email": "valid@csic.edu",
        "password": "123",  # min_length is 6
        "full_name": "Test User",
        "roll_number": "CS9999",
        "program_code": "BTECH_CSE",
    }
    response = client.post("/api/v1/admin/students", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_marks_input_negative_score_rejected(client: TestClient, faculty_headers: dict) -> None:
    """Verify negative marks score is rejected with HTTP 422."""
    payload = {
        "examination_id": "exam-mid-01",
        "enrollment_id": "enr-001",
        "marks_obtained": -15.0,  # ge=0.0 constraint
    }
    response = client.post("/api/v1/admin/marks", json=payload, headers=faculty_headers)
    assert response.status_code == 422


def test_pay_invoice_negative_amount_rejected(client: TestClient, student_a_headers: dict) -> None:
    """Verify negative or zero payment amount is rejected with HTTP 422."""
    response = client.post(
        "/api/v1/fees/invoices/inv-001/pay",
        params={"amount": -100.0},
        headers=student_a_headers,
    )
    assert response.status_code == 422


def test_publish_notice_short_content_rejected(client: TestClient, faculty_headers: dict) -> None:
    """Verify notice with content below min length is rejected with 422."""
    payload = {
        "title": "Valid Notice Title",
        "category": "academic",
        "content": "Hi",  # min_length is 5
    }
    response = client.post("/api/v1/notices", json=payload, headers=faculty_headers)
    assert response.status_code == 422
