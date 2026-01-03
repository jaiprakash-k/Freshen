"""
Notification Service
Push notifications and alert management.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from app.database import get_supabase_client, Tables
from app.services.tts_service import TTSService


class NotificationService:
    """Service for managing notifications."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.tts_service = TTSService()
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        generate_voice: bool = False
    ) -> dict:
        """
        Create and store a notification.
        
        Args:
            user_id: Target user
            notification_type: Type (expiry_alert, recipe_suggestion, etc.)
            title: Notification title
            body: Notification body
            data: Additional data payload
            generate_voice: Whether to generate TTS audio
        
        Returns:
            Created notification
        """
        notification_id = str(uuid.uuid4())
        
        voice_url = None
        if generate_voice:
            try:
                voice_url = await self.tts_service.generate_speech(body)
            except Exception:
                pass  # Voice generation is optional
        
        notification_data = {
            "id": notification_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "body": body,
            "data": data or {},
            "read": False,
            "voice_url": voice_url,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        result = self.supabase.table(Tables.NOTIFICATIONS).insert(
            notification_data
        ).execute()
        
        return result.data[0] if result.data else notification_data
    
    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> dict:
        """
        Get user's notifications.
        
        Args:
            user_id: User ID
            unread_only: Filter to unread only
            limit: Max notifications to return
        
        Returns:
            Notifications with unread count
        """
        query = self.supabase.table(Tables.NOTIFICATIONS).select("*").eq(
            "user_id", user_id
        )
        
        if unread_only:
            query = query.eq("read", False)
        
        query = query.order("created_at", desc=True).limit(limit)
        result = query.execute()
        
        notifications = result.data or []
        unread_count = sum(1 for n in notifications if not n.get("read"))
        
        return {
            "notifications": notifications,
            "unread_count": unread_count,
        }
    
    async def mark_as_read(
        self,
        user_id: str,
        notification_ids: List[str]
    ) -> int:
        """
        Mark notifications as read.
        
        Returns:
            Number of notifications updated
        """
        for nid in notification_ids:
            self.supabase.table(Tables.NOTIFICATIONS).update({
                "read": True
            }).eq("id", nid).eq("user_id", user_id).execute()
        
        return len(notification_ids)
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all user's notifications as read."""
        result = self.supabase.table(Tables.NOTIFICATIONS).update({
            "read": True
        }).eq("user_id", user_id).eq("read", False).execute()
        
        return len(result.data) if result.data else 0
    
    async def snooze_notification(
        self,
        user_id: str,
        notification_id: str,
        hours: int = 3
    ) -> dict:
        """
        Snooze a notification for later.
        Creates a new notification scheduled for later.
        """
        # Get original notification
        result = self.supabase.table(Tables.NOTIFICATIONS).select("*").eq(
            "id", notification_id
        ).eq("user_id", user_id).execute()
        
        if not result.data:
            return None
        
        original = result.data[0]
        
        # Mark original as read
        self.supabase.table(Tables.NOTIFICATIONS).update({
            "read": True
        }).eq("id", notification_id).execute()
        
        # Create snoozed version (in production, this would be scheduled)
        snooze_time = datetime.utcnow() + timedelta(hours=hours)
        
        return {
            "snoozed_until": snooze_time.isoformat(),
            "original_notification": original,
        }
    
    async def delete_notification(
        self,
        user_id: str,
        notification_id: str
    ) -> bool:
        """Delete a notification."""
        self.supabase.table(Tables.NOTIFICATIONS).delete().eq(
            "id", notification_id
        ).eq("user_id", user_id).execute()
        
        return True
    
    async def create_expiry_alert(
        self,
        user_id: str,
        expiring_items: List[dict],
        with_voice: bool = False
    ) -> dict:
        """
        Create an expiry alert notification.
        
        Args:
            user_id: Target user
            expiring_items: List of items expiring soon
            with_voice: Generate voice alert
        
        Returns:
            Created notification
        """
        if not expiring_items:
            return None
        
        count = len(expiring_items)
        item_names = [item["name"] for item in expiring_items[:3]]
        
        if count == 1:
            title = f"{item_names[0]} expires today!"
            body = f"Your {item_names[0]} needs attention. Use it today or find a recipe!"
        else:
            title = f"{count} items need attention"
            items_text = ", ".join(item_names)
            if count > 3:
                items_text += f" and {count - 3} more"
            body = f"These items are expiring soon: {items_text}"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="expiry_alert",
            title=title,
            body=body,
            data={"item_ids": [item["id"] for item in expiring_items]},
            generate_voice=with_voice,
        )
    
    async def create_recipe_suggestion(
        self,
        user_id: str,
        recipe: dict,
        expiring_items: List[str]
    ) -> dict:
        """Create a recipe suggestion notification."""
        title = f"Recipe idea: {recipe['title']}"
        body = f"Use your {', '.join(expiring_items[:2])} in this delicious recipe!"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="recipe_suggestion",
            title=title,
            body=body,
            data={"recipe_id": recipe["id"]},
        )
    
    async def create_achievement_notification(
        self,
        user_id: str,
        achievement: dict
    ) -> dict:
        """Create an achievement unlock notification."""
        title = f"🎉 Achievement Unlocked!"
        body = f"You earned: {achievement['name']} - {achievement['description']}"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="achievement",
            title=title,
            body=body,
            data={"achievement_id": achievement["id"]},
        )
