"""Authentication and session management service."""
from datetime import timedelta
from typing import Any, Optional

from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.core.security import create_access_token
from backend.app.models.auth import LoginRequest, Token, UserProfile
from backend.app.repositories.database import get_repository


class AuthService:
    """Handles credentials authentication and token issuance."""

    def __init__(self, repo: Optional[Any] = None) -> None:
        self.repo = repo or get_repository()

    def login(self, creds: LoginRequest) -> Token:
        """Authenticate user and issue signed JWT bearer token."""
        user = self.repo.authenticate_user(creds.email, creds.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        token_payload = {
            "sub": user.id,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
        }
        access_token = create_access_token(
            data=token_payload,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )


auth_service = AuthService()
