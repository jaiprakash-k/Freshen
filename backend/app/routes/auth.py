"""
Authentication Routes
User registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, TokenRefresh, UserUpdate, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
auth_service = AuthService()


@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    """Register a new user account."""
    result = await auth_service.register(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        timezone=user_data.timezone,
    )
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user=UserResponse(**result["user"]),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password."""
    result = await auth_service.login(email=credentials.email, password=credentials.password)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user=UserResponse(**result["user"]),
    )


@router.post("/refresh")
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token."""
    result = await auth_service.refresh_token(token_data.refresh_token)
    return success_response(data=result, message="Token refreshed")


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    profile = await auth_service.get_profile(current_user["id"])
    return UserResponse(**profile)


@router.put("/me", response_model=UserResponse)
async def update_profile(updates: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user profile."""
    profile = await auth_service.update_profile(
        user_id=current_user["id"],
        name=updates.name,
        timezone=updates.timezone,
    )
    return UserResponse(**profile)


@router.post("/forgot-password")
async def forgot_password(email: str):
    """Request password reset."""
    await auth_service.request_password_reset(email)
    return success_response(message="If the email exists, a reset link has been sent")
