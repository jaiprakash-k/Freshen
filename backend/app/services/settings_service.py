"""
Settings Service
User preferences management.
"""

from typing import Optional
from app.database import get_supabase_client, Tables
from app.middleware.error_handler import NotFoundError


class SettingsService:
    """Service for user settings management."""
    
    DEFAULT_SETTINGS = {
        "notifications": {
            "enabled": True, "morning_alert_time": "07:00", "evening_reminder": True,
            "evening_reminder_time": "19:00", "voice_alerts": False, "expiry_threshold_days": 3,
        },
        "food": {
            "dietary_restrictions": [], "allergies": [], "disliked_ingredients": [],
            "preferred_cuisines": [], "default_unit_system": "metric",
        },
        "expiration": {"mode": "standard", "custom_shelf_life": {}, "auto_extend_freezer": True},
    }
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_settings(self, user_id: str) -> dict:
        """Get user settings."""
        result = self.supabase.table(Tables.USER_SETTINGS).select("*").eq("user_id", user_id).execute()
        
        if result.data:
            settings = result.data[0]
        else:
            # Create default settings
            settings = {"user_id": user_id, **self.DEFAULT_SETTINGS}
            self.supabase.table(Tables.USER_SETTINGS).insert(settings).execute()
        
        # Get user info
        user = self.supabase.table(Tables.USERS).select("timezone").eq("id", user_id).execute()
        
        return {
            "success": True,
            "notifications": settings.get("notifications", self.DEFAULT_SETTINGS["notifications"]),
            "food": settings.get("food", self.DEFAULT_SETTINGS["food"]),
            "expiration": settings.get("expiration", self.DEFAULT_SETTINGS["expiration"]),
            "timezone": user.data[0]["timezone"] if user.data else "UTC",
            "language": "en",
            "subscription_plan": "free",
        }
    
    async def update_settings(self, user_id: str, notifications: Optional[dict] = None,
                               food: Optional[dict] = None, expiration: Optional[dict] = None,
                               timezone: Optional[str] = None) -> dict:
        """Update user settings."""
        updates = {}
        if notifications:
            updates["notifications"] = notifications
        if food:
            updates["food"] = food
        if expiration:
            updates["expiration"] = expiration
        
        if updates:
            self.supabase.table(Tables.USER_SETTINGS).update(updates).eq("user_id", user_id).execute()
        
        if timezone:
            self.supabase.table(Tables.USERS).update({"timezone": timezone}).eq("id", user_id).execute()
        
        return await self.get_settings(user_id)
    
    async def export_user_data(self, user_id: str) -> dict:
        """Export all user data (GDPR compliance)."""
        user = self.supabase.table(Tables.USERS).select("*").eq("id", user_id).execute()
        settings = self.supabase.table(Tables.USER_SETTINGS).select("*").eq("user_id", user_id).execute()
        items = self.supabase.table(Tables.ITEMS).select("*").eq("user_id", user_id).execute()
        
        return {
            "user": user.data[0] if user.data else {},
            "settings": settings.data[0] if settings.data else {},
            "items": items.data or [],
            "exported_at": "now",
        }
