"""
Notification Worker
Daily jobs for expiry alerts and reminders.
"""

from datetime import datetime
from app.database import get_supabase_client, Tables
from app.services.inventory_service import InventoryService
from app.services.notification_service import NotificationService


async def send_morning_alerts():
    """
    Send morning expiry alerts to all users.
    Runs daily at 7:00 AM.
    """
    print(f"🔔 Sending morning alerts at {datetime.now()}")
    
    supabase = get_supabase_client()
    notification_service = NotificationService()
    inventory_service = InventoryService()
    
    try:
        # Get all users with notifications enabled
        users_result = supabase.table(Tables.USERS).select("id").execute()
        users = users_result.data or []
        
        sent = 0
        for user in users:
            user_id = user["id"]
            
            # Check notification settings
            settings = supabase.table(Tables.USER_SETTINGS).select(
                "notifications"
            ).eq("user_id", user_id).execute()
            
            if settings.data:
                notif_settings = settings.data[0].get("notifications", {})
                if not notif_settings.get("enabled", True):
                    continue
            
            # Get expiring items
            expiring = await inventory_service.get_expiring_items(
                user_id=user_id,
                family_id=None,
                days=3
            )
            
            if expiring:
                # Create notification
                await notification_service.create_expiry_alert(
                    user_id=user_id,
                    expiring_items=expiring,
                    with_voice=notif_settings.get("voice_alerts", False) if settings.data else False
                )
                sent += 1
        
        print(f"✅ Morning alerts sent to {sent} users")
        
    except Exception as e:
        print(f"❌ Morning alerts failed: {e}")


async def send_evening_reminders():
    """
    Send evening reminders for items expiring today.
    Runs daily at 7:00 PM.
    """
    print(f"🔔 Sending evening reminders at {datetime.now()}")
    
    supabase = get_supabase_client()
    notification_service = NotificationService()
    inventory_service = InventoryService()
    
    try:
        users_result = supabase.table(Tables.USERS).select("id").execute()
        users = users_result.data or []
        
        sent = 0
        for user in users:
            user_id = user["id"]
            
            # Get items expiring today only
            expiring = await inventory_service.get_expiring_items(
                user_id=user_id,
                family_id=None,
                days=0
            )
            
            if expiring:
                await notification_service.create_notification(
                    user_id=user_id,
                    notification_type="reminder",
                    title="Last chance!",
                    body=f"{len(expiring)} item(s) expire tonight. Use them now!",
                    data={"item_ids": [item["id"] for item in expiring]}
                )
                sent += 1
        
        print(f"✅ Evening reminders sent to {sent} users")
        
    except Exception as e:
        print(f"❌ Evening reminders failed: {e}")
