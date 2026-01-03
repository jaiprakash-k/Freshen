"""
Family Routes
Family sharing and management.
"""

from fastapi import APIRouter, Depends
from app.models.family import FamilyCreate, FamilyJoin, FamilyPermissionUpdate
from app.services.family_service import FamilyService
from app.middleware.auth import get_current_user
from app.utils.response import success_response

router = APIRouter()
family_service = FamilyService()


@router.post("")
async def create_family(data: FamilyCreate, current_user: dict = Depends(get_current_user)):
    """Create a new family group."""
    result = await family_service.create_family(user_id=current_user["id"], name=data.name)
    return success_response(data=result, message="Family created")


@router.post("/join")
async def join_family(data: FamilyJoin, current_user: dict = Depends(get_current_user)):
    """Join a family using invite code."""
    result = await family_service.join_family(user_id=current_user["id"], invite_code=data.invite_code)
    return success_response(data=result, message="Joined family")


@router.get("")
async def get_family(current_user: dict = Depends(get_current_user)):
    """Get current user's family."""
    family_id = current_user.get("family_id")
    if not family_id:
        return success_response(data=None, message="Not in a family")
    result = await family_service.get_family(family_id, current_user["id"])
    return success_response(data=result)


@router.get("/members")
async def get_members(current_user: dict = Depends(get_current_user)):
    """Get family members."""
    family_id = current_user.get("family_id")
    if not family_id:
        return success_response(data=[], message="Not in a family")
    members = await family_service.get_members(family_id)
    return success_response(data=members)


@router.put("/permissions")
async def update_permissions(data: FamilyPermissionUpdate, current_user: dict = Depends(get_current_user)):
    """Update a member's role (admin only)."""
    family_id = current_user.get("family_id")
    result = await family_service.update_member_role(
        family_id=family_id, admin_id=current_user["id"],
        target_user_id=data.user_id, new_role=data.role.value,
    )
    return success_response(data=result, message="Role updated")


@router.post("/leave")
async def leave_family(current_user: dict = Depends(get_current_user)):
    """Leave current family."""
    family_id = current_user.get("family_id")
    if family_id:
        await family_service.leave_family(family_id, current_user["id"])
    return success_response(message="Left family")


@router.post("/regenerate-code")
async def regenerate_code(current_user: dict = Depends(get_current_user)):
    """Regenerate family invite code (admin only)."""
    family_id = current_user.get("family_id")
    new_code = await family_service.regenerate_invite_code(family_id, current_user["id"])
    return success_response(data={"invite_code": new_code}, message="Invite code regenerated")
