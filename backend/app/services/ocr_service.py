"""
OCR Service
Receipt image processing using OCR.space API.
"""

import re
import httpx
from typing import List, Optional
from datetime import date

from app.config import get_settings, SHELF_LIFE_DEFAULTS
from app.middleware.error_handler import ExternalAPIError, BadRequestError


class OCRService:
    """Service for OCR receipt processing."""
    
    OCR_SPACE_URL = "https://api.ocr.space/parse/image"
    
    def __init__(self):
        self.settings = get_settings()
    
    async def parse_receipt(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_file: Optional[bytes] = None
    ) -> dict:
        """
        Parse receipt image and extract items.
        
        Args:
            image_url: URL of receipt image
            image_base64: Base64 encoded image
            image_file: Raw image bytes
        
        Returns:
            Parsed items with suggested categories and expiry
        """
        if not self.settings.ocr_space_api_key:
            raise BadRequestError("OCR service not configured")
        
        # Call OCR.space API
        raw_text = await self._call_ocr_api(image_url, image_base64, image_file)
        
        if not raw_text:
            return {
                "items": [],
                "raw_text": "",
                "warnings": ["Could not extract text from image"]
            }
        
        # Parse items from text
        items = self._parse_receipt_text(raw_text)
        
        return {
            "items": items,
            "raw_text": raw_text,
            "warnings": [] if items else ["No items could be identified"]
        }
    
    async def _call_ocr_api(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_file: Optional[bytes] = None
    ) -> str:
        """Call OCR.space API and return extracted text."""
        headers = {
            "apikey": self.settings.ocr_space_api_key,
        }
        
        data = {
            "language": "eng",
            "isOverlayRequired": "false",
            "detectOrientation": "true",
            "scale": "true",
            "OCREngine": "2",  # Better for receipts
        }
        
        files = None
        
        if image_url:
            data["url"] = image_url
        elif image_base64:
            data["base64Image"] = f"data:image/jpeg;base64,{image_base64}"
        elif image_file:
            # Convert file bytes to base64 - more reliable than multipart upload
            import base64
            b64_image = base64.b64encode(image_file).decode('utf-8')
            data["base64Image"] = f"data:image/jpeg;base64,{b64_image}"
        else:
            raise BadRequestError("No image provided")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.OCR_SPACE_URL,
                    headers=headers,
                    data=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Log for debugging
                print(f"OCR Response: {result}")
                
                if result.get("IsErroredOnProcessing"):
                    error_msg = result.get("ErrorMessage", ["Unknown error"])
                    if isinstance(error_msg, list):
                        error_msg = error_msg[0] if error_msg else "Unknown error"
                    raise ExternalAPIError("OCR.space", error_msg)
                
                # Extract text from response
                parsed_results = result.get("ParsedResults", [])
                if parsed_results:
                    return parsed_results[0].get("ParsedText", "")
                
                return ""
                
        except httpx.HTTPError as e:
            raise ExternalAPIError("OCR.space", str(e))
    
    def _parse_receipt_text(self, text: str) -> List[dict]:
        """
        Parse receipt text to extract grocery items.
        
        This uses heuristics to identify product lines and extract
        item names, quantities, and prices.
        """
        items = []
        lines = text.strip().split("\n")
        
        # Common patterns for receipt items
        # Format: [Quantity] Item Name [Price]
        item_pattern = re.compile(
            r'^(?:(\d+)\s*[xX]?\s*)?'  # Optional quantity
            r'([A-Za-z][A-Za-z0-9\s\-\'\.]+?)'  # Item name
            r'(?:\s+[\$€£]?\d+[\.,]\d{2})?$'  # Optional price
        )
        
        # Words to skip (headers, footers, etc.)
        skip_words = {
            'total', 'subtotal', 'tax', 'cash', 'change', 'visa', 'mastercard',
            'thank', 'receipt', 'store', 'date', 'time', 'welcome', 'balance',
            'savings', 'discount', 'coupon', 'rewards', 'points', 'card'
        }
        
        for line in lines:
            line = line.strip()
            
            # Skip empty or very short lines
            if len(line) < 3:
                continue
            
            # Skip lines with skip words
            if any(word in line.lower() for word in skip_words):
                continue
            
            # Try to match item pattern
            match = item_pattern.match(line)
            if match:
                quantity_str = match.group(1)
                name = match.group(2).strip()
                
                # Clean up name
                name = re.sub(r'\s+', ' ', name)
                name = name.title()
                
                # Skip if name is too short or looks like a code
                if len(name) < 2 or name.isdigit():
                    continue
                
                quantity = float(quantity_str) if quantity_str else 1.0
                
                # Guess category
                category = self._guess_category(name)
                shelf_life = SHELF_LIFE_DEFAULTS.get(category, 14)
                
                items.append({
                    "name": name,
                    "quantity": quantity,
                    "unit": "piece",
                    "suggested_category": category,
                    "suggested_expiry_days": shelf_life,
                    "confidence": 0.7 if quantity_str else 0.5
                })
        
        return items
    
    def _guess_category(self, name: str) -> str:
        """Guess item category from name."""
        name_lower = name.lower()
        
        # Category keywords
        categories = {
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "yoghurt"],
            "meat": ["beef", "pork", "lamb", "steak", "ground", "bacon", "ham", "sausage"],
            "poultry": ["chicken", "turkey", "duck", "wings", "breast", "thigh"],
            "fish": ["fish", "salmon", "tuna", "shrimp", "cod", "tilapia", "seafood"],
            "vegetables": ["lettuce", "tomato", "onion", "pepper", "carrot", "broccoli", 
                          "spinach", "potato", "celery", "cucumber", "cabbage", "salad"],
            "fruits": ["apple", "banana", "orange", "grape", "berry", "strawberry",
                      "mango", "peach", "pear", "melon", "lemon", "lime"],
            "bread": ["bread", "bagel", "roll", "bun", "muffin", "croissant", "toast"],
            "eggs": ["egg", "eggs"],
            "frozen": ["frozen", "ice cream", "pizza"],
            "canned": ["can", "canned", "soup", "beans"],
            "condiments": ["sauce", "ketchup", "mustard", "mayo", "dressing", "oil", "vinegar"],
            "beverages": ["juice", "soda", "water", "drink", "tea", "coffee"],
            "snacks": ["chips", "cookie", "cracker", "popcorn", "candy", "chocolate"],
            "grains": ["rice", "pasta", "cereal", "oat", "flour", "noodle"],
        }
        
        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category
        
        return "other"
