"""
Shopping List Routes
Shopping list management.
"""

from typing import List
from fastapi import APIRouter, Depends
from app.models.shopping import ShoppingItemCreate, ShoppingItemUpdate
from app.services.shopping_service import ShoppingService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
shopping_service = ShoppingService()


@router.get("")
async def get_shopping_list(current_user: dict = Depends(get_current_user)):
    """Get current shopping list."""
    result = await shopping_service.get_or_create_list(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
    )
    return success_response(data=result)


@router.post("")
async def add_item(item: ShoppingItemCreate, current_user: dict = Depends(get_current_user)):
    """Add item to shopping list."""
    result = await shopping_service.add_item(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        category=item.category,
        notes=item.notes,
    )
    return success_response(data=result, message="Item added")


@router.put("/{item_id}")
async def update_item(item_id: str, updates: ShoppingItemUpdate, current_user: dict = Depends(get_current_user)):
    """Update a shopping list item."""
    result = await shopping_service.update_item(item_id, current_user["id"], **updates.model_dump(exclude_unset=True))
    return success_response(data=result)


@router.post("/{item_id}/toggle")
async def toggle_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Toggle item checked status."""
    result = await shopping_service.toggle_checked(item_id, current_user["id"])
    return success_response(data=result)


@router.delete("/{item_id}")
async def delete_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a shopping list item."""
    await shopping_service.delete_item(item_id, current_user["id"])
    return success_response(message="Item deleted")


@router.post("/clear-checked")
async def clear_checked(current_user: dict = Depends(get_current_user)):
    """Clear all checked items."""
    count = await shopping_service.clear_checked(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
    )
    return success_response(message=f"Cleared {count} items")
