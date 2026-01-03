"""
Family Service
Family group management and sharing.
"""

from datetime import datetime
from typing import List, Optional
import uuid
import random
import string

from app.database import get_supabase_client, Tables
from app.middleware.error_handler import NotFoundError, BadRequestError, ForbiddenError


class FamilyService:
    """Service for family sharing management."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def create_family(self, user_id: str, name: str) -> dict:
        """Create a new family group."""
        family_id = str(uuid.uuid4())
        invite_code = self._generate_invite_code()
        now = datetime.utcnow().isoformat()
        
        family_data = {
            "id": family_id, "name": name, "admin_id": user_id,
            "invite_code": invite_code, "created_at": now,
        }
        
        result = self.supabase.table(Tables.FAMILIES).insert(family_data).execute()
        
        # Add creator as admin member
        member_data = {
            "family_id": family_id, "user_id": user_id,
            "role": "admin", "joined_at": now,
        }
        self.supabase.table(Tables.FAMILY_MEMBERS).insert(member_data).execute()
        
        # Update user's family_id
        self.supabase.table(Tables.USERS).update({"family_id": family_id}).eq("id", user_id).execute()
        
        return {"id": family_id, "name": name, "invite_code": invite_code,
                "admin_id": user_id, "member_count": 1, "created_at": now}
    
    async def join_family(self, user_id: str, invite_code: str) -> dict:
        """Join a family using invite code."""
        result = self.supabase.table(Tables.FAMILIES).select("*").eq(
            "invite_code", invite_code.upper()).execute()
        
        if not result.data:
            raise BadRequestError("Invalid invite code")
        
        family = result.data[0]
        
        # Check if already a member
        existing = self.supabase.table(Tables.FAMILY_MEMBERS).select("id").eq(
            "family_id", family["id"]).eq("user_id", user_id).execute()
        
        if existing.data:
            raise BadRequestError("You are already a member of this family")
        
        now = datetime.utcnow().isoformat()
        member_data = {"family_id": family["id"], "user_id": user_id, "role": "editor", "joined_at": now}
        self.supabase.table(Tables.FAMILY_MEMBERS).insert(member_data).execute()
        self.supabase.table(Tables.USERS).update({"family_id": family["id"]}).eq("id", user_id).execute()
        
        return await self.get_family(family["id"], user_id)
    
    async def get_family(self, family_id: str, user_id: str) -> dict:
        """Get family details."""
        result = self.supabase.table(Tables.FAMILIES).select("*").eq("id", family_id).execute()
        if not result.data:
            raise NotFoundError("Family")
        
        family = result.data[0]
        members = await self.get_members(family_id)
        
        return {
            "id": family["id"], "name": family["name"], "invite_code": family["invite_code"],
            "admin_id": family["admin_id"], "member_count": len(members),
            "created_at": family["created_at"], "members": members,
        }
    
    async def get_members(self, family_id: str) -> List[dict]:
        """Get all family members."""
        result = self.supabase.table(Tables.FAMILY_MEMBERS).select(
            "*, users(id, name, email)").eq("family_id", family_id).execute()
        
        members = []
        for m in (result.data or []):
            user = m.get("users", {})
            members.append({
                "id": m.get("id"), "user_id": m["user_id"], "name": user.get("name", "Unknown"),
                "email": user.get("email", ""), "role": m["role"], "joined_at": m["joined_at"],
            })
        return members
    
    async def update_member_role(self, family_id: str, admin_id: str,
                                  target_user_id: str, new_role: str) -> dict:
        """Update a member's role (admin only)."""
        # Verify admin
        admin_check = self.supabase.table(Tables.FAMILY_MEMBERS).select("role").eq(
            "family_id", family_id).eq("user_id", admin_id).execute()
        
        if not admin_check.data or admin_check.data[0]["role"] != "admin":
            raise ForbiddenError("Only admins can change roles")
        
        self.supabase.table(Tables.FAMILY_MEMBERS).update({"role": new_role}).eq(
            "family_id", family_id).eq("user_id", target_user_id).execute()
        
        return {"user_id": target_user_id, "role": new_role}
    
    async def leave_family(self, family_id: str, user_id: str) -> bool:
        """Leave a family group."""
        self.supabase.table(Tables.FAMILY_MEMBERS).delete().eq(
            "family_id", family_id).eq("user_id", user_id).execute()
        self.supabase.table(Tables.USERS).update({"family_id": None}).eq("id", user_id).execute()
        return True
    
    async def regenerate_invite_code(self, family_id: str, admin_id: str) -> str:
        """Regenerate invite code (admin only)."""
        admin_check = self.supabase.table(Tables.FAMILY_MEMBERS).select("role").eq(
            "family_id", family_id).eq("user_id", admin_id).execute()
        
        if not admin_check.data or admin_check.data[0]["role"] != "admin":
            raise ForbiddenError("Only admins can regenerate invite code")
        
        new_code = self._generate_invite_code()
        self.supabase.table(Tables.FAMILIES).update({"invite_code": new_code}).eq("id", family_id).execute()
        return new_code
    
    def _generate_invite_code(self) -> str:
        """Generate a random 6-character invite code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
