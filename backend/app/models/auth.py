from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT Access Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # seconds


class TokenData(BaseModel):
    """Payload decoded from JWT Token."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Standard credential login request payload."""
    email: str = Field(..., description="Student or faculty institutional email")
    password: str = Field(..., min_length=4, description="Cleartext password")


class UserProfile(BaseModel):
    """User profile data model matching Supabase profiles table."""
    id: str
    email: str
    role: str  # student, faculty, admin
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
