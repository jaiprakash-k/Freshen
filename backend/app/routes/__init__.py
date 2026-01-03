"""
FreshKeep Routes Package
API endpoint routers.
"""

from app.routes.auth import router as auth_router
from app.routes.inventory import router as inventory_router
from app.routes.recipe import router as recipe_router
from app.routes.notification import router as notification_router
from app.routes.analytics import router as analytics_router
from app.routes.shopping import router as shopping_router
from app.routes.family import router as family_router
from app.routes.settings import router as settings_router

__all__ = [
    "auth_router",
    "inventory_router",
    "recipe_router",
    "notification_router",
    "analytics_router",
    "shopping_router",
    "family_router",
    "settings_router",
]
