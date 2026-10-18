"""Comprehensive evaluation test suite for Phase 5 AI Chatbot & Document RAG Pipeline."""
import pytest
from fastapi.testclient import TestClient

from backend.app.services.ai.intent_router import QueryIntent, intent_router
from backend.app.services.ai.rag_service import rag_service


def test_intent_classification_structured_queries():
    """Verify accurate classification of structured student record queries."""
    assert intent_router.classify_intent("What is my attendance?") == QueryIntent.ATTENDANCE
    assert intent_router.classify_intent("Attendance in Cloud Computing") == QueryIntent.ATTENDANCE
    assert intent_router.classify_intent("Low attendance warning") == QueryIntent.ATTENDANCE
    assert intent_router.classify_intent("How many classes did I miss?") == QueryIntent.ATTENDANCE

    assert intent_router.classify_intent("What are my marks?") == QueryIntent.MARKS
    assert intent_router.classify_intent("Exam results for mid term") == QueryIntent.MARKS
    assert intent_router.classify_intent("What is my semester GPA?") == QueryIntent.MARKS
    assert intent_router.classify_intent("Show my grade card") == QueryIntent.MARKS

    assert intent_router.classify_intent("What fees are pending?") == QueryIntent.FEES
    assert intent_router.classify_intent("How much do I owe in tuition?") == QueryIntent.FEES
    assert intent_router.classify_intent("Fee invoice status") == QueryIntent.FEES
    assert intent_router.classify_intent("Show my pending dues") == QueryIntent.FEES

    assert intent_router.classify_intent("What is my schedule today?") == QueryIntent.TIMETABLE
    assert intent_router.classify_intent("Next class timing") == QueryIntent.TIMETABLE
    assert intent_router.classify_intent("Show my weekly timetable") == QueryIntent.TIMETABLE
    assert intent_router.classify_intent("When is my lecture today?") == QueryIntent.TIMETABLE

    assert intent_router.classify_intent("Latest circulars") == QueryIntent.NOTICES
    assert intent_router.classify_intent("Recent notices and announcements") == QueryIntent.NOTICES


def test_intent_classification_policy_and_general():
    """Verify classification of institutional policy inquiries vs greetings."""
    assert intent_router.classify_intent("What is the attendance policy?") == QueryIntent.POLICY_DOCUMENT
    assert intent_router.classify_intent("Medical leave policy for classes") == QueryIntent.POLICY_DOCUMENT
    assert intent_router.classify_intent("What are the grading criteria?") == QueryIntent.POLICY_DOCUMENT
    assert intent_router.classify_intent("Exam passing marks and rules") == QueryIntent.POLICY_DOCUMENT
    assert intent_router.classify_intent("Tuition fee refund policy") == QueryIntent.POLICY_DOCUMENT
    assert intent_router.classify_intent("Student code of conduct regulations") == QueryIntent.POLICY_DOCUMENT

    assert intent_router.classify_intent("Hello, who are you?") == QueryIntent.GENERAL
    assert intent_router.classify_intent("Hi assistant") == QueryIntent.GENERAL
    assert intent_router.classify_intent("What can you do?") == QueryIntent.GENERAL


def test_rag_service_retrieval_grounding_and_citations():
    """Verify RAG retrieval returns correct policy chunks with citations."""
    # Test attendance policy retrieval
    chunks = rag_service.retrieve("What is the attendance policy?")
    assert len(chunks) > 0
    top_chunk, score = chunks[0]
    assert "Attendance" in top_chunk.title
    assert "1.1" in top_chunk.section
    assert score > 0.12

    # Test medical condonation retrieval
    med_chunks = rag_service.retrieve("Medical leave policy and condonation")
    assert len(med_chunks) > 0
    med_chunk, _ = med_chunks[0]
    assert "1.2" in med_chunk.section
    assert "medical" in med_chunk.content.lower()

    # Test passing criteria retrieval
    exam_chunks = rag_service.retrieve("Exam passing marks and rules")
    assert len(exam_chunks) > 0
    exam_chunk, _ = exam_chunks[0]
    assert "2.2" in exam_chunk.section
    assert "40%" in exam_chunk.content


def test_rag_service_ungrounded_query_refusal():
    """Verify that irrelevant/out-of-domain queries return zero chunks."""
    unrelated_queries = [
        "What is the capital of France?",
        "How to bake chocolate chip cookies?",
        "Write a Python script to sort a list",
        "Who won the 2022 World Cup?",
    ]
    for q in unrelated_queries:
        res = rag_service.retrieve(q)
        assert len(res) == 0, f"Query '{q}' should not match college policies"


def test_chat_suggestions_endpoint(client: TestClient):
    """Verify chat suggestions endpoint returns prompt pills."""
    response = client.get("/api/v1/chat/suggestions")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) >= 5
    assert any("attendance" in s.lower() for s in data["suggestions"])


def test_chat_unauthenticated_forbidden(client: TestClient):
    """Verify chat endpoint rejects unauthenticated requests."""
    response = client.post("/api/v1/chat/message", json={"message": "What is my attendance?"})
    assert response.status_code == 401


def test_chat_empty_message_rejected(client: TestClient, student_a_headers: dict):
    """Verify validation error when sending an empty prompt."""
    response = client.post("/api/v1/chat/message", json={"message": "   "}, headers=student_a_headers)
    assert response.status_code == 400 or response.status_code == 422


