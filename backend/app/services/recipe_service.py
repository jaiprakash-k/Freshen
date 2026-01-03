"""
Recipe Service
Recipe discovery and recommendations using Spoonacular API.
"""

import httpx
from typing import List, Optional

from app.config import get_settings
from app.middleware.error_handler import ExternalAPIError


class RecipeService:
    """Service for recipe discovery and recommendations."""
    
    SPOONACULAR_BASE_URL = "https://api.spoonacular.com"
    
    def __init__(self):
        self.settings = get_settings()
    
    async def search_recipes(
        self,
        ingredients: List[str],
        expiring_ingredients: Optional[List[str]] = None,
        diet: Optional[str] = None,
        cuisine: Optional[str] = None,
        max_ready_time: Optional[int] = None,
        limit: int = 15
    ) -> List[dict]:
        """
        Search recipes based on available ingredients.
        
        Args:
            ingredients: List of ingredient names
            expiring_ingredients: Subset that are expiring soon (for scoring)
            diet: Dietary restriction (vegetarian, vegan, etc.)
            cuisine: Preferred cuisine
            max_ready_time: Maximum cooking time in minutes
            limit: Number of results
        
        Returns:
            List of recipes with scores
        """
        if not self.settings.spoonacular_api_key:
            # Return mock data if no API key
            return self._get_mock_recipes(ingredients, expiring_ingredients)
        
        # Build search query
        params = {
            "apiKey": self.settings.spoonacular_api_key,
            "ingredients": ",".join(ingredients[:10]),  # API limit
            "number": limit,
            "ranking": 2,  # Maximize used ingredients
            "ignorePantry": True,
        }
        
        url = f"{self.SPOONACULAR_BASE_URL}/recipes/findByIngredients"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                recipes = response.json()
                
                # Score and format recipes
                scored_recipes = []
                for recipe in recipes:
                    score = self._calculate_score(
                        recipe,
                        expiring_ingredients or []
                    )
                    
                    # Identify which expiring ingredients this recipe uses
                    used_ingredients = [ing["name"].lower() for ing in recipe.get("usedIngredients", [])]
                    uses_expiring = [
                        exp for exp in (expiring_ingredients or [])
                        if any(exp.lower() in used for used in used_ingredients)
                    ]
                    
                    scored_recipes.append({
                        "id": recipe["id"],
                        "title": recipe["title"],
                        "image": recipe.get("image"),
                        "ready_in_minutes": 30,  # Default, need to fetch details
                        "servings": 4,
                        "score": score,
                        "uses_expiring": uses_expiring,
                        "missing_ingredients_count": recipe.get("missedIngredientCount", 0),
                        "used_ingredients_count": recipe.get("usedIngredientCount", 0),
                    })
                
                # Sort by score
                scored_recipes.sort(key=lambda x: x["score"], reverse=True)
                return scored_recipes
                
        except httpx.HTTPError as e:
            raise ExternalAPIError("Spoonacular", str(e))
    
    async def get_recipe_details(self, recipe_id: int) -> dict:
        """
        Get full recipe details including instructions.
        
        Args:
            recipe_id: Spoonacular recipe ID
        
        Returns:
            Full recipe with ingredients and instructions
        """
        if not self.settings.spoonacular_api_key:
            return self._get_mock_recipe_detail(recipe_id)
        
        params = {
            "apiKey": self.settings.spoonacular_api_key,
            "includeNutrition": True,
        }
        
        url = f"{self.SPOONACULAR_BASE_URL}/recipes/{recipe_id}/information"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                recipe = response.json()
                
                # Format ingredients
                ingredients = []
                for ing in recipe.get("extendedIngredients", []):
                    ingredients.append({
                        "name": ing.get("name", ""),
                        "amount": ing.get("amount", 0),
                        "unit": ing.get("unit", ""),
                        "have_it": False,  # Will be set by caller
                    })
                
                # Extract nutrition if available
                nutrition = recipe.get("nutrition", {})
                nutrients = {n["name"]: n for n in nutrition.get("nutrients", [])}
                
                return {
                    "id": recipe["id"],
                    "title": recipe["title"],
                    "image": recipe.get("image"),
                    "source_url": recipe.get("sourceUrl"),
                    "ready_in_minutes": recipe.get("readyInMinutes", 30),
                    "servings": recipe.get("servings", 4),
                    "summary": recipe.get("summary"),
                    "instructions": recipe.get("instructions"),
                    "ingredients": ingredients,
                    "uses_expiring": [],
                    "score": 0,
                    "calories": int(nutrients.get("Calories", {}).get("amount", 0)),
                    "protein": f"{nutrients.get('Protein', {}).get('amount', 0)}g",
                    "fat": f"{nutrients.get('Fat', {}).get('amount', 0)}g",
                    "carbs": f"{nutrients.get('Carbohydrates', {}).get('amount', 0)}g",
                }
                
        except httpx.HTTPError as e:
            raise ExternalAPIError("Spoonacular", str(e))
    
    async def get_recommendations_for_expiring(
        self,
        expiring_items: List[dict],
        dietary_restrictions: Optional[List[str]] = None,
        limit: int = 15
    ) -> List[dict]:
        """
        Get recipe recommendations specifically for expiring items.
        
        Args:
            expiring_items: List of items with name, days_until_expiry
            dietary_restrictions: User's dietary preferences
            limit: Number of recipes to return
        
        Returns:
            Scored and ranked recipe recommendations
        """
        if not expiring_items:
            return []
        
        # Sort by urgency (expiring soonest first)
        sorted_items = sorted(
            expiring_items,
            key=lambda x: x.get("days_until_expiry", 999)
        )
        
        # Extract ingredient names
        all_ingredients = [item["name"] for item in sorted_items]
        expiring_soon = [
            item["name"] for item in sorted_items
            if item.get("days_until_expiry", 999) <= 2
        ]
        
        # Search recipes
        recipes = await self.search_recipes(
            ingredients=all_ingredients,
            expiring_ingredients=expiring_soon,
            diet=dietary_restrictions[0] if dietary_restrictions else None,
            limit=limit
        )
        
        return recipes
    
    def _calculate_score(
        self,
        recipe: dict,
        expiring_ingredients: List[str]
    ) -> float:
        """
        Calculate recommendation score for a recipe.
        
        Score formula:
        - uses_today: +10 per ingredient
        - uses_soon: +5 per ingredient
        - used ingredients: +3 per ingredient
        - missing ingredients: -2 per ingredient
        - quick meal (<30min): +2
        - zero waste (no missing): +5
        """
        score = 0.0
        
        used_ingredients = recipe.get("usedIngredients", [])
        used_names = [ing["name"].lower() for ing in used_ingredients]
        
        # Points for using expiring ingredients
        for exp_ing in expiring_ingredients:
            if any(exp_ing.lower() in used for used in used_names):
                score += 10  # Uses expiring ingredient
        
        # Points for used ingredients
        score += len(used_ingredients) * 3
        
        # Penalty for missing ingredients
        missing_count = recipe.get("missedIngredientCount", 0)
        score -= missing_count * 2
        
        # Bonus for zero waste (no missing ingredients)
        if missing_count == 0:
            score += 5
        
        return max(score, 0)
    
    # Indian Recipe Database
    INDIAN_RECIPES = [
        # Tea Recipes
        {
            "id": 1001, "title": "Masala Chai", "image": "https://www.recipetineats.com/wp-content/uploads/2022/10/Masala-Chai_1.jpg",
            "ready_in_minutes": 15, "servings": 4, "category": "beverages",
            "ingredients": ["tea", "milk", "ginger", "cardamom", "cinnamon", "sugar"],
            "instructions": "1. Boil water with ginger, cardamom, and cinnamon for 5 mins.\n2. Add tea powder and boil for 2 mins.\n3. Add milk and sugar.\n4. Simmer for 5 mins and strain.",
        },
        {
            "id": 1002, "title": "Ginger Tea (Adrak Chai)", "image": "https://www.teaforturmeric.com/wp-content/uploads/2022/01/Ginger-Tea-Social-1.jpg",
            "ready_in_minutes": 10, "servings": 2, "category": "beverages",
            "ingredients": ["tea", "ginger", "milk", "sugar"],
            "instructions": "1. Crush ginger and boil in water for 3 mins.\n2. Add tea powder and simmer.\n3. Add milk and sugar to taste.\n4. Strain and serve hot.",
        },
        {
            "id": 1003, "title": "Elaichi Tea (Cardamom Tea)", "image": "https://www.teaforturmeric.com/wp-content/uploads/2021/12/Cardamom-Tea-5.jpg",
            "ready_in_minutes": 10, "servings": 2, "category": "beverages",
            "ingredients": ["tea", "cardamom", "milk", "sugar"],
            "instructions": "1. Crush cardamom and boil in water.\n2. Add tea powder and simmer 2 mins.\n3. Add milk and sugar.\n4. Strain and enjoy.",
        },
        {
            "id": 1004, "title": "Lemon Tea", "image": "https://i.pinimg.com/originals/6a/eb/cf/6aebcf04a5b12c7f64e3d94e5e1a77a9.jpg",
            "ready_in_minutes": 8, "servings": 2, "category": "beverages",
            "ingredients": ["tea", "lemon", "honey", "sugar"],
            "instructions": "1. Boil water and add tea powder.\n2. Steep for 3 mins.\n3. Strain and add lemon juice.\n4. Sweeten with honey or sugar.",
        },
        # Milk-based dishes
        {
            "id": 1010, "title": "Paneer Butter Masala", "image": "https://www.cubesnjuliennes.com/wp-content/uploads/2020/01/Paneer-Butter-Masala-Recipe.jpg",
            "ready_in_minutes": 40, "servings": 4, "category": "main",
            "ingredients": ["paneer", "butter", "tomato", "cream", "onion", "ginger", "garlic"],
            "instructions": "1. Saute onion, ginger, garlic.\n2. Add tomato puree and cook.\n3. Add cream and butter.\n4. Add paneer cubes and simmer.",
        },
        {
            "id": 1011, "title": "Kheer (Rice Pudding)", "image": "https://www.vegrecipesofindia.com/wp-content/uploads/2021/04/kheer-recipe-1.jpg",
            "ready_in_minutes": 45, "servings": 6, "category": "dessert",
            "ingredients": ["milk", "rice", "sugar", "cardamom", "almonds", "cashews"],
            "instructions": "1. Wash and soak rice for 30 mins.\n2. Boil milk and add rice.\n3. Cook on low heat until thick.\n4. Add sugar, cardamom, and nuts.",
        },
        # Dal recipes
        {
            "id": 1020, "title": "Dal Tadka", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2022/01/dal-tadka-recipe.jpg",
            "ready_in_minutes": 35, "servings": 4, "category": "main",
            "ingredients": ["toor dal", "onion", "tomato", "cumin", "mustard", "turmeric", "red chilli"],
            "instructions": "1. Pressure cook dal with turmeric.\n2. Prepare tadka with cumin, mustard, onion.\n3. Add tomatoes and cook.\n4. Mix tadka with dal.",
        },
        {
            "id": 1021, "title": "Dal Makhani", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2022/03/dal-makhani-recipe.jpg",
            "ready_in_minutes": 60, "servings": 6, "category": "main",
            "ingredients": ["urad dal", "rajma", "butter", "cream", "tomato", "onion", "ginger", "garlic"],
            "instructions": "1. Soak and pressure cook dals.\n2. Make gravy with butter, onion, tomato.\n3. Add cooked dal and simmer.\n4. Finish with cream.",
        },
        # Rice dishes
        {
            "id": 1030, "title": "Vegetable Pulao", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2022/02/veg-pulao-recipe.jpg",
            "ready_in_minutes": 30, "servings": 4, "category": "main",
            "ingredients": ["rice", "carrot", "beans", "peas", "onion", "cumin", "bay leaf"],
            "instructions": "1. Saute whole spices and onion.\n2. Add vegetables and rice.\n3. Add water and cook.\n4. Garnish with coriander.",
        },
        {
            "id": 1031, "title": "Lemon Rice", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2021/07/lemon-rice-recipe.jpg",
            "ready_in_minutes": 20, "servings": 4, "category": "main",
            "ingredients": ["rice", "lemon", "mustard", "turmeric", "curry leaves", "peanuts"],
            "instructions": "1. Cook rice and cool.\n2. Prepare tempering with mustard, turmeric.\n3. Add peanuts and curry leaves.\n4. Mix with rice and lemon juice.",
        },
        # Bread and Roti
        {
            "id": 1040, "title": "Aloo Paratha", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2021/08/aloo-paratha-recipe.jpg",
            "ready_in_minutes": 40, "servings": 4, "category": "bread",
            "ingredients": ["atta", "potato", "cumin", "coriander", "green chilli", "butter"],
            "instructions": "1. Boil and mash potatoes.\n2. Add spices for filling.\n3. Make dough and stuff with filling.\n4. Cook on tawa with butter.",
        },
        # Maggi recipes
        {
            "id": 1050, "title": "Vegetable Maggi", "image": "https://i.ytimg.com/vi/rNQhMe7K4I0/maxresdefault.jpg",
            "ready_in_minutes": 15, "servings": 2, "category": "snacks",
            "ingredients": ["maggi", "noodles", "carrot", "beans", "peas", "onion"],
            "instructions": "1. Boil water and add vegetables.\n2. Add maggi and tastemaker.\n3. Cook for 2-3 minutes.\n4. Serve hot.",
        },
        {
            "id": 1051, "title": "Masala Maggi", "image": "https://i.ytimg.com/vi/dNHKBSi2cFo/maxresdefault.jpg",
            "ready_in_minutes": 12, "servings": 2, "category": "snacks",
            "ingredients": ["maggi", "noodles", "onion", "tomato", "green chilli"],
            "instructions": "1. Saute onions and tomatoes.\n2. Add water and boil.\n3. Add maggi and tastemaker.\n4. Cook and serve.",
        },
        # Snacks
        {
            "id": 1060, "title": "Masala Omelette", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2021/11/masala-omelette-recipe.jpg",
            "ready_in_minutes": 10, "servings": 1, "category": "breakfast",
            "ingredients": ["eggs", "onion", "tomato", "green chilli", "coriander"],
            "instructions": "1. Beat eggs with salt.\n2. Add chopped onion, tomato, chilli.\n3. Cook on pan with oil.\n4. Fold and serve.",
        },
        {
            "id": 1061, "title": "Bread Omelette", "image": "https://i.ytimg.com/vi/f7C_eE9N7Oc/maxresdefault.jpg",
            "ready_in_minutes": 15, "servings": 2, "category": "breakfast",
            "ingredients": ["eggs", "bread", "onion", "butter"],
            "instructions": "1. Beat eggs with salt and pepper.\n2. Dip bread in egg mixture.\n3. Toast on buttered pan.\n4. Serve hot.",
        },
        # Chips/Namkeen based
        {
            "id": 1070, "title": "Bhel Puri", "image": "https://www.indianhealthyrecipes.com/wp-content/uploads/2022/07/bhel-puri-recipe.jpg",
            "ready_in_minutes": 10, "servings": 4, "category": "snacks",
            "ingredients": ["puffed rice", "onion", "tomato", "coriander", "lemon", "chutney", "sev"],
            "instructions": "1. Mix puffed rice with onion, tomato.\n2. Add chutneys and lemon juice.\n3. Top with sev and coriander.\n4. Serve immediately.",
        },
    ]
    
    def _get_mock_recipes(
        self,
        ingredients: List[str],
        expiring: Optional[List[str]] = None
    ) -> List[dict]:
        """Return Indian recipes matching user's ingredients."""
        ingredients_lower = [ing.lower() for ing in ingredients]
        
        # Score each recipe based on matching ingredients
        scored_recipes = []
        for recipe in self.INDIAN_RECIPES:
            recipe_ingredients = [ing.lower() for ing in recipe["ingredients"]]
            
            # Count matching ingredients
            matches = 0
            matched_ingredients = []
            for user_ing in ingredients_lower:
                for recipe_ing in recipe_ingredients:
                    if user_ing in recipe_ing or recipe_ing in user_ing:
                        matches += 1
                        matched_ingredients.append(user_ing)
                        break
            
            if matches > 0:
                # Calculate score
                score = matches * 10  # 10 points per matching ingredient
                missing = len(recipe_ingredients) - matches
                score -= missing * 2  # -2 points for missing
                
                # Bonus for using expiring ingredients
                uses_expiring = []
                if expiring:
                    for exp in expiring:
                        if any(exp.lower() in ri or ri in exp.lower() for ri in recipe_ingredients):
                            score += 15  # Extra bonus for expiring
                            uses_expiring.append(exp)
                
                scored_recipes.append({
                    "id": recipe["id"],
                    "title": recipe["title"],
                    "image": recipe["image"],
                    "ready_in_minutes": recipe["ready_in_minutes"],
                    "servings": recipe["servings"],
                    "score": max(score, 0),
                    "uses_expiring": uses_expiring,
                    "missing_ingredients_count": missing,
                    "used_ingredients_count": matches,
                })
        
        # Sort by score (highest first)
        scored_recipes.sort(key=lambda x: x["score"], reverse=True)
        
        # If no matches, return top recipes
        if not scored_recipes:
            return [{
                "id": r["id"],
                "title": r["title"],
                "image": r["image"],
                "ready_in_minutes": r["ready_in_minutes"],
                "servings": r["servings"],
                "score": 5,
                "uses_expiring": [],
                "missing_ingredients_count": len(r["ingredients"]),
                "used_ingredients_count": 0,
            } for r in self.INDIAN_RECIPES[:5]]
        
        return scored_recipes[:15]
    
    def _get_mock_recipe_detail(self, recipe_id: int) -> dict:
        """Return mock recipe detail from Indian database."""
        # Find recipe by ID
        recipe = None
        for r in self.INDIAN_RECIPES:
            if r["id"] == recipe_id:
                recipe = r
                break
        
        if not recipe:
            recipe = self.INDIAN_RECIPES[0]  # Default to first recipe
        
        return {
            "id": recipe["id"],
            "title": recipe["title"],
            "image": recipe["image"],
            "source_url": None,
            "ready_in_minutes": recipe["ready_in_minutes"],
            "servings": recipe["servings"],
            "summary": f"A delicious Indian recipe for {recipe['title']}.",
            "instructions": recipe.get("instructions", "Follow traditional preparation method."),
            "ingredients": [
                {"name": ing, "amount": 1, "unit": "as needed", "have_it": False}
                for ing in recipe["ingredients"]
            ],
            "uses_expiring": [],
            "score": 0,
            "calories": 250,
            "protein": "8g",
            "fat": "10g",
            "carbs": "30g",
        }
