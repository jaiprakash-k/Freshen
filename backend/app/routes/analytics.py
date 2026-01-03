"""
Analytics Routes
Statistics, insights, and achievements.
"""

from fastapi import APIRouter, Depends, Query
from app.services.analytics_service import AnalyticsService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/summary")
async def get_summary(current_user: dict = Depends(get_current_user)):
    """Get quick summary stats."""
    summary = await analytics_service.get_summary(current_user["id"])
    return success_response(data=summary)


@router.get("/time-period")
async def get_time_period(
    period: str = Query("week", pattern="^(week|month|year|all)$"),
    current_user: dict = Depends(get_current_user),
):
    """Get analytics for a time period."""
    result = await analytics_service.get_time_period(current_user["id"], period)
    return success_response(data=result)


@router.get("/insights")
async def get_insights(current_user: dict = Depends(get_current_user)):
    """Get AI-generated insights and tips."""
    insights = await analytics_service.get_insights(current_user["id"])
    return success_response(data=insights)


@router.get("/achievements")
async def get_achievements(current_user: dict = Depends(get_current_user)):
    """Get user achievements with progress."""
    achievements = await analytics_service.get_achievements(current_user["id"])
    return success_response(data=achievements)


@router.post("/check-achievements")
async def check_achievements(current_user: dict = Depends(get_current_user)):
    """Check for newly unlocked achievements."""
    newly_unlocked = await analytics_service.check_and_unlock_achievements(current_user["id"])
    return success_response(data=newly_unlocked, message=f"{len(newly_unlocked)} new achievements!")