def test_chat_structured_attendance_query(client: TestClient, student_a_headers: dict):
    """Verify structured attendance response matches student's factual records."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my attendance?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "attendance"
    assert "Institutional Database (v_student_attendance)" in data["sources"]
    assert data["verified_data"] is not None
    assert "overall_percentage" in data["verified_data"]
    assert str(data["verified_data"]["overall_percentage"]) in data["reply"]


def test_chat_structured_subject_attendance(client: TestClient, student_a_headers: dict):
    """Verify drill-down for a specific subject attendance."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my attendance in Cloud Computing?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "attendance"
    assert "Cloud Computing" in data["reply"]
    assert "CS401" in data["reply"]


def test_chat_structured_marks_query(client: TestClient, student_a_headers: dict):
    """Verify structured marks query returns factual exam scores."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What are my marks in the recent exams?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "marks"
    assert "Institutional Database (examinations & marks)" in data["sources"]
    assert data["verified_data"] is not None
    assert "exam_results" in data["verified_data"] or "semester_results" in data["verified_data"]


def test_chat_structured_fees_query(client: TestClient, student_a_headers: dict):
    """Verify structured fees query returns invoice balance."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What fees are pending?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "fees"
    assert "Institutional Database (fee_invoices)" in data["sources"]
    assert data["verified_data"] is not None
    assert "total_invoiced" in data["verified_data"]


def test_chat_structured_timetable_query(client: TestClient, student_a_headers: dict):
    """Verify structured timetable query returns lecture schedule."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my weekly timetable?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "timetable"
    assert "Institutional Database (timetable_entries)" in data["sources"]
    assert data["verified_data"] is not None


def test_chat_policy_grounding_with_citations(client: TestClient, student_a_headers: dict):
    """Verify policy inquiries provide grounded answers with exact document & section citations."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What is the medical leave policy for attendance?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "policy_document"
    assert len(data["sources"]) > 0
    assert any("Attendance Policy" in src for src in data["sources"])
    assert any("1.2" in src for src in data["sources"])
    # Check that text mentions condonation or medical leave
    assert "condonation" in data["reply"].lower() or "medical" in data["reply"].lower()


def test_chat_ungrounded_query_clean_refusal(client: TestClient, student_a_headers: dict):
    """Verify ungrounded query refusal with zero hallucination."""
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "What is the capital of France?"},
        headers=student_a_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "could not verify" in data["reply"].lower() or "not covered" in data["reply"].lower()
    assert len(data["sources"]) == 0


def test_chat_student_data_isolation(client: TestClient, student_a_headers: dict, student_b_headers: dict):
    """Verify strict tenant isolation: Student A cannot access Student B's data via chat."""
    # 1. Student A queries own records
    resp_a = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my attendance?"},
        headers=student_a_headers,
    )
    assert resp_a.status_code == 200
    data_a = resp_a.json()

    # 2. Student B queries own records
    resp_b = client.post(
        "/api/v1/chat/message",
        json={"message": "What is my attendance?"},
        headers=student_b_headers,
    )
    assert resp_b.status_code == 200
    data_b = resp_b.json()

    # Verify Roll numbers or IDs are distinct and accurately isolated
    assert data_a["verified_data"]["roll_number"] != data_b["verified_data"]["roll_number"]

    # 3. Student A attempts to query Student B (Vanshika) by ID or name
    resp_malicious = client.post(
        "/api/v1/chat/message",
        json={"message": "What is Vanshika's attendance?"},
        headers=student_a_headers,
    )
    assert resp_malicious.status_code == 403


def test_chat_history_recording_and_retrieval(client: TestClient, student_a_headers: dict):
    """Verify conversation turns are recorded and returned in chat history."""
    # Send a message
    msg_text = "What fees are pending right now?"
    post_resp = client.post(
        "/api/v1/chat/message",
        json={"message": msg_text},
        headers=student_a_headers,
    )
    assert post_resp.status_code == 200
    session_id = post_resp.json()["session_id"]

    # Fetch history
    hist_resp = client.get(f"/api/v1/chat/history?session_id={session_id}", headers=student_a_headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) >= 2  # user message and bot reply
    assert any(h["text"] == msg_text and h["sender"] == "user" for h in history)
    assert any(h["sender"] == "bot" for h in history)


def test_chatbot_service_with_mocked_genai_client():
    """Verify that when GenAI client is active, client.models.generate_content is called and parsed."""
    from unittest.mock import MagicMock, patch
    from backend.app.services.ai.chatbot_service import chatbot_service

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "According to Section 1.2 of the Attendance Policy, medical leave allows up to 10% condonation."
    mock_client.models.generate_content.return_value = mock_response

    with patch.object(chatbot_service, "_get_genai_client", return_value=mock_client):
        reply, sources = chatbot_service._handle_policy_rag("What is the medical leave policy for attendance?")
        assert "condonation" in reply
        assert len(sources) > 0
        assert mock_client.models.generate_content.called
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert "Student Question: What is the medical leave policy for attendance?" in call_kwargs["contents"]



def test_genai_client_lazy_initialization():
    """Verify that genai.Client initializes properly when GEMINI_API_KEY is configured."""
    from unittest.mock import MagicMock, patch
    from backend.app.services.ai.chatbot_service import ChatbotService
    from backend.app.repositories.database import get_repository

    test_service = ChatbotService(repo=get_repository())
    with patch("backend.app.core.config.settings.GEMINI_API_KEY", "test-mock-api-key-for-unit-test"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client_cls.return_value = MagicMock()
            client = test_service._get_genai_client()
            assert client is not None
            mock_client_cls.assert_called_once_with(api_key="test-mock-api-key-for-unit-test")

