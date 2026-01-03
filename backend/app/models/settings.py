"""
User Settings Models
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class NotificationSettings(BaseModel):
    """Notification preferences."""
    enabled: bool = True
    morning_alert_time: str = "07:00"  # HH:MM format
    evening_reminder: bool = True
    evening_reminder_time: str = "19:00"
    voice_alerts: bool = False
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None  # "08:00"
    expiry_threshold_days: int = 3  # Alert when items expire within N days


class FoodPreferences(BaseModel):
    """Dietary and food preferences."""
    dietary_restrictions: List[str] = []  # vegetarian, vegan, gluten-free, etc.
    allergies: List[str] = []
    disliked_ingredients: List[str] = []
    preferred_cuisines: List[str] = []
    default_unit_system: str = "metric"  # metric or imperial


class ExpirationSettings(BaseModel):
    """Expiration tracking preferences."""
    mode: str = "standard"  # conservative, standard, optimistic
    custom_shelf_life: dict = {}  # { "dairy": 5, "meat": 2, ... }
    auto_extend_freezer: bool = True  # Extend expiry when moved to freezer


class UserSettingsResponse(BaseModel):
    """Response model for user settings."""
    success: bool = True
    notifications: NotificationSettings
    food: FoodPreferences
    expiration: ExpirationSettings
    
    # Account
    timezone: str = "UTC"
    language: str = "en"
    
    # Subscription
    subscription_plan: str = "free"  # free, premium, family
    subscription_expires: Optional[str] = None


class UserSettingsUpdate(BaseModel):
    """Request model for updating settings."""
    notifications: Optional[NotificationSettings] = None
    food: Optional[FoodPreferences] = None
    expiration: Optional[ExpirationSettings] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
