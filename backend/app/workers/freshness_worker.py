"""
Freshness Worker
Daily job to update item freshness status.
"""

from datetime import datetime, date
from app.database import get_supabase_client, Tables


async def update_all_freshness_status():
    """
    Update freshness status for all active items.
    Runs daily at 12:01 AM.
    """
    print(f"🔄 Starting freshness update at {datetime.now()}")
    
    supabase = get_supabase_client()
    today = date.today()
    
    try:
        # Get all active items
        result = supabase.table(Tables.ITEMS).select(
            "id, expiration_date"
        ).eq("status", "active").execute()
        
        items = result.data or []
        updated = 0
        expired = 0
        
        for item in items:
            exp_date_str = item.get("expiration_date")
            if not exp_date_str:
                continue
            
            # Parse expiration date
            if isinstance(exp_date_str, str):
                exp_date = datetime.fromisoformat(exp_date_str.replace("Z", "")).date()
            else:
                exp_date = exp_date_str
            
            # Check if expired
            if exp_date < today:
                # Mark as expired
                supabase.table(Tables.ITEMS).update({
                    "status": "expired",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", item["id"]).execute()
                expired += 1
            
            updated += 1
        
        print(f"✅ Freshness update complete: {updated} items checked, {expired} marked expired")
        
    except Exception as e:
        print(f"❌ Freshness update failed: {e}")
