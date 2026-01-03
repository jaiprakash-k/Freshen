"""
Analytics Service
Usage statistics, insights, and achievements.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import uuid

from app.database import get_supabase_client, Tables
from app.utils.expiration import estimate_food_value, estimate_environmental_impact


class AnalyticsService:
    """Service for analytics and insights."""
    
    # Achievement definitions
    ACHIEVEMENTS = [
        {"id": "first_save", "name": "First Save", "description": "Saved your first item from waste", "target": 1},
        {"id": "week_streak_7", "name": "Week Warrior", "description": "7-day streak without waste", "target": 7},
        {"id": "month_streak_30", "name": "Monthly Master", "description": "30-day streak without waste", "target": 30},
        {"id": "saved_10", "name": "Food Saver", "description": "Saved 10 items from waste", "target": 10},
        {"id": "saved_50", "name": "Waste Fighter", "description": "Saved 50 items from waste", "target": 50},
        {"id": "saved_100", "name": "Eco Champion", "description": "Saved 100 items from waste", "target": 100},
        {"id": "money_saved_50", "name": "Budget Conscious", "description": "Saved $50 worth of food", "target": 50},
        {"id": "money_saved_100", "name": "Smart Saver", "description": "Saved $100 worth of food", "target": 100},
        {"id": "recipes_tried_5", "name": "Kitchen Explorer", "description": "Tried 5 suggested recipes", "target": 5},
        {"id": "family_member", "name": "Team Player", "description": "Joined a family group", "target": 1},
    ]
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_summary(self, user_id: str) -> dict:
        """
        Get quick summary stats for user.
        
        Returns aggregated lifetime stats.
        """
        # Get from analytics_daily or calculate from logs
        try:
            result = self.supabase.table(Tables.ANALYTICS_DAILY).select("*").eq(
                "user_id", user_id
            ).execute()
            
            daily_data = result.data or []
        except Exception:
            daily_data = []
        
        if daily_data:
            return self._aggregate_summary(daily_data)
        
        # Fallback: calculate from consumption/waste logs
        return await self._calculate_summary_from_logs(user_id)
    
    async def get_time_period(
        self,
        user_id: str,
        period: str = "week"
    ) -> dict:
        """
        Get analytics for a specific time period.
        
        Args:
            user_id: User ID
            period: week, month, year, or all
        
        Returns:
            Summary, daily data, and category breakdowns
        """
        # Calculate date range
        today = date.today()
        
        if period == "week":
            start_date = today - timedelta(days=7)
        elif period == "month":
            start_date = today - timedelta(days=30)
        elif period == "year":
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=3650)  # ~10 years
        
        # Get daily analytics data
        try:
            result = self.supabase.table(Tables.ANALYTICS_DAILY).select("*").eq(
                "user_id", user_id
            ).gte("date", start_date.isoformat()).execute()
            
            daily_data = result.data or []
        except Exception:
            daily_data = []
        
        # Calculate category breakdowns from waste/consumption logs
        waste_by_category = await self._get_waste_by_category(user_id, start_date)
        savings_by_category = await self._get_savings_by_category(user_id, start_date)
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "summary": self._aggregate_summary(daily_data),
            "daily_data": [
                {
                    "date": d["date"],
                    "items_saved": d.get("items_saved", 0),
                    "items_wasted": d.get("waste_count", 0),
                    "money_saved": d.get("money_saved", 0),
                    "money_wasted": d.get("waste_cost", 0),
                }
                for d in daily_data
            ],
            "waste_by_category": waste_by_category,
            "savings_by_category": savings_by_category,
        }
    
    async def get_insights(self, user_id: str) -> List[dict]:
        """
        Get AI-generated insights for user.
        
        Returns personalized tips based on usage patterns.
        """
        insights = []
        
        # Get recent stats
        summary = await self.get_summary(user_id)
        
        # Generate insights based on patterns
        if summary.get("waste_count", 0) > 5:
            insights.append({
                "id": str(uuid.uuid4()),
                "type": "tip",
                "title": "Reduce Food Waste",
                "description": f"You've wasted {summary['waste_count']} items. Try checking expiration dates more frequently!",
                "action_text": "View expiring items",
                "action_url": "/inventory/expiring",
                "created_at": datetime.utcnow().isoformat(),
            })
        
        if summary.get("items_saved", 0) >= 10:
            insights.append({
                "id": str(uuid.uuid4()),
                "type": "achievement",
                "title": "Great Progress!",
                "description": f"You've saved {summary['items_saved']} items from waste. Keep it up!",
                "created_at": datetime.utcnow().isoformat(),
            })
        
        # Default insight if none generated
        if not insights:
            insights.append({
                "id": str(uuid.uuid4()),
                "type": "tip",
                "title": "Track Your Groceries",
                "description": "Add items to your inventory when you shop to get personalized recommendations.",
                "action_text": "Add items",
                "action_url": "/inventory/add",
                "created_at": datetime.utcnow().isoformat(),
            })
        
        return insights
    
    async def get_achievements(self, user_id: str) -> dict:
        """
        Get user's achievements with progress.
        
        Returns:
            List of all achievements with unlock status
        """
        # Get unlocked achievements
        try:
            result = self.supabase.table(Tables.USER_ACHIEVEMENTS).select("*").eq(
                "user_id", user_id
            ).execute()
            unlocked = {a["achievement_id"]: a for a in (result.data or [])}
        except Exception:
            unlocked = {}
        
        # Get current stats for progress calculation
        summary = await self.get_summary(user_id)
        
        achievements = []
        for ach in self.ACHIEVEMENTS:
            is_unlocked = ach["id"] in unlocked
            progress = self._calculate_achievement_progress(ach, summary)
            
            achievements.append({
                "id": ach["id"],
                "name": ach["name"],
                "description": ach["description"],
                "icon": self._get_achievement_icon(ach["id"]),
                "unlocked": is_unlocked,
                "unlocked_at": unlocked.get(ach["id"], {}).get("unlocked_at"),
                "progress": min(progress, 1.0),
                "target": ach["target"],
                "current": int(progress * ach["target"]),
            })
        
        unlocked_count = sum(1 for a in achievements if a["unlocked"])
        
        return {
            "unlocked_count": unlocked_count,
            "total_count": len(achievements),
            "achievements": achievements,
        }
    
    async def record_daily_stats(
        self,
        user_id: str,
        items_saved: int = 0,
        money_saved: float = 0,
        co2_prevented: float = 0,
        water_saved: float = 0,
        waste_count: int = 0,
        waste_cost: float = 0
    ) -> None:
        """Record daily statistics (called by background worker)."""
        today = date.today().isoformat()
        
        data = {
            "user_id": user_id,
            "date": today,
            "items_saved": items_saved,
            "money_saved": money_saved,
            "co2_prevented_kg": co2_prevented,
            "water_saved_liters": water_saved,
            "waste_count": waste_count,
            "waste_cost": waste_cost,
        }
        
        try:
            # Upsert: update if exists, insert if not
            self.supabase.table(Tables.ANALYTICS_DAILY).upsert(
                data,
                on_conflict="user_id,date"
            ).execute()
        except Exception:
            pass
    
    async def check_and_unlock_achievements(
        self,
        user_id: str
    ) -> List[dict]:
        """
        Check if user has earned any new achievements.
        
        Returns:
            List of newly unlocked achievements
        """
        summary = await self.get_summary(user_id)
        
        try:
            result = self.supabase.table(Tables.USER_ACHIEVEMENTS).select(
                "achievement_id"
            ).eq("user_id", user_id).execute()
            already_unlocked = {a["achievement_id"] for a in (result.data or [])}
        except Exception:
            already_unlocked = set()
        
        newly_unlocked = []
        
        for ach in self.ACHIEVEMENTS:
            if ach["id"] in already_unlocked:
                continue
            
            progress = self._calculate_achievement_progress(ach, summary)
            
            if progress >= 1.0:
                # Unlock achievement
                try:
                    self.supabase.table(Tables.USER_ACHIEVEMENTS).insert({
                        "user_id": user_id,
                        "achievement_id": ach["id"],
                        "unlocked_at": datetime.utcnow().isoformat(),
                    }).execute()
                    
                    newly_unlocked.append({
                        "id": ach["id"],
                        "name": ach["name"],
                        "description": ach["description"],
                    })
                except Exception:
                    pass
        
        return newly_unlocked
    
    def _aggregate_summary(self, daily_data: List[dict]) -> dict:
        """Aggregate daily data into summary."""
        if not daily_data:
            return {
                "items_saved": 0,
                "money_saved": 0.0,
                "co2_prevented_kg": 0.0,
                "water_saved_liters": 0.0,
                "current_streak": 0,
                "best_streak": 0,
                "waste_count": 0,
                "waste_cost": 0.0,
            }
        
        return {
            "items_saved": sum(d.get("items_saved", 0) for d in daily_data),
            "money_saved": sum(d.get("money_saved", 0) for d in daily_data),
            "co2_prevented_kg": sum(d.get("co2_prevented_kg", 0) for d in daily_data),
            "water_saved_liters": sum(d.get("water_saved_liters", 0) for d in daily_data),
            "current_streak": self._calculate_streak(daily_data),
            "best_streak": self._calculate_best_streak(daily_data),
            "waste_count": sum(d.get("waste_count", 0) for d in daily_data),
            "waste_cost": sum(d.get("waste_cost", 0) for d in daily_data),
        }
    
    async def _calculate_summary_from_logs(self, user_id: str) -> dict:
        """Calculate summary from raw logs if analytics table is empty."""
        try:
            # Get consumption logs
            consumption = self.supabase.table(Tables.CONSUMPTION_LOGS).select("*").eq(
                "user_id", user_id
            ).execute()
            
            # Get waste logs
            waste = self.supabase.table(Tables.WASTE_LOGS).select("*").eq(
                "user_id", user_id
            ).execute()
            
            items_saved = len(consumption.data or [])
            waste_count = len(waste.data or [])
            waste_cost = sum(w.get("estimated_value", 0) for w in (waste.data or []))
            co2_wasted = sum(w.get("co2_impact_kg", 0) for w in (waste.data or []))
            
            # Estimate savings (assuming average item value of $3)
            money_saved = items_saved * 3.0
            
            return {
                "items_saved": items_saved,
                "money_saved": money_saved,
                "co2_prevented_kg": items_saved * 2.5,  # Average CO2 per item
                "water_saved_liters": items_saved * 1000,  # Average water per item
                "current_streak": 0,
                "best_streak": 0,
                "waste_count": waste_count,
                "waste_cost": waste_cost,
            }
        except Exception:
            return {
                "items_saved": 0,
                "money_saved": 0.0,
                "co2_prevented_kg": 0.0,
                "water_saved_liters": 0.0,
                "current_streak": 0,
                "best_streak": 0,
                "waste_count": 0,
                "waste_cost": 0.0,
            }
    
    async def _get_waste_by_category(
        self,
        user_id: str,
        start_date: date
    ) -> Dict[str, int]:
        """Get waste count by category."""
        # In production, join with items table to get category
        return {"other": 0}
    
    async def _get_savings_by_category(
        self,
        user_id: str,
        start_date: date
    ) -> Dict[str, float]:
        """Get savings by category."""
        return {"other": 0}
    
    def _calculate_streak(self, daily_data: List[dict]) -> int:
        """Calculate current no-waste streak."""
        if not daily_data:
            return 0
        
        # Sort by date descending
        sorted_data = sorted(daily_data, key=lambda x: x["date"], reverse=True)
        
        streak = 0
        for day in sorted_data:
            if day.get("waste_count", 0) == 0:
                streak += 1
            else:
                break
        
        return streak
    
    def _calculate_best_streak(self, daily_data: List[dict]) -> int:
        """Calculate best no-waste streak."""
        if not daily_data:
            return 0
        
        sorted_data = sorted(daily_data, key=lambda x: x["date"])
        
        best = 0
        current = 0
        
        for day in sorted_data:
            if day.get("waste_count", 0) == 0:
                current += 1
                best = max(best, current)
            else:
                current = 0
        
        return best
    
    def _calculate_achievement_progress(
        self,
        achievement: dict,
        summary: dict
    ) -> float:
        """Calculate progress towards an achievement."""
        ach_id = achievement["id"]
        target = achievement["target"]
        
        if ach_id == "first_save":
            return min(summary.get("items_saved", 0) / target, 1.0)
        elif ach_id.startswith("week_streak"):
            return min(summary.get("current_streak", 0) / target, 1.0)
        elif ach_id.startswith("month_streak"):
            return min(summary.get("best_streak", 0) / target, 1.0)
        elif ach_id.startswith("saved_"):
            return min(summary.get("items_saved", 0) / target, 1.0)
        elif ach_id.startswith("money_saved_"):
            return min(summary.get("money_saved", 0) / target, 1.0)
        else:
            return 0.0
    
    def _get_achievement_icon(self, ach_id: str) -> str:
        """Get emoji icon for achievement."""
        icons = {
            "first_save": "🌱",
            "week_streak_7": "🔥",
            "month_streak_30": "🏆",
            "saved_10": "⭐",
            "saved_50": "🌟",
            "saved_100": "💫",
            "money_saved_50": "💰",
            "money_saved_100": "💎",
            "recipes_tried_5": "👨‍🍳",
            "family_member": "👨‍👩‍👧‍👦",
        }
        return icons.get(ach_id, "🏅")
