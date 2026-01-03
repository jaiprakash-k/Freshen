"""
Expiration Date Utilities
Smart expiration calculation and freshness tracking.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple

from app.config import SHELF_LIFE_DEFAULTS, FRESHNESS_THRESHOLDS


def calculate_expiration_date(
    category: str,
    purchase_date: Optional[date] = None,
    storage: str = "fridge",
    mode: str = "standard"
) -> date:
    """
    Calculate expiration date based on category and storage.
    
    Args:
        category: Item category (dairy, meat, vegetables, etc.)
        purchase_date: Date of purchase (defaults to today)
        storage: Storage location (fridge, freezer, pantry)
        mode: Expiration mode (conservative, standard, optimistic)
    
    Returns:
        Calculated expiration date
    """
    if purchase_date is None:
        purchase_date = date.today()
    
    # Get base shelf life for category
    base_days = SHELF_LIFE_DEFAULTS.get(category.lower(), SHELF_LIFE_DEFAULTS["other"])
    
    # Adjust for storage type
    if storage == "freezer":
        # Frozen items last much longer
        base_days = max(base_days * 10, 90)
    elif storage == "pantry":
        # Some items last longer in pantry (canned, dry goods)
        if category.lower() in ["canned", "grains", "snacks", "condiments"]:
            pass  # Keep default, these are already pantry-optimized
        else:
            # Fresh items don't last as long in pantry
            base_days = max(base_days // 2, 1)
    
    # Adjust for mode
    mode_multipliers = {
        "conservative": 0.7,
        "standard": 1.0,
        "optimistic": 1.3,
    }
    multiplier = mode_multipliers.get(mode, 1.0)
    adjusted_days = int(base_days * multiplier)
    
    return purchase_date + timedelta(days=adjusted_days)


def get_days_until_expiry(expiration_date: Optional[date]) -> Optional[int]:
    """
    Calculate days until expiration.
    
    Args:
        expiration_date: Item's expiration date
    
    Returns:
        Number of days until expiry (negative if expired), or None if no date
    """
    if not expiration_date:
        return None
    
    if isinstance(expiration_date, datetime):
        expiration_date = expiration_date.date()
    
    today = date.today()
    delta = expiration_date - today
    return delta.days


def get_freshness_status(expiration_date: Optional[date]) -> str:
    """
    Get freshness status based on expiration date.
    
    Args:
        expiration_date: Item's expiration date
    
    Returns:
        Freshness status: 'fresh', 'warning', 'expires_today', or 'expired'
    """
    days = get_days_until_expiry(expiration_date)
    
    if days is None:
        return "fresh"  # No expiration date, assume fresh
    
    if days < 0:
        return "expired"
    elif days == 0:
        return "expires_today"
    elif days <= FRESHNESS_THRESHOLDS["warning"]:
        return "warning"
    else:
        return "fresh"


def get_freshness_color(status: str) -> str:
    """Get color code for freshness status."""
    colors = {
        "fresh": "#4CAF50",      # Green
        "warning": "#FF9800",    # Orange
        "expires_today": "#FF5722",  # Deep Orange
        "expired": "#F44336",    # Red
    }
    return colors.get(status, "#9E9E9E")


def categorize_items_by_freshness(items: list) -> dict:
    """
    Categorize items into freshness groups.
    
    Args:
        items: List of items with 'expiration_date' field
    
    Returns:
        Dictionary with items grouped by freshness status
    """
    categories = {
        "expired": [],
        "expires_today": [],
        "warning": [],
        "fresh": [],
    }
    
    for item in items:
        exp_date = item.get("expiration_date")
        if isinstance(exp_date, str):
            exp_date = datetime.fromisoformat(exp_date.replace("Z", "+00:00")).date()
        
        status = get_freshness_status(exp_date)
        categories[status].append(item)
    
    return categories


def get_expiring_soon(items: list, days: int = 3) -> list:
    """
    Get items expiring within specified days.
    
    Args:
        items: List of items
        days: Number of days to look ahead
    
    Returns:
        List of items expiring within the specified days
    """
    expiring = []
    today = date.today()
    threshold = today + timedelta(days=days)
    
    for item in items:
        exp_date = item.get("expiration_date")
        if not exp_date:
            continue
        
        if isinstance(exp_date, str):
            exp_date = datetime.fromisoformat(exp_date.replace("Z", "+00:00")).date()
        elif isinstance(exp_date, datetime):
            exp_date = exp_date.date()
        
        if today <= exp_date <= threshold:
            expiring.append(item)
    
    # Sort by expiration date (soonest first)
    expiring.sort(key=lambda x: x.get("expiration_date", "9999-12-31"))
    
    return expiring


def estimate_food_value(category: str, quantity: float, unit: str) -> float:
    """
    Estimate the monetary value of food items.
    Used for savings/waste calculations.
    
    Args:
        category: Item category
        quantity: Item quantity
        unit: Unit of measurement
    
    Returns:
        Estimated value in dollars
    """
    # Average prices per unit by category (rough estimates)
    category_prices = {
        "dairy": {"liter": 2.0, "piece": 3.0, "kg": 8.0},
        "meat": {"kg": 12.0, "piece": 5.0},
        "poultry": {"kg": 8.0, "piece": 4.0},
        "fish": {"kg": 15.0, "piece": 8.0},
        "vegetables": {"kg": 3.0, "piece": 0.5},
        "fruits": {"kg": 4.0, "piece": 0.75},
        "bread": {"piece": 3.0, "kg": 4.0},
        "eggs": {"piece": 0.25, "dozen": 3.0},
        "frozen": {"kg": 6.0, "piece": 4.0},
        "canned": {"piece": 2.0},
        "condiments": {"piece": 4.0, "liter": 5.0},
        "beverages": {"liter": 2.0, "piece": 1.5},
        "snacks": {"piece": 3.0, "kg": 8.0},
        "grains": {"kg": 3.0, "piece": 2.0},
        "other": {"piece": 2.0, "kg": 5.0},
    }
    
    prices = category_prices.get(category.lower(), category_prices["other"])
    unit_price = prices.get(unit.lower(), prices.get("piece", 2.0))
    
    return round(quantity * unit_price, 2)


def estimate_environmental_impact(category: str, quantity: float, unit: str) -> Tuple[float, float]:
    """
    Estimate environmental impact of food waste.
    
    Args:
        category: Item category
        quantity: Item quantity
        unit: Unit of measurement
    
    Returns:
        Tuple of (CO2 in kg, Water in liters) saved/wasted
    """
    # CO2 emissions per kg of food (rough estimates)
    co2_per_kg = {
        "meat": 27.0,
        "poultry": 6.9,
        "fish": 5.0,
        "dairy": 3.2,
        "eggs": 4.8,
        "vegetables": 2.0,
        "fruits": 1.1,
        "grains": 2.7,
        "bread": 1.5,
        "other": 2.5,
    }
    
    # Water usage per kg of food (liters)
    water_per_kg = {
        "meat": 15400,
        "poultry": 4300,
        "fish": 3500,
        "dairy": 1000,
        "eggs": 3300,
        "vegetables": 300,
        "fruits": 800,
        "grains": 1600,
        "bread": 1600,
        "other": 1000,
    }
    
    # Convert quantity to kg if needed
    kg_quantity = quantity
    if unit.lower() in ["piece", "pieces"]:
        kg_quantity = quantity * 0.15  # Assume average piece is ~150g
    elif unit.lower() in ["liter", "liters", "l"]:
        kg_quantity = quantity  # Assume 1L ≈ 1kg
    
    co2 = round(kg_quantity * co2_per_kg.get(category.lower(), 2.5), 2)
    water = round(kg_quantity * water_per_kg.get(category.lower(), 1000), 0)
    
    return co2, water
