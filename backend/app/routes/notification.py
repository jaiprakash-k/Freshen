"""
Notification Routes
Push notifications and alerts.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from app.services.notification_service import NotificationService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
notification_service = NotificationService()


@router.get("")
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Get user notifications."""
    result = await notification_service.get_notifications(
        user_id=current_user["id"],
        unread_only=unread_only,
        limit=limit,
    )
    return success_response(
        data=result["notifications"],
        unread_count=result["unread_count"],
    )


@router.post("/dismiss")
async def dismiss_notifications(
    notification_ids: List[str],
    current_user: dict = Depends(get_current_user),
):
    """Mark notifications as read."""
    count = await notification_service.mark_as_read(
        user_id=current_user["id"],
        notification_ids=notification_ids,
    )
    return success_response(message=f"Marked {count} notifications as read")


@router.post("/dismiss-all")
async def dismiss_all(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read."""
    count = await notification_service.mark_all_as_read(current_user["id"])
    return success_response(message=f"Marked {count} notifications as read")


@router.post("/{notification_id}/snooze")
async def snooze_notification(
    notification_id: str,
    hours: int = Query(3, ge=1, le=24),
    current_user: dict = Depends(get_current_user),
):
    """Snooze a notification for later."""
    result = await notification_service.snooze_notification(
        user_id=current_user["id"],
        notification_id=notification_id,
        hours=hours,
    )
    return success_response(data=result, message=f"Snoozed for {hours} hours")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a notification."""
    await notification_service.delete_notification(current_user["id"], notification_id)
    return success_response(message="Notification deleted")
