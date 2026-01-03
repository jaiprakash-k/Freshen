"""
Authentication Service
User registration, login, and token management.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid

from app.database import get_supabase_client, Tables
from app.config import get_settings
from app.middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.middleware.error_handler import (
    BadRequestError,
    UnauthorizedError,
    NotFoundError,
)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.settings = get_settings()
    
    async def register(
        self,
        email: str,
        password: str,
        name: str,
        timezone: str = "UTC"
    ) -> dict:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: Plain text password
            name: User's display name
            timezone: User's timezone
        
        Returns:
            Created user data with tokens
        
        Raises:
            BadRequestError: If email already exists
        """
        # Check if email already exists
        existing = self.supabase.table(Tables.USERS).select("id").eq(
            "email", email.lower()
        ).execute()
        
        if existing.data:
            raise BadRequestError("Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_pw = hash_password(password)
        
        user_data = {
            "id": user_id,
            "email": email.lower(),
            "password_hash": hashed_pw,
            "name": name,
            "timezone": timezone,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        result = self.supabase.table(Tables.USERS).insert(user_data).execute()
        
        if not result.data:
            raise BadRequestError("Failed to create user")
        
        user = result.data[0]
        
        # Create default settings
        await self._create_default_settings(user_id)
        
        # Generate tokens
        tokens = self._generate_tokens(user_id)
        
        return {
            "user": self._format_user(user),
            **tokens
        }
    
    async def login(self, email: str, password: str) -> dict:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User's email
            password: Plain text password
        
        Returns:
            User data with tokens
        
        Raises:
            UnauthorizedError: If credentials are invalid
        """
        # Get user by email
        result = self.supabase.table(Tables.USERS).select("*").eq(
            "email", email.lower()
        ).execute()
        
        if not result.data:
            raise UnauthorizedError("Invalid email or password")
        
        user = result.data[0]
        
        # Verify password
        if not verify_password(password, user.get("password_hash", "")):
            raise UnauthorizedError("Invalid email or password")
        
        # Update last login
        self.supabase.table(Tables.USERS).update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        # Generate tokens
        tokens = self._generate_tokens(user["id"])
        
        return {
            "user": self._format_user(user),
            **tokens
        }
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access and refresh tokens
        
        Raises:
            UnauthorizedError: If refresh token is invalid
        """
        try:
            payload = decode_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid token type")
            
            user_id = payload.get("sub")
            
            # Verify user still exists
            result = self.supabase.table(Tables.USERS).select("id").eq(
                "id", user_id
            ).execute()
            
            if not result.data:
                raise UnauthorizedError("User not found")
            
            # Generate new tokens
            return self._generate_tokens(user_id)
            
        except Exception as e:
            raise UnauthorizedError("Invalid refresh token")
    
    async def get_profile(self, user_id: str) -> dict:
        """Get user profile by ID."""
        result = self.supabase.table(Tables.USERS).select("*").eq(
            "id", user_id
        ).execute()
        
        if not result.data:
            raise NotFoundError("User")
        
        return self._format_user(result.data[0])
    
    async def update_profile(
        self,
        user_id: str,
        name: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> dict:
        """Update user profile."""
        updates = {"updated_at": datetime.utcnow().isoformat()}
        
        if name:
            updates["name"] = name
        if timezone:
            updates["timezone"] = timezone
        
        result = self.supabase.table(Tables.USERS).update(updates).eq(
            "id", user_id
        ).execute()
        
        if not result.data:
            raise NotFoundError("User")
        
        return self._format_user(result.data[0])
    
    async def request_password_reset(self, email: str) -> bool:
        """
        Request password reset (sends email with token).
        Returns True even if email doesn't exist (security).
        """
        result = self.supabase.table(Tables.USERS).select("id, name").eq(
            "email", email.lower()
        ).execute()
        
        if result.data:
            # Generate reset token
            user = result.data[0]
            reset_token = str(uuid.uuid4())
            expires = datetime.utcnow() + timedelta(hours=1)
            
            # Store reset token (in production, send email)
            self.supabase.table(Tables.USERS).update({
                "reset_token": reset_token,
                "reset_token_expires": expires.isoformat()
            }).eq("id", user["id"]).execute()
            
            # TODO: Send email with reset link
            print(f"Password reset token for {email}: {reset_token}")
        
        return True
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using reset token."""
        result = self.supabase.table(Tables.USERS).select("id, reset_token_expires").eq(
            "reset_token", token
        ).execute()
        
        if not result.data:
            raise BadRequestError("Invalid or expired reset token")
        
        user = result.data[0]
        expires = datetime.fromisoformat(user["reset_token_expires"])
        
        if datetime.utcnow() > expires:
            raise BadRequestError("Reset token has expired")
        
        # Update password and clear token
        hashed_pw = hash_password(new_password)
        self.supabase.table(Tables.USERS).update({
            "password_hash": hashed_pw,
            "reset_token": None,
            "reset_token_expires": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        return True
    
    async def _create_default_settings(self, user_id: str) -> None:
        """Create default settings for new user."""
        default_settings = {
            "user_id": user_id,
            "notifications": {
                "enabled": True,
                "morning_alert_time": "07:00",
                "evening_reminder": True,
                "evening_reminder_time": "19:00",
                "voice_alerts": False,
                "expiry_threshold_days": 3,
            },
            "food": {
                "dietary_restrictions": [],
                "allergies": [],
                "disliked_ingredients": [],
                "preferred_cuisines": [],
                "default_unit_system": "metric",
            },
            "expiration": {
                "mode": "standard",
                "custom_shelf_life": {},
                "auto_extend_freezer": True,
            }
        }
        
        try:
            self.supabase.table(Tables.USER_SETTINGS).insert(default_settings).execute()
        except Exception:
            pass  # Settings table might not exist yet
    
    def _generate_tokens(self, user_id: str) -> dict:
        """Generate access and refresh tokens."""
        access_token = create_access_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.settings.access_token_expire_minutes * 60,
        }
    
    def _format_user(self, user: dict) -> dict:
        """Format user data for response (exclude sensitive fields)."""
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "timezone": user.get("timezone", "UTC"),
            "family_id": user.get("family_id"),
            "created_at": user["created_at"],
        }
