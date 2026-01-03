"""
Notification Models
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel


class NotificationType(str, Enum):
    """Notification type enumeration."""
    EXPIRY_ALERT = "expiry_alert"
    RECIPE_SUGGESTION = "recipe_suggestion"
    ACHIEVEMENT = "achievement"
    FAMILY_UPDATE = "family_update"
    REMINDER = "reminder"


class NotificationResponse(BaseModel):
    """Response model for notification."""
    id: str
    user_id: str
    type: str
    title: str
    body: str
    data: Optional[dict] = None
    read: bool = False
    voice_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationDismiss(BaseModel):
    """Request model for dismissing notification."""
    notification_ids: List[str]


class NotificationSnooze(BaseModel):
    """Request model for snoozing notification."""
    notification_id: str
    snooze_hours: int = 3


class NotificationListResponse(BaseModel):
    """Response model for list of notifications."""
    success: bool = True
    data: List[NotificationResponse]
    unread_count: int
