"""Tests for authentication and token validation."""
from fastapi.testclient import TestClient

from backend.app.core.security import create_access_token, decode_access_token


def test_valid_student_login(client: TestClient) -> None:
    """Verify student logins succeed for Rashi, Vanshika, Silki, and Akshit with password 1234 and issue bearer tokens."""
    for student_email, expected_id in [
        ("rashi@csic.edu", "stu-001"),
        ("vanshika@csic.edu", "stu-002"),
        ("silki@csic.edu", "stu-003"),
        ("akshit@csic.edu", "stu-004"),
    ]:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": student_email, "password": "1234"},
        )
        assert response.status_code == 200, f"Login failed for {student_email}: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

        # Verify token payload
        decoded = decode_access_token(data["access_token"])
        assert decoded["sub"] == expected_id
        assert decoded["role"] == "student"


def test_valid_faculty_login(client: TestClient) -> None:
    """Verify faculty login succeeds with faculty role and password 1234."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "rajesh.kumar@csic.edu", "password": "1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    decoded = decode_access_token(data["access_token"])
    assert decoded["role"] == "faculty"


def test_valid_admin_login(client: TestClient) -> None:
    """Verify administrator login succeeds with admin role and password 1234."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@csic.edu", "password": "1234"},
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
        json={"email": "rashi@csic.edu", "password": "WrongPassword!"},
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
    assert data["email"] == "rashi@csic.edu"
    assert data["role"] == "student"


def test_get_current_user_unauthenticated(client: TestClient) -> None:
    """Verify /auth/me without token returns HTTP 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_login_contract_and_profile_retrieval_all_roles(client: TestClient) -> None:
    """Verify frontend/backend login contract and user profile retrieval for students, faculty, and admin."""
    roles_credentials = [
        ("rashi@csic.edu", "1234", "student", "Rashi"),
        ("vanshika@csic.edu", "1234", "student", "Vanshika"),
        ("silki@csic.edu", "1234", "student", "Silki"),
        ("akshit@csic.edu", "1234", "student", "Akshit"),
        ("rajesh.kumar@csic.edu", "1234", "faculty", "Akshit"),
        ("anita.deshmukh@csic.edu", "1234", "faculty", "Prof. Anita Deshmukh"),
        ("admin@csic.edu", "1234", "admin", "Akshit"),
    ]
    for email, password, expected_role, expected_name in roles_credentials:
        # Step 1: Login
        login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_res.status_code == 200, f"Login failed for {email}: {login_res.text}"
        login_data = login_res.json()

        # Contract assertion
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"
        assert login_data["expires_in"] == 86400
        token = login_data["access_token"]
        assert len(token) > 20

        # Step 2: Retrieve profile using access_token
        auth_headers = {"Authorization": f"Bearer {token}"}
        profile_res = client.get("/api/v1/auth/me", headers=auth_headers)
        assert profile_res.status_code == 200
        profile = profile_res.json()
        assert profile["email"] == email
        assert profile["role"] == expected_role
        assert profile["full_name"] == expected_name
        assert profile["is_active"] is True
