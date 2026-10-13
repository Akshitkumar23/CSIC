"""Tests for authentication and token validation."""
from fastapi.testclient import TestClient

from backend.app.core.security import create_access_token, decode_access_token


def test_valid_student_login(client: TestClient) -> None:
    """Verify student login succeeds and issues bearer token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "aarav.sharma@csic.edu", "password": "Student@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

    # Verify token payload
    decoded = decode_access_token(data["access_token"])
    assert decoded["sub"] == "stu-001"
    assert decoded["role"] == "student"


def test_valid_faculty_login(client: TestClient) -> None:
    """Verify faculty login succeeds with faculty role."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.kumar@csic.edu", "password": "Faculty@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    decoded = decode_access_token(data["access_token"])
    assert decoded["role"] == "faculty"


def test_valid_admin_login(client: TestClient) -> None:
    """Verify administrator login succeeds with admin role."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@csic.edu", "password": "Admin@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    decoded = decode_access_token(data["access_token"])
    assert decoded["role"] == "admin"


def test_invalid_password_returns_401(client: TestClient) -> None:
    """Verify invalid password returns HTTP 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "aarav.sharma@csic.edu", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_nonexistent_email_returns_401(client: TestClient) -> None:
    """Verify unregistered email returns HTTP 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@csic.edu", "password": "SomePassword123"},
    )
    assert response.status_code == 401


def test_get_current_user_profile(client: TestClient, student_a_headers: dict) -> None:
    """Verify /auth/me returns authenticated student attributes."""
    response = client.get("/api/v1/auth/me", headers=student_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "stu-001"
    assert data["email"] == "aarav.sharma@csic.edu"
    assert data["role"] == "student"


def test_get_current_user_unauthenticated(client: TestClient) -> None:
    """Verify /auth/me without token returns HTTP 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
