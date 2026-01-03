"""
Shopping List Models
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ShoppingItemCreate(BaseModel):
    """Request model for adding shopping item."""
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="piece", max_length=20)
    category: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=200)


class ShoppingItemUpdate(BaseModel):
    """Request model for updating shopping item."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    checked: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=200)


class ShoppingItemResponse(BaseModel):
    """Response model for shopping item."""
    id: str
    list_id: str
    name: str
    quantity: float
    unit: str
    category: Optional[str] = None
    checked: bool = False
    added_by: str
    added_by_name: Optional[str] = None
    notes: Optional[str] = None
    auto_generated: bool = False  # True if generated from low stock
    created_at: datetime

    class Config:
        from_attributes = True


class ShoppingListResponse(BaseModel):
    """Response model for shopping list."""
    success: bool = True
    id: str
    family_id: Optional[str] = None
    name: str
    items: List[ShoppingItemResponse]
    total_items: int
    checked_items: int
    updated_at: datetime

    class Config:
        from_attributes = True


class ShoppingListImportRequest(BaseModel):
    """Request for importing purchased items to inventory."""
    item_ids: List[str]  # IDs of shopping items to import
    clear_checked: bool = True  # Remove checked items after import
