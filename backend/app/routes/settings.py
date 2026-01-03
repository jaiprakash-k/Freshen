"""
Settings Routes
User preferences management.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.settings import UserSettingsUpdate
from app.services.settings_service import SettingsService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
settings_service = SettingsService()


@router.get("")
async def get_settings(current_user: dict = Depends(get_current_user)):
    """Get all user settings."""
    result = await settings_service.get_settings(current_user["id"])
    return result


@router.put("")
async def update_settings(updates: UserSettingsUpdate, current_user: dict = Depends(get_current_user)):
    """Update user settings."""
    result = await settings_service.update_settings(
        user_id=current_user["id"],
        notifications=updates.notifications.model_dump() if updates.notifications else None,
        food=updates.food.model_dump() if updates.food else None,
        expiration=updates.expiration.model_dump() if updates.expiration else None,
        timezone=updates.timezone,
    )
    return result


@router.post("/export")
async def export_data(current_user: dict = Depends(get_current_user)):
    """Export all user data (GDPR)."""
    data = await settings_service.export_user_data(current_user["id"])
    return JSONResponse(content=data, media_type="application/json",
                        headers={"Content-Disposition": "attachment; filename=freshkeep_data.json"})
