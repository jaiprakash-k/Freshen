"""
Analytics and Achievement Models
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    """Quick summary stats for user."""
    items_saved: int
    money_saved: float
    co2_prevented_kg: float
    water_saved_liters: float
    current_streak: int
    best_streak: int
    waste_count: int
    waste_cost: float


class DailyStats(BaseModel):
    """Daily statistics data point."""
    date: date
    items_saved: int
    items_wasted: int
    money_saved: float
    money_wasted: float


class AnalyticsTimePeriod(BaseModel):
    """Analytics data for a time period."""
    success: bool = True
    period: str  # week, month, year, all
    start_date: date
    end_date: date
    summary: AnalyticsSummary
    daily_data: List[DailyStats]
    
    # Category breakdown
    waste_by_category: dict  # { "dairy": 5, "vegetables": 3, ... }
    savings_by_category: dict


class AnalyticsInsight(BaseModel):
    """AI-generated insight."""
    id: str
    type: str  # tip, warning, achievement, trend
    title: str
    description: str
    action_text: Optional[str] = None
    action_url: Optional[str] = None
    created_at: datetime


class AnalyticsInsightsResponse(BaseModel):
    """Response model for analytics insights."""
    success: bool = True
    insights: List[AnalyticsInsight]


class AchievementResponse(BaseModel):
    """Response model for achievement."""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0  # 0-1 progress towards unlock
    target: Optional[int] = None
    current: Optional[int] = None


class AchievementsListResponse(BaseModel):
    """Response model for list of achievements."""
    success: bool = True
    unlocked_count: int
    total_count: int
    achievements: List[AchievementResponse]


class ExportRequest(BaseModel):
    """Request model for data export."""
    format: str = "csv"  # csv, json
    include_items: bool = True
    include_analytics: bool = True
    include_waste_logs: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None
