"""
Inventory Item Models
"""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ItemCategory(str, Enum):
    """Item category enumeration."""
    DAIRY = "dairy"
    MEAT = "meat"
    POULTRY = "poultry"
    FISH = "fish"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    BREAD = "bread"
    EGGS = "eggs"
    FROZEN = "frozen"
    CANNED = "canned"
    CONDIMENTS = "condiments"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    GRAINS = "grains"
    OTHER = "other"


class StorageType(str, Enum):
    """Storage location enumeration."""
    FRIDGE = "fridge"
    FREEZER = "freezer"
    PANTRY = "pantry"


class ItemStatus(str, Enum):
    """Item status enumeration."""
    ACTIVE = "active"
    CONSUMED = "consumed"
    WASTED = "wasted"
    EXPIRED = "expired"


class FreshnessStatus(str, Enum):
    """Item freshness status."""
    FRESH = "fresh"
    WARNING = "warning"
    EXPIRES_TODAY = "expires_today"
    EXPIRED = "expired"


class WasteReason(str, Enum):
    """Reasons for food waste."""
    FORGOT = "forgot"
    SPOILED = "spoiled"
    TASTED_BAD = "tasted_bad"
    TOO_MUCH = "too_much"
    CHANGED_PLANS = "changed_plans"
    OTHER = "other"


class ItemCreate(BaseModel):
    """Request model for creating an inventory item."""
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: str = Field(default="piece", max_length=20)
    category: ItemCategory = ItemCategory.OTHER
    storage: StorageType = StorageType.FRIDGE
    purchase_date: Optional[date] = None
    expiration_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = None


class ItemUpdate(BaseModel):
    """Request model for updating an inventory item."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    category: Optional[ItemCategory] = None
    storage: Optional[StorageType] = None
    expiration_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = None


class ItemConsumeRequest(BaseModel):
    """Request model for marking item as consumed."""
    quantity_consumed: Optional[float] = None  # If None, consume all
    notes: Optional[str] = None


class ItemWasteRequest(BaseModel):
    """Request model for marking item as wasted."""
    reason: WasteReason = WasteReason.FORGOT
    feedback_text: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = None


class ItemResponse(BaseModel):
    """Response model for inventory item."""
    id: str
    family_id: Optional[str] = None
    user_id: str
    name: str
    quantity: float
    unit: str
    category: str
    storage: str
    purchase_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    status: str
    freshness: str
    days_until_expiry: Optional[int] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """Response model for list of items."""
    success: bool = True
    data: List[ItemResponse]
    total: int
    expiring_count: int
    expired_count: int


class ReceiptItem(BaseModel):
    """Parsed item from receipt OCR."""
    name: str
    quantity: float = 1.0
    unit: str = "piece"
    suggested_category: ItemCategory = ItemCategory.OTHER
    suggested_expiry_days: int
    confidence: float = Field(..., ge=0, le=1)


class ReceiptParseResponse(BaseModel):
    """Response from receipt OCR parsing."""
    success: bool = True
    items: List[ReceiptItem]
    raw_text: Optional[str] = None
    warnings: List[str] = []


class BarcodeResponse(BaseModel):
    """Response from barcode lookup."""
    success: bool = True
    found: bool
    upc: str
    name: Optional[str] = None
    category: Optional[ItemCategory] = None
    suggested_expiry_days: Optional[int] = None
    brand: Optional[str] = None
