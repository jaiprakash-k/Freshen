"""
Text-to-Speech Service
Voice alerts using ElevenLabs API.
"""

import httpx
import hashlib
from typing import Optional
from pathlib import Path

from app.config import get_settings


class TTSService:
    """Service for text-to-speech generation."""
    
    ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"
    
    def __init__(self):
        self.settings = get_settings()
        self._audio_cache = {}
        
        # Ensure audio cache directory exists
        self.cache_dir = Path("./audio_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (uses default if not provided)
        
        Returns:
            URL or path to audio file, or None if failed
        """
        if not self.settings.elevenlabs_api_key:
            return None
        
        # Check cache
        cache_key = self._get_cache_key(text, voice_id)
        if cache_key in self._audio_cache:
            return self._audio_cache[cache_key]
        
        voice = voice_id or self.settings.elevenlabs_voice_id
        url = f"{self.ELEVENLABS_URL}/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.settings.elevenlabs_api_key,
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                # Save audio file
                audio_path = self.cache_dir / f"{cache_key}.mp3"
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                
                # In production, upload to S3 and return URL
                file_path = str(audio_path)
                self._audio_cache[cache_key] = file_path
                
                return file_path
                
        except httpx.HTTPError as e:
            print(f"TTS generation failed: {e}")
            return None
    
    async def generate_cooking_instruction(
        self,
        instruction: str,
        step_number: int
    ) -> Optional[str]:
        """
        Generate voice for a cooking instruction step.
        
        Args:
            instruction: The cooking instruction text
            step_number: Step number in recipe
        
        Returns:
            Path to audio file
        """
        text = f"Step {step_number}: {instruction}"
        return await self.generate_speech(text)
    
    async def generate_expiry_alert(
        self,
        items: list
    ) -> Optional[str]:
        """
        Generate voice alert for expiring items.
        
        Args:
            items: List of item dicts with 'name' and 'days_until_expiry'
        
        Returns:
            Path to audio file
        """
        if not items:
            return None
        
        # Build natural language alert
        if len(items) == 1:
            item = items[0]
            days = item.get("days_until_expiry", 0)
            if days == 0:
                text = f"Attention! Your {item['name']} expires today. Consider using it soon."
            elif days == 1:
                text = f"Heads up! Your {item['name']} expires tomorrow."
            else:
                text = f"Your {item['name']} will expire in {days} days."
        else:
            expiring_today = [i for i in items if i.get("days_until_expiry", 0) == 0]
            expiring_soon = [i for i in items if 0 < i.get("days_until_expiry", 999) <= 3]
            
            parts = []
            if expiring_today:
                names = ", ".join(i["name"] for i in expiring_today[:3])
                parts.append(f"{names} expire today")
            if expiring_soon:
                names = ", ".join(i["name"] for i in expiring_soon[:3])
                parts.append(f"{names} expire soon")
            
            text = f"Food alert! {' and '.join(parts)}. Check your FreshKeep app for recipes."
        
        return await self.generate_speech(text)
    
    def _get_cache_key(self, text: str, voice_id: Optional[str]) -> str:
        """Generate cache key for audio."""
        content = f"{text}:{voice_id or 'default'}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
