"""
User and Authentication Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    name: str = Field(..., min_length=2, max_length=100)
    timezone: str = Field(default="UTC")


class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Request model for updating user profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    timezone: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    name: str
    timezone: str
    family_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    success: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Request model for password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Request model for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8)
