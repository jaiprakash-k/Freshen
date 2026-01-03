"""
FreshKeep Backend Configuration
Loads environment variables and provides app-wide settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # JWT Authentication
    jwt_secret: str = "freshkeep_super_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OCR.space
    ocr_space_api_key: str = ""

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    # Spoonacular
    spoonacular_api_key: str = ""

    # Firebase (optional)
    firebase_credentials_path: Optional[str] = None

    # Redis (optional)
    redis_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Category-based default shelf life (in days)
SHELF_LIFE_DEFAULTS = {
    "dairy": 7,
    "meat": 3,
    "poultry": 2,
    "fish": 2,
    "vegetables": 5,
    "fruits": 5,
    "bread": 5,
    "eggs": 21,
    "frozen": 90,
    "canned": 365,
    "condiments": 180,
    "beverages": 30,
    "snacks": 60,
    "grains": 180,
    "other": 14,
}

# Storage types
STORAGE_TYPES = ["fridge", "freezer", "pantry"]

# Item status
ITEM_STATUS = ["active", "consumed", "wasted", "expired"]

# Freshness thresholds (days until expiry)
FRESHNESS_THRESHOLDS = {
    "fresh": 4,      # > 3 days
    "warning": 1,    # 1-3 days
    "expires_today": 0,  # 0 days
    "expired": -1,   # < 0 days
}

# Waste reasons
WASTE_REASONS = [
    "forgot",
    "spoiled",
    "tasted_bad",
    "too_much",
    "changed_plans",
    "other",
]
