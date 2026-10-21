"""Tests for Search Information Module (Feature Gap 1).

Validates:
- Unauthenticated access returns HTTP 401
- Authenticated retrieval of seeded records (Syllabus, Timetable, Results, Fees, FAQ)
- Filter by branch (exact and alias like CSE)
- Filter by year (1-4)
- Empty results for non-matching criteria
- Pydantic/FastAPI validation error HTTP 422 for invalid year values (< 1 or > 4)
- Filter by category and subject
- Full-text keyword search across title, content_details, and subject
- Role access for students and faculty
"""
from fastapi.testclient import TestClient


def test_search_unauthorized(client: TestClient) -> None:
    """Verify unauthenticated request returns HTTP 401 Unauthorized."""
    response = client.get("/api/v1/search")
    assert response.status_code == 401


def test_search_all_records_authenticated(client: TestClient, student_a_headers: dict) -> None:
    """Verify authenticated student can retrieve all seeded institutional records."""
    response = client.get("/api/v1/search", headers=student_a_headers)
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 5

    item_ids = {item["id"] for item in items}
    expected_ids = {"info-001", "info-002", "info-003", "info-004", "info-005"}
    assert expected_ids.issubset(item_ids)

    # Verify schema structure of seeded records
    sample = next(item for item in items if item["id"] == "info-001")
    assert sample["branch"] == "Computer Science & Engineering"
    assert sample["year"] == 3
    assert sample["category"] == "Syllabus"
    assert "Cloud Computing" in sample["subject"]
    assert "CS401" in sample["title"]
    assert "Virtualization" in sample["content_details"]
    assert sample["file_url"] == "/docs/syllabus/cs401_syllabus.pdf"
    assert "created_at" in sample


def test_search_filter_by_branch(client: TestClient, student_a_headers: dict) -> None:
    """Verify branch filtering with full name, alias CSE, and unmatched branch."""
    # Full branch name
    resp1 = client.get("/api/v1/search?branch=Computer%20Science%20%26%20Engineering", headers=student_a_headers)
    assert resp1.status_code == 200
    assert len(resp1.json()) >= 5

    # Acronym alias CSE
    resp2 = client.get("/api/v1/search?branch=CSE", headers=student_a_headers)
    assert resp2.status_code == 200
    assert len(resp2.json()) >= 5

    # Non-existent branch returns empty list
    resp3 = client.get("/api/v1/search?branch=Mechanical%20Engineering", headers=student_a_headers)
    assert resp3.status_code == 200
    assert len(resp3.json()) == 0


def test_search_filter_by_year(client: TestClient, student_a_headers: dict) -> None:
    """Verify year filtering returns year-matched records and empty list for unused year."""
    # Year 3 has 5 seeded records
    resp3 = client.get("/api/v1/search?year=3", headers=student_a_headers)
    assert resp3.status_code == 200
    assert len(resp3.json()) >= 5

    # Year 1 has 0 records
    resp1 = client.get("/api/v1/search?year=1", headers=student_a_headers)
    assert resp1.status_code == 200
    assert len(resp1.json()) == 0


def test_search_invalid_year_validation(client: TestClient, student_a_headers: dict) -> None:
    """Verify year outside 1-4 triggers FastAPI 422 Unprocessable Entity."""
    # Year 0 (below min 1)
    resp_zero = client.get("/api/v1/search?year=0", headers=student_a_headers)
    assert resp_zero.status_code == 422

    # Year 5 (above max 4)
    resp_five = client.get("/api/v1/search?year=5", headers=student_a_headers)
    assert resp_five.status_code == 422

    # Negative year
    resp_neg = client.get("/api/v1/search?year=-1", headers=student_a_headers)
    assert resp_neg.status_code == 422

    # Non-integer year
    resp_alpha = client.get("/api/v1/search?year=third", headers=student_a_headers)
    assert resp_alpha.status_code == 422


def test_search_filter_by_category(client: TestClient, student_a_headers: dict) -> None:
    """Verify filtering by each of the 5 reference categories."""
    categories = {
        "Syllabus": "info-001",
        "Timetable": "info-002",
        "Results": "info-003",
        "Fees": "info-004",
        "FAQ": "info-005",
    }
    for cat, expected_id in categories.items():
        resp = client.get(f"/api/v1/search?category={cat}", headers=student_a_headers)
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) >= 1
        ids = [item["id"] for item in items]
        assert expected_id in ids
        for item in items:
            assert item["category"].lower() == cat.lower()


def test_search_filter_by_subject(client: TestClient, student_a_headers: dict) -> None:
    """Verify subject filtering by exact or partial name."""
    resp = client.get("/api/v1/search?subject=Cloud%20Computing", headers=student_a_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert any("Cloud Computing" in item["subject"] for item in items)

    # Non-existent subject
    resp_none = client.get("/api/v1/search?subject=Quantum%20Teleportation", headers=student_a_headers)
    assert resp_none.status_code == 200
    assert len(resp_none.json()) == 0


def test_search_text_query(client: TestClient, student_a_headers: dict) -> None:
    """Verify text keyword search matching title and content_details."""
    # Content detail search: "Virtualization" in info-001
    resp_content = client.get("/api/v1/search?q=Virtualization", headers=student_a_headers)
    assert resp_content.status_code == 200
    assert any(item["id"] == "info-001" for item in resp_content.json())

    # Title search: "Datesheet" / "Mid-Term" in info-003
    resp_title = client.get("/api/v1/search?q=Mid-Term", headers=student_a_headers)
    assert resp_title.status_code == 200
    assert any(item["id"] == "info-003" for item in resp_title.json())

    # No match keyword
    resp_empty = client.get("/api/v1/search?q=nonexistentxyz123", headers=student_a_headers)
    assert resp_empty.status_code == 200
    assert len(resp_empty.json()) == 0


def test_search_combined_filters(client: TestClient, student_a_headers: dict) -> None:
    """Verify combining multiple filters narrows down to exact item."""
    resp = client.get(
        "/api/v1/search?branch=CSE&year=3&category=Syllabus&subject=Cloud",
        headers=student_a_headers,
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["id"] == "info-001"


def test_search_access_for_faculty(client: TestClient, faculty_headers: dict) -> None:
    """Verify faculty can also search institutional information."""
    resp = client.get("/api/v1/search", headers=faculty_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 5


def test_search_partial_category_and_branch_matching(client: TestClient, student_a_headers: dict) -> None:
    """Verify partial category and branch search strings match expected records."""
    # Partial category matching
    resp_syll = client.get("/api/v1/search?category=syll", headers=student_a_headers)
    assert resp_syll.status_code == 200
    assert any(item["id"] == "info-001" for item in resp_syll.json())

    resp_fee = client.get("/api/v1/search?category=fee", headers=student_a_headers)
    assert resp_fee.status_code == 200
    assert any(item["id"] == "info-004" for item in resp_fee.json())

    # Partial branch matching
    resp_branch_cs = client.get("/api/v1/search?branch=Computer%20Science", headers=student_a_headers)
    assert resp_branch_cs.status_code == 200
    assert len(resp_branch_cs.json()) >= 5

    resp_branch_eng = client.get("/api/v1/search?branch=Engineering", headers=student_a_headers)
    assert resp_branch_eng.status_code == 200
    assert len(resp_branch_eng.json()) >= 5
