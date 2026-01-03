"""
Inventory Service
Core CRUD operations for grocery inventory management.
"""

from datetime import datetime, date
from typing import Optional, List
import uuid

from app.database import get_supabase_client, Tables
from app.config import get_settings
from app.utils.expiration import (
    calculate_expiration_date,
    get_freshness_status,
    get_days_until_expiry,
    estimate_food_value,
    estimate_environmental_impact,
)
from app.middleware.error_handler import NotFoundError, ForbiddenError


class InventoryService:
    """Service for inventory management operations."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def list_items(
        self,
        user_id: str,
        family_id: Optional[str] = None,
        status: str = "active",
        category: Optional[str] = None,
        storage: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """
        List inventory items with filters.
        
        Args:
            user_id: Current user ID
            family_id: Family ID (for shared inventory)
            status: Item status filter (active, consumed, wasted, expired)
            category: Category filter
            storage: Storage location filter
            search: Search term for item name
            limit: Max items to return
            offset: Pagination offset
        
        Returns:
            List of items with counts
        """
        query = self.supabase.table(Tables.ITEMS).select("*")
        
        # Filter by user or family
        if family_id:
            query = query.eq("family_id", family_id)
        else:
            query = query.eq("user_id", user_id)
        
        # Apply filters
        if status:
            query = query.eq("status", status)
        if category:
            query = query.eq("category", category)
        if storage:
            query = query.eq("storage", storage)
        if search:
            query = query.ilike("name", f"%{search}%")
        
        # Order by expiration date (soonest first)
        query = query.order("expiration_date", desc=False)
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        items = result.data or []
        
        # Enrich items with freshness info
        enriched_items = [self._enrich_item(item) for item in items]
        
        # Get counts
        expiring_count = sum(1 for item in enriched_items if item["freshness"] in ["warning", "expires_today"])
        expired_count = sum(1 for item in enriched_items if item["freshness"] == "expired")
        
        return {
            "items": enriched_items,
            "total": len(enriched_items),
            "expiring_count": expiring_count,
            "expired_count": expired_count,
        }
    
    async def get_expiring_items(
        self,
        user_id: str,
        family_id: Optional[str] = None,
        days: int = 3
    ) -> List[dict]:
        """Get items expiring within specified days."""
        result = await self.list_items(
            user_id=user_id,
            family_id=family_id,
            status="active"
        )
        
        expiring = []
        today = date.today()
        
        for item in result["items"]:
            days_left = item.get("days_until_expiry")
            if days_left is not None and 0 <= days_left <= days:
                expiring.append(item)
        
        return expiring
    
    async def get_expired_items(
        self,
        user_id: str,
        family_id: Optional[str] = None
    ) -> List[dict]:
        """Get all expired items."""
        result = await self.list_items(
            user_id=user_id,
            family_id=family_id,
            status="active"
        )
        
        return [item for item in result["items"] if item["freshness"] == "expired"]
    
    async def get_item(self, item_id: str, user_id: str) -> dict:
        """Get single item by ID."""
        result = self.supabase.table(Tables.ITEMS).select("*").eq(
            "id", item_id
        ).execute()
        
        if not result.data:
            raise NotFoundError("Item")
        
        item = result.data[0]
        
        # Verify ownership
        if item["user_id"] != user_id and item.get("family_id") is None:
            raise ForbiddenError("You don't have access to this item")
        
        return self._enrich_item(item)
    
    async def create_item(
        self,
        user_id: str,
        name: str,
        quantity: float,
        unit: str = "piece",
        category: str = "other",
        storage: str = "fridge",
        purchase_date: Optional[date] = None,
        expiration_date: Optional[date] = None,
        notes: Optional[str] = None,
        photo_url: Optional[str] = None,
        family_id: Optional[str] = None
    ) -> dict:
        """
        Create a new inventory item.
        
        Auto-calculates expiration date if not provided.
        """
        item_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Auto-calculate expiration if not provided
        if not expiration_date:
            expiration_date = calculate_expiration_date(
                category=category,
                purchase_date=purchase_date,
                storage=storage
            )
        
        item_data = {
            "id": item_id,
            "user_id": user_id,
            "family_id": family_id,
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "category": category,
            "storage": storage,
            "purchase_date": (purchase_date or date.today()).isoformat(),
            "expiration_date": expiration_date.isoformat() if expiration_date else None,
            "status": "active",
            "notes": notes,
            "photo_url": photo_url,
            "created_at": now,
            "updated_at": now,
        }
        
        result = self.supabase.table(Tables.ITEMS).insert(item_data).execute()
        
        if not result.data:
            raise Exception("Failed to create item")
        
        return self._enrich_item(result.data[0])
    
    async def update_item(
        self,
        item_id: str,
        user_id: str,
        **updates
    ) -> dict:
        """Update an inventory item."""
        # Verify ownership first
        await self.get_item(item_id, user_id)
        
        # Filter allowed updates
        allowed_fields = [
            "name", "quantity", "unit", "category", "storage",
            "expiration_date", "notes", "photo_url"
        ]
        
        update_data = {
            k: v for k, v in updates.items()
            if k in allowed_fields and v is not None
        }
        
        if not update_data:
            return await self.get_item(item_id, user_id)
        
        # Handle date conversion
        if "expiration_date" in update_data:
            exp = update_data["expiration_date"]
            if isinstance(exp, date):
                update_data["expiration_date"] = exp.isoformat()
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = self.supabase.table(Tables.ITEMS).update(update_data).eq(
            "id", item_id
        ).execute()
        
        return self._enrich_item(result.data[0])
    
    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete (soft delete) an item."""
        await self.get_item(item_id, user_id)
        
        self.supabase.table(Tables.ITEMS).update({
            "status": "deleted",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", item_id).execute()
        
        return True
    
    async def consume_item(
        self,
        item_id: str,
        user_id: str,
        quantity_consumed: Optional[float] = None,
        notes: Optional[str] = None
    ) -> dict:
        """
        Mark item as consumed (fully or partially).
        
        Args:
            item_id: Item to consume
            user_id: Current user
            quantity_consumed: Amount consumed (None = all)
            notes: Optional consumption notes
        
        Returns:
            Updated item (or deleted if fully consumed)
        """
        item = await self.get_item(item_id, user_id)
        now = datetime.utcnow()
        
        # Log consumption
        log_data = {
            "id": str(uuid.uuid4()),
            "item_id": item_id,
            "user_id": user_id,
            "quantity_consumed": quantity_consumed or item["quantity"],
            "consumed_at": now.isoformat(),
            "notes": notes,
        }
        
        try:
            self.supabase.table(Tables.CONSUMPTION_LOGS).insert(log_data).execute()
        except Exception:
            pass  # Table might not exist
        
        # Update item
        if quantity_consumed and quantity_consumed < item["quantity"]:
            # Partial consumption
            new_quantity = item["quantity"] - quantity_consumed
            result = self.supabase.table(Tables.ITEMS).update({
                "quantity": new_quantity,
                "updated_at": now.isoformat()
            }).eq("id", item_id).execute()
            return self._enrich_item(result.data[0])
        else:
            # Full consumption
            result = self.supabase.table(Tables.ITEMS).update({
                "status": "consumed",
                "updated_at": now.isoformat()
            }).eq("id", item_id).execute()
            return self._enrich_item(result.data[0])
    
    async def waste_item(
        self,
        item_id: str,
        user_id: str,
        reason: str = "forgot",
        feedback_text: Optional[str] = None,
        photo_url: Optional[str] = None
    ) -> dict:
        """
        Mark item as wasted.
        
        Args:
            item_id: Item to mark as wasted
            user_id: Current user
            reason: Waste reason (forgot, spoiled, tasted_bad, etc.)
            feedback_text: Optional feedback
            photo_url: Optional photo of wasted item
        
        Returns:
            Updated item
        """
        item = await self.get_item(item_id, user_id)
        now = datetime.utcnow()
        
        # Calculate waste impact
        value = estimate_food_value(item["category"], item["quantity"], item["unit"])
        co2, water = estimate_environmental_impact(item["category"], item["quantity"], item["unit"])
        
        # Log waste
        log_data = {
            "id": str(uuid.uuid4()),
            "item_id": item_id,
            "user_id": user_id,
            "wasted_at": now.isoformat(),
            "reason": reason,
            "feedback_text": feedback_text,
            "photo_url": photo_url,
            "estimated_value": value,
            "co2_impact_kg": co2,
            "water_impact_liters": water,
        }
        
        try:
            self.supabase.table(Tables.WASTE_LOGS).insert(log_data).execute()
        except Exception:
            pass  # Table might not exist
        
        # Update item status
        result = self.supabase.table(Tables.ITEMS).update({
            "status": "wasted",
            "updated_at": now.isoformat()
        }).eq("id", item_id).execute()
        
        return self._enrich_item(result.data[0])
    
    async def bulk_add_items(
        self,
        user_id: str,
        items: List[dict],
        family_id: Optional[str] = None
    ) -> List[dict]:
        """Add multiple items at once (from receipt OCR)."""
        created_items = []
        
        for item_data in items:
            item = await self.create_item(
                user_id=user_id,
                family_id=family_id,
                name=item_data.get("name"),
                quantity=item_data.get("quantity", 1),
                unit=item_data.get("unit", "piece"),
                category=item_data.get("category", "other"),
                storage=item_data.get("storage", "fridge"),
                expiration_date=item_data.get("expiration_date"),
            )
            created_items.append(item)
        
        return created_items
    
    async def get_inventory_stats(
        self,
        user_id: str,
        family_id: Optional[str] = None
    ) -> dict:
        """Get inventory statistics."""
        result = await self.list_items(user_id=user_id, family_id=family_id, limit=1000)
        items = result["items"]
        
        # Category breakdown
        by_category = {}
        by_storage = {}
        by_freshness = {"fresh": 0, "warning": 0, "expires_today": 0, "expired": 0}
        
        total_value = 0
        
        for item in items:
            cat = item["category"]
            stor = item["storage"]
            fresh = item["freshness"]
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_storage[stor] = by_storage.get(stor, 0) + 1
            by_freshness[fresh] = by_freshness.get(fresh, 0) + 1
            
            total_value += estimate_food_value(cat, item["quantity"], item["unit"])
        
        return {
            "total_items": len(items),
            "by_category": by_category,
            "by_storage": by_storage,
            "by_freshness": by_freshness,
            "estimated_value": round(total_value, 2),
            "expiring_count": result["expiring_count"],
            "expired_count": result["expired_count"],
        }
    
    def _enrich_item(self, item: dict) -> dict:
        """Add computed fields to item."""
        exp_date_str = item.get("expiration_date")
        exp_date = None
        
        if exp_date_str:
            if isinstance(exp_date_str, str):
                exp_date = datetime.fromisoformat(exp_date_str.replace("Z", "+00:00")).date()
            elif isinstance(exp_date_str, datetime):
                exp_date = exp_date_str.date()
            elif isinstance(exp_date_str, date):
                exp_date = exp_date_str
        
        days_until = get_days_until_expiry(exp_date)
        freshness = get_freshness_status(exp_date)
        
        return {
            **item,
            "days_until_expiry": days_until,
            "freshness": freshness,
        }
