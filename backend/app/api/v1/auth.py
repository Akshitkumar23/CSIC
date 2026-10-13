"""Authentication endpoints."""
from fastapi import APIRouter, Depends

from backend.app.core.security import get_current_user
from backend.app.models.auth import LoginRequest, Token, UserProfile
from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="Authenticate user with credentials")
async def login(credentials: LoginRequest) -> Token:
    """Validate user credentials and return an OAuth2 compliant JWT Bearer token."""
    return auth_service.login(credentials)


@router.get("/me", response_model=UserProfile, summary="Get authenticated profile")
async def get_my_profile(
    current_user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """Return user profile attributes for the currently active session."""
    return current_user
