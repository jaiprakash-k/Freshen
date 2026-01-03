"""
Inventory Routes
CRUD operations for grocery items.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from app.models.item import ItemCreate, ItemUpdate, ItemResponse, ItemConsumeRequest, ItemWasteRequest, ItemListResponse
from app.services.inventory_service import InventoryService
from app.services.ocr_service import OCRService
from app.services.barcode_service import BarcodeService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
inventory_service = InventoryService()
ocr_service = OCRService()
barcode_service = BarcodeService()


@router.get("")
async def list_items(
    status: str = Query("active"),
    category: Optional[str] = None,
    storage: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
):
    """List all inventory items with optional filters."""
    result = await inventory_service.list_items(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
        status=status, category=category, storage=storage,
        search=search, limit=limit, offset=offset,
    )
    return ItemListResponse(
        data=[ItemResponse(**item) for item in result["items"]],
        total=result["total"],
        expiring_count=result["expiring_count"],
        expired_count=result["expired_count"],
    )


@router.get("/expiring")
async def get_expiring_items(
    days: int = Query(3, le=7),
    current_user: dict = Depends(get_current_user),
):
    """Get items expiring within specified days."""
    items = await inventory_service.get_expiring_items(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
        days=days,
    )
    return success_response(data=items, count=len(items))


@router.get("/expired")
async def get_expired_items(current_user: dict = Depends(get_current_user)):
    """Get all expired items."""
    items = await inventory_service.get_expired_items(
        user_id=current_user["id"], family_id=current_user.get("family_id"))
    return success_response(data=items, count=len(items))


@router.get("/stats")
async def get_inventory_stats(current_user: dict = Depends(get_current_user)):
    """Get inventory statistics."""
    stats = await inventory_service.get_inventory_stats(
        user_id=current_user["id"], family_id=current_user.get("family_id"))
    return success_response(data=stats)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Get single item by ID."""
    item = await inventory_service.get_item(item_id, current_user["id"])
    return ItemResponse(**item)


@router.post("", response_model=ItemResponse)
async def create_item(item_data: ItemCreate, current_user: dict = Depends(get_current_user)):
    """Add a new item manually."""
    item = await inventory_service.create_item(
        user_id=current_user["id"], family_id=current_user.get("family_id"),
        name=item_data.name, quantity=item_data.quantity, unit=item_data.unit,
        category=item_data.category.value, storage=item_data.storage.value,
        purchase_date=item_data.purchase_date, expiration_date=item_data.expiration_date,
        notes=item_data.notes, photo_url=item_data.photo_url,
    )
    return ItemResponse(**item)


@router.post("/receipt")
async def add_from_receipt(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Parse receipt image and return extracted items."""
    contents = await file.read()
    result = await ocr_service.parse_receipt(image_file=contents)
    return success_response(data=result)


@router.post("/receipt/confirm")
async def confirm_receipt_items(items: list, current_user: dict = Depends(get_current_user)):
    """Confirm and add parsed receipt items to inventory."""
    created = await inventory_service.bulk_add_items(
        user_id=current_user["id"], items=items, family_id=current_user.get("family_id"))
    return success_response(data=created, message=f"Added {len(created)} items")


@router.get("/barcode/{upc}")
async def lookup_barcode(upc: str, current_user: dict = Depends(get_current_user)):
    """Look up product by barcode."""
    result = await barcode_service.lookup(upc)
    return success_response(data=result)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, updates: ItemUpdate, current_user: dict = Depends(get_current_user)):
    """Update an item."""
    item = await inventory_service.update_item(item_id, current_user["id"], **updates.model_dump(exclude_unset=True))
    return ItemResponse(**item)


@router.delete("/{item_id}")
async def delete_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an item."""
    await inventory_service.delete_item(item_id, current_user["id"])
    return success_response(message="Item deleted")


@router.post("/{item_id}/consume")
async def consume_item(item_id: str, data: ItemConsumeRequest, current_user: dict = Depends(get_current_user)):
    """Mark item as consumed."""
    item = await inventory_service.consume_item(
        item_id, current_user["id"], quantity_consumed=data.quantity_consumed, notes=data.notes)
    return success_response(data=item, message="Item consumed")


@router.post("/{item_id}/waste")
async def waste_item(item_id: str, data: ItemWasteRequest, current_user: dict = Depends(get_current_user)):
    """Mark item as wasted."""
    item = await inventory_service.waste_item(
        item_id, current_user["id"], reason=data.reason.value, feedback_text=data.feedback_text)
    return success_response(data=item, message="Item marked as wasted")
