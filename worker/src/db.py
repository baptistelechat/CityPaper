import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY

def get_project_root():
    # worker/src/db.py -> worker/src -> worker -> PROJECT_ROOT
    return Path(__file__).parent.parent.parent

def get_db_path():
    root = get_project_root()
    # Point to src/data so frontend can access the file
    data_dir = root / "src" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
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

def clean_name(n):
    if not n: return ""
    return "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in n]).strip()

def update_city_entry(city_name, country_name, admin_info, uploaded_urls=None, request_id=None):
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
    clean_admin_info = {}
    if "structured" in admin_info:
        clean_admin_info["structured"] = admin_info["structured"]
    else:
        # Fallback if structured is missing
        clean_admin_info = admin_info.copy()
        if "parts" in clean_admin_info:
            del clean_admin_info["parts"]
        if "display_name" in clean_admin_info and "structured" in admin_info:
             del clean_admin_info["display_name"]

    # Extract coordinates
    lat = admin_info.get("latitude")
    lon = admin_info.get("longitude")
    coordinates = f"{lat:.4f}, {lon:.4f}" if lat is not None and lon is not None else ""

    # Generate Slug (URL friendly) from structured data
    structured = clean_admin_info.get("structured", {})
    slug_parts = []
    
    # Preferred slug structure: Country-State-City or Country-City if state missing
    s_country = structured.get("country") or country_name
    s_state = structured.get("state")
    s_city = structured.get("city") or city_name
    
    if s_country: slug_parts.append(clean_name(s_country).lower().replace(" ", "-"))
    if s_state: slug_parts.append(clean_name(s_state).lower().replace(" ", "-"))
    if s_city: slug_parts.append(clean_name(s_city).lower().replace(" ", "-"))
    
    slug = "-".join([p for p in slug_parts if p])
    if not slug:
        # Fallback
        slug = f"{clean_name(country_name)}-{clean_name(city_name)}".lower().replace(" ", "-")

    # Determine ID
    # 1. Use request_id (UUID) if provided (Canonical Supabase ID)
    # 2. Use existing ID if entry exists
    # 3. Generate new UUID if new entry
    if request_id:
        entry_id = request_id
    elif entry_index >= 0:
        entry_id = db[entry_index].get("id")
    else:
        entry_id = str(uuid.uuid4())

    new_entry = {
        "id": entry_id,
        "slug": slug,
        "name": city_name,
        "country": country_name,
        "coordinates": coordinates,
        "admin_info": clean_admin_info,
        "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "published"
    }
    
    if entry_index >= 0:
        db[entry_index] = new_entry
        print(f"🔄 Updated entry for {city_name}, {country_name} (ID: {entry_id})")
    else:
        db.append(new_entry)
        print(f"➕ Added new entry for {city_name}, {country_name} (ID: {entry_id})")
    
    save_db(db)
