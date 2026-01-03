"""
Analytics Worker
Weekly job for data aggregation and insights.
"""

from datetime import datetime, date, timedelta
from app.database import get_supabase_client, Tables
from app.services.analytics_service import AnalyticsService


async def aggregate_weekly_analytics():
    """
    Aggregate weekly analytics data for all users.
    Runs every Sunday at 11:00 PM.
    """
    print(f"📊 Starting weekly analytics at {datetime.now()}")
    
    supabase = get_supabase_client()
    analytics_service = AnalyticsService()
    
    try:
        # Get all users
        users_result = supabase.table(Tables.USERS).select("id").execute()
        users = users_result.data or []
        
        processed = 0
        for user in users:
            user_id = user["id"]
            
            # Calculate stats for past week
            today = date.today()
            week_ago = today - timedelta(days=7)
            
            # Count consumed items
            consumed = supabase.table(Tables.CONSUMPTION_LOGS).select(
                "id", count="exact"
            ).eq("user_id", user_id).gte(
                "consumed_at", week_ago.isoformat()
            ).execute()
            
            # Count wasted items
            wasted = supabase.table(Tables.WASTE_LOGS).select(
                "id, estimated_value, co2_impact_kg", count="exact"
            ).eq("user_id", user_id).gte(
                "wasted_at", week_ago.isoformat()
            ).execute()
            
            items_saved = consumed.count or 0
            waste_data = wasted.data or []
            waste_count = len(waste_data)
            waste_cost = sum(w.get("estimated_value", 0) for w in waste_data)
            
            # Record daily stats
            await analytics_service.record_daily_stats(
                user_id=user_id,
                items_saved=items_saved,
                money_saved=items_saved * 3.0,  # Estimate $3 per item
                co2_prevented=items_saved * 2.5,
                water_saved=items_saved * 1000,
                waste_count=waste_count,
                waste_cost=waste_cost,
            )
            
            # Check for new achievements
            await analytics_service.check_and_unlock_achievements(user_id)
            
            processed += 1
        
        print(f"✅ Weekly analytics complete: {processed} users processed")
        
    except Exception as e:
        print(f"❌ Weekly analytics failed: {e}")
