import json
import os
from pathlib import Path
from datetime import datetime, timezone
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY

def get_project_root():
    # worker/src/db.py -> worker/src -> worker -> PROJECT_ROOT
    return Path(__file__).parent.parent.parent

def get_db_path():
    root = get_project_root()
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "cities.json"

def load_db():
    db_path = get_db_path()
    if not db_path.exists():
        return []
    
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️  Error decoding {db_path}. Returning empty list.")
        return []

def save_db(data):
    db_path = get_db_path()
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Database saved to {db_path}")

def update_city_entry(city_name, country_name, admin_info):
    """
    Updates or adds a city entry in the database.
    """
    db = load_db()
    
    # Find existing entry
    entry_index = -1
    for i, entry in enumerate(db):
        if entry.get("name") == city_name and entry.get("country") == country_name:
            entry_index = i
            break
    
    # Create a cleaner admin_info for the DB (less verbose)
    # We only need 'structured' for the frontend to reconstruct paths
    clean_admin_info = {}
    if "structured" in admin_info:
        clean_admin_info["structured"] = admin_info["structured"]
    else:
        # Fallback if structured is missing (should not happen with new logic)
        clean_admin_info = admin_info.copy()
        if "parts" in clean_admin_info:
            del clean_admin_info["parts"]
        # display_name might be useful for UI, but user asked to be less verbose.
        # Let's keep display_name as it's hard to reconstruct perfectly from structured data (formatting varies)
        # But user said "encore moins verbeux".
        # If we have structured, we can arguably rebuild a display string.
        # Let's remove display_name too if structured exists.
        if "display_name" in clean_admin_info and "structured" in admin_info:
             del clean_admin_info["display_name"]

    new_entry = {
        "name": city_name,
        "country": country_name,
        "admin_info": clean_admin_info,
        "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "published"
    }
    
    if entry_index >= 0:
        print(f"🔄 Updating existing entry for {city_name}")
        # Merge? Or Overwrite?
        # Overwrite maps, but maybe keep other fields?
        # For now, overwrite is safer to ensure consistency with latest generation.
        db[entry_index] = new_entry
    else:
        print(f"➕ Adding new entry for {city_name}")
        db.append(new_entry)
        
    save_db(db)
    return True

# -------------------------------------------------------------------------
# Supabase Interaction
# -------------------------------------------------------------------------

def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase credentials missing (SUPABASE_URL or SUPABASE_KEY).")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def poll_pending_requests(limit: int = 5):
    """Fetches pending requests up to the limit."""
    supabase = init_supabase()
    if not supabase:
        return []
    
    try:
        response = supabase.table('requests')\
            .select("*")\
            .eq('status', 'pending')\
            .order('created_at', desc=False)\
            .limit(limit)\
            .execute()
        
        if response.data:
            return response.data
        return []
    except Exception as e:
        print(f"❌ Error polling Supabase: {e}")
        return []

def reset_stale_requests(minutes: int = 30):
    """Resets requests stuck in 'processing' for too long back to 'pending'."""
    supabase = init_supabase()
    if not supabase:
        return

    # Calculate threshold time
    # Note: Supabase/Postgres uses ISO strings. 
    # Ideally we'd do this filter on the server side, but supabase-py filter syntax for dates can be tricky.
    # Simple approach: fetch all processing, check dates in python.
    
    try:
        response = supabase.table('requests').select("*").eq('status', 'processing').execute()
        if not response.data:
            return
            
        now = datetime.now(timezone.utc)
        count = 0
        
        for req in response.data:
            updated_at_str = req.get('updated_at') or req.get('created_at')
            if not updated_at_str:
                continue
                
            # Parse ISO string (e.g. 2023-10-27T10:00:00.123456+00:00)
            try:
                updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
            except ValueError:
                continue
                
            age_minutes = (now - updated_at).total_seconds() / 60
            
            if age_minutes > minutes:
                print(f"♻️  Resetting stale request {req.get('city')} ({req.get('id')}) - stuck for {int(age_minutes)}m")
                update_request_status(req.get('id'), 'pending')
                count += 1
                
        if count > 0:
            print(f"✅ Reset {count} stale requests to pending.")
            
    except Exception as e:
        print(f"❌ Error resetting stale requests: {e}")

def update_request_status(request_id: str, status: str, metadata: dict = None):
    """Updates the status of a request."""
    supabase = init_supabase()
    if not supabase:
        return False
        
    try:
        data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if metadata:
            data["metadata"] = metadata
            
        supabase.table('requests').update(data).eq('id', request_id).execute()
        print(f"✅ Request {request_id} updated to {status}")
        return True
    except Exception as e:
        print(f"❌ Error updating request {request_id}: {e}")
        return False

