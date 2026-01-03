"""
Recipe Models
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class RecipeIngredient(BaseModel):
    """Ingredient in a recipe."""
    name: str
    amount: float
    unit: str
    have_it: bool = False  # Whether user has this in inventory


class RecipeSearchParams(BaseModel):
    """Query parameters for recipe search."""
    use_expiring: bool = True
    max_time: Optional[int] = None  # Max cooking time in minutes
    diet: Optional[str] = None  # vegetarian, vegan, gluten-free, etc.
    cuisine: Optional[str] = None
    limit: int = Field(default=15, le=50)


class RecipeResponse(BaseModel):
    """Response model for recipe summary."""
    id: int
    title: str
    image: Optional[str] = None
    ready_in_minutes: int
    servings: int
    score: float  # Recommendation score based on expiring items
    uses_expiring: List[str] = []  # Names of expiring items used
    missing_ingredients_count: int

    class Config:
        from_attributes = True


class RecipeDetailResponse(BaseModel):
    """Response model for full recipe details."""
    id: int
    title: str
    image: Optional[str] = None
    source_url: Optional[str] = None
    ready_in_minutes: int
    servings: int
    summary: Optional[str] = None
    instructions: Optional[str] = None
    ingredients: List[RecipeIngredient]
    uses_expiring: List[str] = []
    score: float
    
    # Voice cooking
    voice_instructions_url: Optional[str] = None
    
    # Nutrition (optional)
    calories: Optional[int] = None
    protein: Optional[str] = None
    fat: Optional[str] = None
    carbs: Optional[str] = None

    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Response model for list of recipes."""
    success: bool = True
    data: List[RecipeResponse]
    total: int
