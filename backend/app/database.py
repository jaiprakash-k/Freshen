"""
FreshKeep Database Configuration
Supabase client setup and connection management.
"""

from functools import lru_cache
from supabase import create_client, Client

from app.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.
    Uses service role key for full database access.
    Returns None if credentials not configured.
    """
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_service_role_key:
        # Return None for development without Supabase
        return None
    
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )


def get_supabase_anon_client() -> Client:
    """
    Get Supabase client with anon key (for RLS-protected operations).
    """
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env"
        )
    
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )


# Database table names
class Tables:
    USERS = "users"
    FAMILIES = "families"
    FAMILY_MEMBERS = "family_members"
    ITEMS = "items"
    CONSUMPTION_LOGS = "consumption_logs"
    WASTE_LOGS = "waste_logs"
    NOTIFICATIONS = "notifications"
    SHOPPING_LISTS = "shopping_lists"
    SHOPPING_ITEMS = "shopping_items"
    ANALYTICS_DAILY = "analytics_daily"
    ANALYTICS_INSIGHTS = "analytics_insights"
    ACHIEVEMENTS = "achievements"
    USER_ACHIEVEMENTS = "user_achievements"
    USER_SETTINGS = "user_settings"
