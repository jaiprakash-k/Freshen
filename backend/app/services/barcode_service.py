"""
Barcode Service
Product lookup via barcode/UPC codes.
"""

import httpx
from typing import Optional

from app.config import SHELF_LIFE_DEFAULTS
from app.middleware.error_handler import ExternalAPIError


class BarcodeService:
    """Service for barcode product lookup."""
    
    # Open Food Facts API (free, no API key needed)
    OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v0/product"
    
    # UPCitemdb API (free tier - backup)
    UPCITEMDB_URL = "https://api.upcitemdb.com/prod/trial/lookup"
    
    # Built-in Indian product database (common products)
    INDIAN_PRODUCTS = {
        # Tata Products
        "8901052020294": {"name": "Tata Tea Chakra Gold 500g", "brand": "Tata", "category": "beverages", "expiry_days": 365},
        "8901052021000": {"name": "Tata Tea Premium 250g", "brand": "Tata", "category": "beverages", "expiry_days": 365},
        "8901030715204": {"name": "Tata Salt 1kg", "brand": "Tata", "category": "condiments", "expiry_days": 730},
        # Amul Products
        "8901262011068": {"name": "Amul Butter 500g", "brand": "Amul", "category": "dairy", "expiry_days": 180},
        "8901262150064": {"name": "Amul Fresh Milk 500ml", "brand": "Amul", "category": "dairy", "expiry_days": 7},
        "8901262011112": {"name": "Amul Gold Milk 1L", "brand": "Amul", "category": "dairy", "expiry_days": 7},
        "8901262011259": {"name": "Amul Cheese Slices", "brand": "Amul", "category": "dairy", "expiry_days": 90},
        # Britannia Products
        "8901063011014": {"name": "Britannia Good Day 75g", "brand": "Britannia", "category": "snacks", "expiry_days": 180},
        "8901063109780": {"name": "Britannia Bread 400g", "brand": "Britannia", "category": "bread", "expiry_days": 3},
        "8901063157078": {"name": "Britannia Cheese 200g", "brand": "Britannia", "category": "dairy", "expiry_days": 90},
        # Parle Products
        "8901207100017": {"name": "Parle-G 80g", "brand": "Parle", "category": "snacks", "expiry_days": 270},
        "8901207018756": {"name": "Parle Monaco 75g", "brand": "Parle", "category": "snacks", "expiry_days": 180},
        "8901207000508": {"name": "Parle Hide & Seek 100g", "brand": "Parle", "category": "snacks", "expiry_days": 180},
        # Nestle Products
        "8901058002393": {"name": "Maggi 2-Minute Noodles", "brand": "Nestle", "category": "grains", "expiry_days": 270},
        "8901058840216": {"name": "Nestle Everyday Dairy Whitener", "brand": "Nestle", "category": "dairy", "expiry_days": 180},
        "8901058002478": {"name": "Maggi Masala Noodles 70g", "brand": "Nestle", "category": "grains", "expiry_days": 270},
        # MDH / Everest Spices
        "8901049015017": {"name": "MDH Chana Masala 100g", "brand": "MDH", "category": "condiments", "expiry_days": 365},
        "8901049017011": {"name": "MDH Garam Masala 100g", "brand": "MDH", "category": "condiments", "expiry_days": 365},
        # Haldiram's
        "8904004408130": {"name": "Haldirams Bhujia 400g", "brand": "Haldirams", "category": "snacks", "expiry_days": 180},
        "8904004402671": {"name": "Haldirams Aloo Bhujia 200g", "brand": "Haldirams", "category": "snacks", "expiry_days": 180},
        # Fortune / Saffola
        "8901058836912": {"name": "Fortune Sunflower Oil 1L", "brand": "Fortune", "category": "condiments", "expiry_days": 365},
        "8904033500095": {"name": "Saffola Gold Oil 1L", "brand": "Saffola", "category": "condiments", "expiry_days": 365},
        # ITC Products
        "8901725181109": {"name": "Aashirvaad Atta 5kg", "brand": "ITC", "category": "grains", "expiry_days": 180},
        "8901725181000": {"name": "Aashirvaad Multigrain Atta 5kg", "brand": "ITC", "category": "grains", "expiry_days": 180},
        "8901725100001": {"name": "Sunfeast Dark Fantasy", "brand": "ITC", "category": "snacks", "expiry_days": 180},
        # MTR
        "8901042507019": {"name": "MTR Rava Idli Mix 500g", "brand": "MTR", "category": "grains", "expiry_days": 365},
        "8901042507026": {"name": "MTR Dosa Mix 500g", "brand": "MTR", "category": "grains", "expiry_days": 365},
        # Dabur
        "8901207043116": {"name": "Real Fruit Power Mango 1L", "brand": "Dabur", "category": "beverages", "expiry_days": 180},
        "8901207043130": {"name": "Real Mixed Fruit Juice 1L", "brand": "Dabur", "category": "beverages", "expiry_days": 180},
        # Mother Dairy
        "8906002810015": {"name": "Mother Dairy Milk 500ml", "brand": "Mother Dairy", "category": "dairy", "expiry_days": 3},
        "8906002810091": {"name": "Mother Dairy Curd 400g", "brand": "Mother Dairy", "category": "dairy", "expiry_days": 7},
        # Paper Boat
        "8906067340011": {"name": "Paper Boat Aam Panna 250ml", "brand": "Paper Boat", "category": "beverages", "expiry_days": 180},
        # Lijjat/Bikaji
        "8901042560021": {"name": "Lijjat Papad", "brand": "Lijjat", "category": "snacks", "expiry_days": 180},
        
        # DMart Private Label Products
        "8904215700012": {"name": "DMart Toor Dal 1kg", "brand": "DMart", "category": "grains", "expiry_days": 365},
        "8904215700029": {"name": "DMart Rice 5kg", "brand": "DMart", "category": "grains", "expiry_days": 365},
        "8904215700036": {"name": "DMart Sugar 1kg", "brand": "DMart", "category": "condiments", "expiry_days": 730},
        "8904215700043": {"name": "DMart Refined Oil 1L", "brand": "DMart", "category": "condiments", "expiry_days": 365},
        "8904215700050": {"name": "DMart Wheat Flour 5kg", "brand": "DMart", "category": "grains", "expiry_days": 180},
        "8904215700067": {"name": "DMart Moong Dal 1kg", "brand": "DMart", "category": "grains", "expiry_days": 365},
        "8904215700074": {"name": "DMart Chana Dal 1kg", "brand": "DMart", "category": "grains", "expiry_days": 365},
        "8904215700081": {"name": "DMart Urad Dal 1kg", "brand": "DMart", "category": "grains", "expiry_days": 365},
        "8904215700098": {"name": "DMart Masoor Dal 1kg", "brand": "DMart", "category": "grains", "expiry_days": 365},
        "8904215700104": {"name": "DMart Poha 500g", "brand": "DMart", "category": "grains", "expiry_days": 180},
        "8904215700111": {"name": "DMart Besan 500g", "brand": "DMart", "category": "grains", "expiry_days": 180},
        "8904215700128": {"name": "DMart Suji 500g", "brand": "DMart", "category": "grains", "expiry_days": 180},
        
        # BigBasket BB Royal Products
        "8906110730012": {"name": "BB Royal Basmati Rice 5kg", "brand": "BigBasket", "category": "grains", "expiry_days": 365},
        "8906110730029": {"name": "BB Royal Toor Dal 1kg", "brand": "BigBasket", "category": "grains", "expiry_days": 365},
        "8906110730036": {"name": "BB Royal Sugar 1kg", "brand": "BigBasket", "category": "condiments", "expiry_days": 730},
        
        # Patanjali Products
        "8906006280016": {"name": "Patanjali Cow Ghee 500ml", "brand": "Patanjali", "category": "dairy", "expiry_days": 270},
        "8906006280023": {"name": "Patanjali Desi Ghee 1kg", "brand": "Patanjali", "category": "dairy", "expiry_days": 270},
        "8906006280030": {"name": "Patanjali Atta 5kg", "brand": "Patanjali", "category": "grains", "expiry_days": 180},
        "8906006280047": {"name": "Patanjali Mustard Oil 1L", "brand": "Patanjali", "category": "condiments", "expiry_days": 365},
        "8906006280054": {"name": "Patanjali Honey 500g", "brand": "Patanjali", "category": "condiments", "expiry_days": 730},
        "8906006280061": {"name": "Patanjali Cow Milk 500ml", "brand": "Patanjali", "category": "dairy", "expiry_days": 3},
        "8906006280078": {"name": "Patanjali Dahi 400g", "brand": "Patanjali", "category": "dairy", "expiry_days": 7},
        
        # Catch Spices
        "8901595100016": {"name": "Catch Red Chilli Powder 100g", "brand": "Catch", "category": "condiments", "expiry_days": 365},
        "8901595100023": {"name": "Catch Turmeric Powder 100g", "brand": "Catch", "category": "condiments", "expiry_days": 365},
        "8901595100030": {"name": "Catch Coriander Powder 100g", "brand": "Catch", "category": "condiments", "expiry_days": 365},
        
        # Everest Spices
        "8901063100015": {"name": "Everest Kitchen King 100g", "brand": "Everest", "category": "condiments", "expiry_days": 365},
        "8901063100022": {"name": "Everest Meat Masala 100g", "brand": "Everest", "category": "condiments", "expiry_days": 365},
        "8901063100039": {"name": "Everest Pav Bhaji Masala 100g", "brand": "Everest", "category": "condiments", "expiry_days": 365},
        
        # Bingo / Lays Chips
        "8901491101516": {"name": "Lays Classic Salted 52g", "brand": "Lays", "category": "snacks", "expiry_days": 90},
        "8901491100519": {"name": "Lays Magic Masala 52g", "brand": "Lays", "category": "snacks", "expiry_days": 90},
        "8901725121471": {"name": "Bingo Mad Angles 66g", "brand": "ITC", "category": "snacks", "expiry_days": 90},
        "8901725121501": {"name": "Bingo Tedhe Medhe 66g", "brand": "ITC", "category": "snacks", "expiry_days": 90},
        
        # Kurkure
        "8901491503648": {"name": "Kurkure Masala Munch 75g", "brand": "PepsiCo", "category": "snacks", "expiry_days": 90},
        "8901491503655": {"name": "Kurkure Green Chutney 75g", "brand": "PepsiCo", "category": "snacks", "expiry_days": 90},
        
        # Pepsi / Coca Cola
        "8901388101516": {"name": "Pepsi 750ml", "brand": "PepsiCo", "category": "beverages", "expiry_days": 180},
        "8901388000012": {"name": "Coca Cola 750ml", "brand": "Coca Cola", "category": "beverages", "expiry_days": 180},
        "8901388101619": {"name": "Sprite 750ml", "brand": "Coca Cola", "category": "beverages", "expiry_days": 180},
        "8901388101626": {"name": "Fanta Orange 750ml", "brand": "Coca Cola", "category": "beverages", "expiry_days": 180},
        "8901388101633": {"name": "Thums Up 750ml", "brand": "Coca Cola", "category": "beverages", "expiry_days": 180},
        "8901388101640": {"name": "Limca 750ml", "brand": "Coca Cola", "category": "beverages", "expiry_days": 180},
        
        # Tropicana / Minute Maid
        "8901388001019": {"name": "Tropicana Orange Juice 1L", "brand": "PepsiCo", "category": "beverages", "expiry_days": 60},
        "8901388001026": {"name": "Tropicana Apple Juice 1L", "brand": "PepsiCo", "category": "beverages", "expiry_days": 60},
    }
    
    def __init__(self):
        # Local cache for common products
        self._product_cache = {}
    
    async def lookup(self, barcode: str) -> dict:
        """
        Look up product by barcode/UPC.
        
        Args:
            barcode: UPC/EAN barcode string
        
        Returns:
            Product info with suggested category and shelf life
        """
        # Clean barcode
        barcode = barcode.strip().replace("-", "").replace(" ", "")
        
        # Check cache first
        if barcode in self._product_cache:
            return self._product_cache[barcode]
        
        # Check built-in Indian product database first (fast lookup)
        result = self._lookup_indian_database(barcode)
        
        # If not found in local DB, try Open Food Facts
        if not result["found"]:
            result = await self._lookup_open_food_facts(barcode)
        
        # If still not found, try UPCitemdb as fallback
        if not result["found"]:
            result = await self._lookup_upcitemdb(barcode)
        
        if result["found"]:
            self._product_cache[barcode] = result
        else:
            # Add helpful message for manual entry
            result["message"] = "Product not found. You can add it manually with this barcode."
            result["allow_manual_entry"] = True
        
        return result
    
    def _lookup_indian_database(self, barcode: str) -> dict:
        """Check built-in Indian product database."""
        if barcode in self.INDIAN_PRODUCTS:
            product = self.INDIAN_PRODUCTS[barcode]
            return {
                "found": True,
                "source": "Local Database",
                "upc": barcode,
                "name": product["name"],
                "category": product["category"],
                "suggested_expiry_days": product["expiry_days"],
                "brand": product["brand"],
                "image_url": None,
            }
        return self._not_found_response(barcode)
    
    async def _lookup_open_food_facts(self, barcode: str) -> dict:
        """Query Open Food Facts API."""
        url = f"{self.OPEN_FOOD_FACTS_URL}/{barcode}.json"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers={"User-Agent": "FreshKeep/1.0"})
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != 1:
                    return self._not_found_response(barcode)
                
                product = data.get("product", {})
                
                # Extract product info
                name = product.get("product_name") or product.get("product_name_en", "Unknown")
                brand = product.get("brands", "")
                
                # Skip if no name found
                if not name or name == "Unknown":
                    return self._not_found_response(barcode)
                
                # Determine category from tags
                categories_tags = product.get("categories_tags", [])
                category = self._map_category(categories_tags)
                
                shelf_life = SHELF_LIFE_DEFAULTS.get(category, 14)
                
                return {
                    "found": True,
                    "source": "Open Food Facts",
                    "upc": barcode,
                    "name": name,
                    "category": category,
                    "suggested_expiry_days": shelf_life,
                    "brand": brand,
                    "image_url": product.get("image_url"),
                    "nutrition_grade": product.get("nutrition_grades"),
                }
                
        except httpx.HTTPError:
            return self._not_found_response(barcode)
    
    async def _lookup_upcitemdb(self, barcode: str) -> dict:
        """Query UPCitemdb API as fallback."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.UPCITEMDB_URL,
                    params={"upc": barcode},
                    headers={"User-Agent": "FreshKeep/1.0"}
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("code") != "OK" or not data.get("items"):
                    return self._not_found_response(barcode)
                
                item = data["items"][0]
                name = item.get("title", "Unknown")
                brand = item.get("brand", "")
                
                if not name or name == "Unknown":
                    return self._not_found_response(barcode)
                
                # Guess category from name
                category = self._guess_category_from_name(name)
                shelf_life = SHELF_LIFE_DEFAULTS.get(category, 14)
                
                return {
                    "found": True,
                    "source": "UPCitemdb",
                    "upc": barcode,
                    "name": name,
                    "category": category,
                    "suggested_expiry_days": shelf_life,
                    "brand": brand,
                    "image_url": item.get("images", [None])[0] if item.get("images") else None,
                }
                
        except httpx.HTTPError:
            return self._not_found_response(barcode)
    
    def _not_found_response(self, barcode: str) -> dict:
        """Return a not found response."""
        return {
            "found": False,
            "upc": barcode,
            "name": None,
            "category": None,
            "suggested_expiry_days": None,
            "brand": None,
        }
    
    def _guess_category_from_name(self, name: str) -> str:
        """Guess category from product name."""
        name_lower = name.lower()
        
        category_keywords = {
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "dairy"],
            "meat": ["beef", "pork", "lamb", "steak", "bacon", "ham", "sausage"],
            "poultry": ["chicken", "turkey", "duck", "wings"],
            "fish": ["fish", "salmon", "tuna", "shrimp", "seafood"],
            "vegetables": ["vegetable", "salad", "lettuce", "tomato", "potato", "carrot"],
            "fruits": ["fruit", "apple", "banana", "orange", "berry", "mango"],
            "bread": ["bread", "bagel", "muffin", "bakery"],
            "eggs": ["egg"],
            "frozen": ["frozen", "ice cream"],
            "canned": ["canned", "soup", "beans"],
            "condiments": ["sauce", "ketchup", "mustard", "mayo", "dressing"],
            "beverages": ["juice", "soda", "water", "drink", "tea", "coffee"],
            "snacks": ["chips", "cookie", "cracker", "candy", "chocolate", "snack"],
            "grains": ["rice", "pasta", "cereal", "flour", "noodle"],
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in name_lower for kw in keywords):
                return category
        
        return "other"
    
    def _map_category(self, category_tags: list) -> str:
        """Map Open Food Facts categories to our categories."""
        tags_str = " ".join(category_tags).lower()
        
        category_mapping = {
            "dairy": ["dairy", "milk", "cheese", "yogurt", "butter", "cream"],
            "meat": ["meat", "beef", "pork", "lamb", "bacon", "ham"],
            "poultry": ["poultry", "chicken", "turkey"],
            "fish": ["fish", "seafood", "salmon", "tuna", "shrimp"],
            "vegetables": ["vegetable", "salad", "lettuce", "tomato", "potato"],
            "fruits": ["fruit", "apple", "banana", "orange", "berry"],
            "bread": ["bread", "bakery", "pastry", "baked"],
            "eggs": ["egg"],
            "frozen": ["frozen", "ice-cream", "gelato"],
            "canned": ["canned", "preserved", "jarred"],
            "condiments": ["sauce", "condiment", "dressing", "oil", "vinegar"],
            "beverages": ["beverage", "drink", "juice", "soda", "water", "tea", "coffee"],
            "snacks": ["snack", "chip", "cookie", "candy", "chocolate", "biscuit"],
            "grains": ["grain", "cereal", "rice", "pasta", "flour", "bread"],
        }
        
        for category, keywords in category_mapping.items():
            if any(kw in tags_str for kw in keywords):
                return category
        
        return "other"
    
    async def add_to_cache(self, barcode: str, product_info: dict) -> None:
        """Add product to local cache (for manual additions)."""
        self._product_cache[barcode] = {
            "found": True,
            "upc": barcode,
            **product_info
        }
