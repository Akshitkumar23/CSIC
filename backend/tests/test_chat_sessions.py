"""Tests for Multi-Session Chat, Persistence, and Multi-Turn Context Resolution."""
import pytest
from fastapi.testclient import TestClient


def test_create_and_list_sessions(client: TestClient, student_a_headers: dict):
    """Verify creating, listing, and getting messages for a session."""
    # Create new session
    resp = client.post(
        "/api/v1/chat/sessions",
        json={"title": "Academic Advising Session"},
        headers=student_a_headers,
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "Academic Advising Session"
    session_id = created["id"]

    # List sessions
    list_resp = client.get("/api/v1/chat/sessions", headers=student_a_headers)
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert any(s["id"] == session_id for s in sessions)

    # Post message into this session
    msg_resp = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my attendance?", "session_id": session_id},
        headers=student_a_headers,
    )
    assert msg_resp.status_code == 200
    assert msg_resp.json()["session_id"] == session_id

    # Retrieve session messages
    msgs_resp = client.get(f"/api/v1/chat/sessions/{session_id}/messages", headers=student_a_headers)
    assert msgs_resp.status_code == 200
    msgs = msgs_resp.json()
    assert len(msgs) >= 2
    assert msgs[0]["sender"] == "user"
    assert msgs[1]["sender"] == "bot"


def test_multi_turn_follow_up_context(client: TestClient, student_a_headers: dict):
    """Verify follow-up inquiries like 'What about CS401?' and 'How many classes to recover?' maintain context."""
    # Create session
    sess_resp = client.post(
        "/api/v1/chat/sessions",
        json={"title": "Multi-Turn Attendance Exploration"},
        headers=student_a_headers,
    )
    assert sess_resp.status_code == 201
    session_id = sess_resp.json()["id"]

    # Turn 1: Broad question
    t1 = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my attendance?", "session_id": session_id},
        headers=student_a_headers,
    )
    assert t1.status_code == 200
    assert t1.json()["query_type"] == "attendance"

    # Turn 2: Follow-up referencing only subject code
    t2 = client.post(
        "/api/v1/chat/message",
        json={"message": "What about CS401?", "session_id": session_id},
        headers=student_a_headers,
    )
    assert t2.status_code == 200
    data2 = t2.json()
    assert data2["query_type"] == "attendance"
    assert "CS401" in data2["reply"]
    assert "Cloud Computing" in data2["reply"]

    # Turn 3: Follow-up question asking about recovery
    t3 = client.post(
        "/api/v1/chat/message",
        json={"message": "How many classes to recover?", "session_id": session_id},
        headers=student_a_headers,
    )
    assert t3.status_code == 200
    data3 = t3.json()
    assert data3["query_type"] == "attendance"
    assert "CS401" in data3["reply"]


def test_session_data_isolation(client: TestClient, student_a_headers: dict, student_b_headers: dict):
    """Verify Student B cannot view or delete Student A's chat session."""
    # Student A creates session
    resp = client.post(
        "/api/v1/chat/sessions",
        json={"title": "Student A Private Chat"},
        headers=student_a_headers,
    )
    assert resp.status_code == 201
    session_id = resp.json()["id"]

    # Student B attempts to read session messages
    leak_resp = client.get(f"/api/v1/chat/sessions/{session_id}/messages", headers=student_b_headers)
    assert leak_resp.status_code == 200
    # Must be empty because Student B does not own this session
    assert len(leak_resp.json()) == 0

    # Student B attempts to delete Student A's session
    del_resp = client.delete(f"/api/v1/chat/sessions/{session_id}", headers=student_b_headers)
    # Delete endpoint succeeds silently or with 204, but query verified session still exists for Student A
    list_a = client.get("/api/v1/chat/sessions", headers=student_a_headers)
    assert any(s["id"] == session_id for s in list_a.json())

    # Clean delete by Student A
    del_a = client.delete(f"/api/v1/chat/sessions/{session_id}", headers=student_a_headers)
    assert del_a.status_code == 204
    list_a_after = client.get("/api/v1/chat/sessions", headers=student_a_headers)
    assert not any(s["id"] == session_id for s in list_a_after.json())
