"""
Shopping List Service
Shopping list management with auto-generation.
"""

from datetime import datetime
from typing import List, Optional
import uuid

from app.database import get_supabase_client, Tables
from app.middleware.error_handler import NotFoundError


class ShoppingService:
    """Service for shopping list management."""
    
    LOW_STOCK_THRESHOLDS = {"piece": 1, "kg": 0.5, "liter": 0.5, "dozen": 0.5}
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_or_create_list(self, user_id: str, family_id: Optional[str] = None) -> dict:
        """Get current shopping list or create one."""
        query = self.supabase.table(Tables.SHOPPING_LISTS).select("*")
        if family_id:
            query = query.eq("family_id", family_id)
        else:
            query = query.eq("user_id", user_id)
        
        result = query.order("created_at", desc=True).limit(1).execute()
        
        if result.data:
            shopping_list = result.data[0]
        else:
            shopping_list = await self._create_list(user_id, family_id)
        
        items = await self._get_list_items(shopping_list["id"])
        
        return {
            "id": shopping_list["id"],
            "family_id": shopping_list.get("family_id"),
            "name": shopping_list.get("name", "Shopping List"),
            "items": items,
            "total_items": len(items),
            "checked_items": sum(1 for i in items if i.get("checked")),
            "updated_at": shopping_list.get("updated_at"),
        }
    
    async def add_item(self, user_id: str, name: str, quantity: float = 1,
                       unit: str = "piece", category: Optional[str] = None,
                       notes: Optional[str] = None, family_id: Optional[str] = None) -> dict:
        """Add item to shopping list."""
        shopping_list = await self.get_or_create_list(user_id, family_id)
        now = datetime.utcnow().isoformat()
        
        item_data = {
            "id": str(uuid.uuid4()),
            "list_id": shopping_list["id"],
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
            "notes": notes,
            "checked": False,
            "added_by": user_id,
            "auto_generated": False,
            "created_at": now,
        }
        
        result = self.supabase.table(Tables.SHOPPING_ITEMS).insert(item_data).execute()
        return result.data[0] if result.data else item_data
    
    async def update_item(self, item_id: str, user_id: str, **updates) -> dict:
        """Update a shopping list item."""
        allowed = ["name", "quantity", "unit", "checked", "notes"]
        update_data = {k: v for k, v in updates.items() if k in allowed and v is not None}
        
        result = self.supabase.table(Tables.SHOPPING_ITEMS).update(update_data).eq("id", item_id).execute()
        if not result.data:
            raise NotFoundError("Shopping item")
        return result.data[0]
    
    async def toggle_checked(self, item_id: str, user_id: str) -> dict:
        """Toggle item checked status."""
        result = self.supabase.table(Tables.SHOPPING_ITEMS).select("checked").eq("id", item_id).execute()
        if not result.data:
            raise NotFoundError("Shopping item")
        return await self.update_item(item_id, user_id, checked=not result.data[0]["checked"])
    
    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a shopping list item."""
        self.supabase.table(Tables.SHOPPING_ITEMS).delete().eq("id", item_id).execute()
        return True
    
    async def clear_checked(self, user_id: str, family_id: Optional[str] = None) -> int:
        """Clear all checked items from list."""
        shopping_list = await self.get_or_create_list(user_id, family_id)
        checked_count = sum(1 for i in shopping_list["items"] if i.get("checked"))
        self.supabase.table(Tables.SHOPPING_ITEMS).delete().eq(
            "list_id", shopping_list["id"]).eq("checked", True).execute()
        return checked_count
    
    async def _create_list(self, user_id: str, family_id: Optional[str] = None) -> dict:
        """Create a new shopping list."""
        now = datetime.utcnow().isoformat()
        list_data = {"id": str(uuid.uuid4()), "user_id": user_id, "family_id": family_id,
                     "name": "Shopping List", "created_at": now, "updated_at": now}
        result = self.supabase.table(Tables.SHOPPING_LISTS).insert(list_data).execute()
        return result.data[0] if result.data else list_data
    
    async def _get_list_items(self, list_id: str) -> List[dict]:
        """Get all items in a shopping list."""
        result = self.supabase.table(Tables.SHOPPING_ITEMS).select("*").eq(
            "list_id", list_id).order("created_at", desc=False).execute()
        return result.data or []
