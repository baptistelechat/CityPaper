import json
import os
from pathlib import Path
from datetime import datetime, timezone

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

def update_city_entry(city_name, country_name, uploaded_urls, admin_info):
    """
    Updates or adds a city entry in the database.
    """
    db = load_db()
    
    # Structure the maps data
    # uploaded_urls is { relative_path: url }
    # relative_path e.g. "Paris/A4_Print/Paris-a4_print-noir.png"
    # We want to organize by Format -> Theme -> URL
    
    maps_structure = {}
    
    for path_str, url in uploaded_urls.items():
        # path_str is like "A4_Print/Paris-a4_print-noir.png" or "Paris/A4_Print/..." depending on prefix
        # We need to parse it.
        # But wait, map_generator.py returns uploaded_urls with keys being relative paths to the uploaded directory.
        # If we uploaded "output/France/Paris", the keys are relative to that.
        
        # Let's try to extract format and theme from filename or path
        # Filename format: "{city}-{format}-{theme}.{ext}"
        # e.g. "Paris-a4_print-noir.png"
        
        path = Path(path_str)
        filename = path.name
        
        # Simple heuristic: split by '-'
        # But city name might contain '-'
        # Better to rely on parent directory if it is the format name (e.g. "A4_Print")
        
        format_name = path.parent.name # e.g. "A4_Print" or "4K_Wallpaper"
        
        # If the file is in the root of the upload (e.g. unstructured), path.parent.name might be "."
        # map_generator creates folders like "A4_Print", "4K_Wallpaper"
        
        if format_name in [".", ""]:
            # Maybe use filename parsing
            pass
        
        # Let's just store the flat map of filename -> url if structure is hard, 
        # but the story asks for "entry with Hugging Face URLs". 
        # A structured format is better for the frontend.
        
        if format_name not in maps_structure:
            maps_structure[format_name] = {}
            
        # Try to extract theme from filename
        # filename: City-Format-Theme.ext
        # We know the format.
        # Let's look at map_generator.py line 264: f"{safe_city_name}-{safe_fmt}-{safe_theme}{file_path.suffix}"
        
        # This parsing might be brittle if city name has dashes.
        # But we can try.
        
        maps_structure[format_name][filename] = url

    # Find existing entry
    entry_index = -1
    for i, entry in enumerate(db):
        if entry.get("name") == city_name and entry.get("country") == country_name:
            entry_index = i
            break
    
    new_entry = {
        "name": city_name,
        "country": country_name,
        "admin_info": admin_info,
        "maps": maps_structure,
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
