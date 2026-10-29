"""Authentication endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.security import get_current_user
from backend.app.models.auth import LoginRequest, Token, UserProfile
from backend.app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="Authenticate user with credentials")
async def login(credentials: LoginRequest) -> Token:
    """Validate user credentials and return an OAuth2 compliant JWT Bearer token."""
    try:
        return auth_service.login(credentials)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Authentication error for %s: %s", credentials.email, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service error: {str(exc)}",
        )


@router.get("/me", response_model=UserProfile, summary="Get authenticated profile")
async def get_my_profile(
    current_user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """Return user profile attributes for the currently active session."""
    return current_user
