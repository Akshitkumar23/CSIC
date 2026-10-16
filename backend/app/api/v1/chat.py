"""AI Chatbot API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, status

from backend.app.core.security import get_current_user
from backend.app.models.auth import UserProfile
from backend.app.models.chat import (
    ChatHistoryItem,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionItem,
    ChatSuggestionsResponse,
)
from backend.app.services.ai.chatbot_service import chatbot_service

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Process conversational message",
)
async def send_chat_message(
    payload: ChatMessageRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> ChatMessageResponse:
    """Send a question to the CSIC AI Assistant.

    Classifies intent, executes zero-SQL verified database queries for personal records,
    or grounds institutional policy queries in document chunks using Gemini/RAG.
    """
    return chatbot_service.process_message(
        message=payload.message,
        user_id=current_user.id,
        user_role=current_user.role,
        session_id=payload.session_id,
    )


@router.get(
    "/sessions",
    response_model=List[ChatSessionItem],
    summary="List student conversation sessions",
)
async def list_chat_sessions(
    current_user: UserProfile = Depends(get_current_user),
) -> List[ChatSessionItem]:
    """Retrieve all chat sessions for the authenticated student."""
    return chatbot_service.list_sessions(user_id=current_user.id)


@router.post(
    "/sessions",
    response_model=ChatSessionItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation session",
)
async def create_chat_session(
    payload: Optional[ChatSessionCreateRequest] = None,
    current_user: UserProfile = Depends(get_current_user),
) -> ChatSessionItem:
    """Create a new conversational session thread."""
    title = payload.title if payload else None
    return chatbot_service.create_session(user_id=current_user.id, title=title)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation session",
)
async def delete_chat_session(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> None:
    """Delete a conversation session and all its messages."""
    chatbot_service.delete_session(user_id=current_user.id, session_id=session_id)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=List[ChatHistoryItem],
    summary="Get messages for a specific session",
)
async def get_session_messages(
    session_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> List[ChatHistoryItem]:
    """Retrieve message history for a specific conversation session."""
    return chatbot_service.get_history(user_id=current_user.id, session_id=session_id)


@router.get(
    "/history",
    response_model=List[ChatHistoryItem],
    summary="Get user chat message history",
)
async def get_chat_history(
    session_id: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_user),
) -> List[ChatHistoryItem]:
    """Retrieve message history for authenticated user and optional session ID."""
    return chatbot_service.get_history(
        user_id=current_user.id,
        session_id=session_id,
    )


@router.get(
    "/suggestions",
    response_model=ChatSuggestionsResponse,
    summary="Get suggested chat prompts",
)
async def get_chat_suggestions() -> ChatSuggestionsResponse:
    """Retrieve curated prompt suggestions for academic queries and institutional policies."""
    return chatbot_service.get_suggestions()
