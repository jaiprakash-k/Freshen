"""
Family Sharing Models
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class FamilyRole(str, Enum):
    """Family member role enumeration."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class FamilyCreate(BaseModel):
    """Request model for creating a family."""
    name: str = Field(..., min_length=2, max_length=100)


class FamilyJoin(BaseModel):
    """Request model for joining a family."""
    invite_code: str = Field(..., min_length=6, max_length=10)


class FamilyMemberResponse(BaseModel):
    """Response model for a family member."""
    id: str
    user_id: str
    name: str
    email: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class FamilyResponse(BaseModel):
    """Response model for family data."""
    id: str
    name: str
    invite_code: str
    admin_id: str
    member_count: int
    created_at: datetime
    members: Optional[List[FamilyMemberResponse]] = None

    class Config:
        from_attributes = True


class FamilyPermissionUpdate(BaseModel):
    """Request model for updating member permissions."""
    user_id: str
    role: FamilyRole


class FamilyInviteResponse(BaseModel):
    """Response model for family invite."""
    success: bool = True
    family_id: str
    invite_code: str
    expires_at: Optional[datetime] = None
