"""
FreshKeep Backend - Main Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import (
    auth_router,
    inventory_router,
    recipe_router,
    notification_router,
    analytics_router,
    shopping_router,
    family_router,
    settings_router,
)
from app.middleware.error_handler import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 FreshKeep Backend starting...")
    settings = get_settings()
    print(f"📍 Environment: {settings.app_env}")
    print(f"🌐 Server: http://{settings.app_host}:{settings.app_port}")
    
    yield
    
    # Shutdown
    print("👋 FreshKeep Backend shutting down...")


# Create FastAPI application
app = FastAPI(
    title="FreshKeep API",
    description="""
    **FreshKeep** - Smart Grocery Management System
    
    Reduce food waste with intelligent expiration tracking, recipe suggestions,
    and family sharing features.
    
    ## Features
    
    * 🛒 **Inventory Management** - Track groceries with smart expiration dates
    * 📸 **Receipt OCR** - Scan receipts to auto-add items
    * 🔍 **Barcode Lookup** - Quick product identification
    * 🍳 **Recipe Suggestions** - Use expiring ingredients wisely
    * 👨‍👩‍👧‍👦 **Family Sharing** - Sync inventory across family members
    * 📊 **Analytics** - Track savings and reduce waste
    * 🔔 **Smart Notifications** - Never forget about expiring food
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(recipe_router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(shopping_router, prefix="/api/shopping-list", tags=["Shopping List"])
app.include_router(family_router, prefix="/api/family", tags=["Family Sharing"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "success": True,
        "message": "Welcome to FreshKeep API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "success": True,
        "status": "healthy",
        "service": "freshkeep-api",
    }
