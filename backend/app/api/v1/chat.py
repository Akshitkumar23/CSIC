"""AI Chatbot API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, status

from backend.app.core.security import get_current_user
from backend.app.models.auth import UserProfile
from backend.app.models.chat import (
    ChatHistoryItem,
    ChatMessageRequest,
    ChatMessageResponse,
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
