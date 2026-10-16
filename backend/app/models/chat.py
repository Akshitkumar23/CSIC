"""Pydantic models for CSIC AI Chatbot service."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Student chat input message payload."""
    message: str = Field(..., min_length=1, max_length=1000, description="Inquiry text from student")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID")


class ChatMessageResponse(BaseModel):
    """Chatbot output response with query type and source citations."""
    id: str = Field(..., description="Unique message ID")
    reply: str = Field(..., description="Assistant response text")
    query_type: str = Field(..., description="Classified intent (attendance, marks, fees, timetable, notices, policy_document, general)")
    sources: List[str] = Field(default_factory=list, description="Grounding data sources or policy citations")
    verified_data: Optional[Dict[str, Any]] = Field(None, description="Deterministic structured database facts if applicable")
    session_id: str = Field(..., description="Chat session identifier")
    timestamp: str = Field(..., description="Formatted timestamp")


class ChatHistoryItem(BaseModel):
    """Historical message item in conversation."""
    id: str
    session_id: str
    sender: str = Field(..., description="'user' or 'bot'")
    text: str
    query_type: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    verified_data: Optional[Dict[str, Any]] = None
    timestamp: str


class ChatSuggestionsResponse(BaseModel):
    """Suggested quick prompts for student drawer."""
    suggestions: List[str]


class ChatSessionItem(BaseModel):
    """Chat session metadata item for sidebar list."""
    id: str
    title: str
    created_at: str
    updated_at: str
    last_message_preview: Optional[str] = None


class ChatSessionCreateRequest(BaseModel):
    """Payload to create a new session."""
    title: Optional[str] = Field(None, max_length=200, description="Optional title for the conversation")


class ChatSessionListResponse(BaseModel):
    """List of chat sessions for a student."""
    sessions: List[ChatSessionItem]
