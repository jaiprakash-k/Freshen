"""
Recipe Routes
Recipe discovery and recommendations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.services.recipe_service import RecipeService
from app.services.inventory_service import InventoryService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
recipe_service = RecipeService()
inventory_service = InventoryService()


@router.get("")
async def get_recipes(
    use_expiring: bool = Query(True),
    max_time: Optional[int] = None,
    diet: Optional[str] = None,
    cuisine: Optional[str] = None,
    limit: int = Query(15, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Get recipe recommendations based on inventory."""
    # Get expiring items
    expiring = await inventory_service.get_expiring_items(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
        days=3 if use_expiring else 7,
    )
    
    if not expiring:
        # Get all active items if no expiring
        result = await inventory_service.list_items(
            user_id=current_user["id"],
            family_id=current_user.get("family_id"),
            limit=20,
        )
        items = result["items"]
    else:
        items = expiring
    
    recipes = await recipe_service.get_recommendations_for_expiring(
        expiring_items=items,
        dietary_restrictions=[diet] if diet else None,
        limit=limit,
    )
    
    return success_response(data=recipes, total=len(recipes))


@router.get("/{recipe_id}")
async def get_recipe_detail(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get full recipe details."""
    recipe = await recipe_service.get_recipe_details(recipe_id)
    
    # Check which ingredients user has
    result = await inventory_service.list_items(
        user_id=current_user["id"],
        family_id=current_user.get("family_id"),
    )
    
    inventory_names = {item["name"].lower() for item in result["items"]}
    
    for ingredient in recipe.get("ingredients", []):
        ingredient["have_it"] = any(
            inv_name in ingredient["name"].lower() or ingredient["name"].lower() in inv_name
            for inv_name in inventory_names
        )
    
    return success_response(data=recipe)
