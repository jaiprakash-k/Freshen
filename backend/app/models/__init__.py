"""
FreshKeep Models Package
Pydantic models for request/response validation.
"""

from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    TokenRefresh,
)
from app.models.item import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemConsumeRequest,
    ItemWasteRequest,
    ItemListResponse,
)
from app.models.family import (
    FamilyCreate,
    FamilyJoin,
    FamilyResponse,
    FamilyMemberResponse,
    FamilyPermissionUpdate,
)
from app.models.recipe import (
    RecipeResponse,
    RecipeDetailResponse,
    RecipeSearchParams,
)
from app.models.notification import (
    NotificationResponse,
    NotificationDismiss,
)
from app.models.analytics import (
    AnalyticsSummary,
    AnalyticsTimePeriod,
    AnalyticsInsight,
    AchievementResponse,
)
from app.models.shopping import (
    ShoppingItemCreate,
    ShoppingItemUpdate,
    ShoppingItemResponse,
    ShoppingListResponse,
)
from app.models.settings import (
    UserSettingsResponse,
    UserSettingsUpdate,
    NotificationSettings,
    FoodPreferences,
    ExpirationSettings,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin", 
    "UserResponse",
    "UserUpdate",
    "TokenResponse",
    "TokenRefresh",
    # Item
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "ItemConsumeRequest",
    "ItemWasteRequest",
    "ItemListResponse",
    # Family
    "FamilyCreate",
    "FamilyJoin",
    "FamilyResponse",
    "FamilyMemberResponse",
    "FamilyPermissionUpdate",
    # Recipe
    "RecipeResponse",
    "RecipeDetailResponse",
    "RecipeSearchParams",
    # Notification
    "NotificationResponse",
    "NotificationDismiss",
    # Analytics
    "AnalyticsSummary",
    "AnalyticsTimePeriod",
    "AnalyticsInsight",
    "AchievementResponse",
    # Shopping
    "ShoppingItemCreate",
    "ShoppingItemUpdate",
    "ShoppingItemResponse",
    "ShoppingListResponse",
    # Settings
    "UserSettingsResponse",
    "UserSettingsUpdate",
    "NotificationSettings",
    "FoodPreferences",
    "ExpirationSettings",
]
