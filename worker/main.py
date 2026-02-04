import argparse
import sys
import json
from pathlib import Path
from src.setup_env import ensure_maptoposter_installed, ensure_venv
from src.map_generator import run_generation_for_city, clean_name
from src.db import update_city_entry, get_db_path
from src.git_ops import commit_and_push_changes

def build_location_string(admin_info: dict, fallback_city: str, fallback_country: str) -> str:
    """Builds a structured location string for commit messages."""
    structured = admin_info.get('structured', {})
    if structured:
        parts = [
            structured.get('country') or fallback_country,
            structured.get('region'),
            structured.get('state'),
            structured.get('county'),
            structured.get('postcode'),
            structured.get('city') or fallback_city
        ]
        # Filter None/Empty and join with underscores, cleaned
        return "_".join([clean_name(p) for p in parts if p])
    else:
        return f"{clean_name(fallback_country)}_{clean_name(fallback_city)}"

def process_batch(json_path: Path, worker_dir: Path, python_exe: str, maptoposter_dir: Path, args):
    """
    Process a batch of cities from a JSON file.
    """
    print(f"📜 Reading cities from {json_path}...")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            cities_data = json.load(f)
        
        print(f"Found {len(cities_data)} cities to process.")
        
        for item in cities_data:
            city_name = item.get("name")
            country_name = item.get("country")
            
            # Extract extra fields for better precision (supporting OSM naming convention)
            postcode = item.get("postcode")
            state = item.get("state") or item.get("region") # state usually maps to Region
            county = item.get("county") or item.get("department") # county usually maps to Department
            village = item.get("village")
            
            if not city_name or not country_name:
                print(f"⚠️  Skipping invalid item: {item}")
                continue
            
            # Construct a precise search query
            # Order matters for Nominatim sometimes, but usually "Smallest, Largest" is good.
            # e.g. "Gordes, Vaucluse, Provence-Alpes-Côte d'Azur"
            # or "Nantes, 44000, Loire-Atlantique"
            
            parts = [city_name]
            if postcode: parts.append(postcode)
            if village and village != city_name: parts.append(village)
            if county: parts.append(county)
            if state: parts.append(state)
            
            # We don't append country here because run_generation_for_city takes it as a separate arg
            # and calculate_bounds appends it.
            
            search_city_param = ", ".join(parts)
            
            if search_city_param != city_name:
                print(f"🎯 Using precise search query: '{search_city_param}' for '{city_name}'")
            
            success, uploaded_urls, admin_info = run_generation_for_city(
                search_city_param, country_name, python_exe, maptoposter_dir, worker_dir, 
                args.theme, args.all_themes or True,
                display_city_override=city_name, # Keep the simple name for the map title
                display_country_override=args.display_country
            )
            
            if success and uploaded_urls:
                # Use the original simple name for the database entry
                update_city_entry(city_name, country_name, uploaded_urls, admin_info)
                
                # Build detailed location string for commit message
                location_str = build_location_string(admin_info, city_name, country_name)
                
                # Commit after each city
                db_path = get_db_path()
                commit_and_push_changes(db_path, f"🌍 Update data for {location_str}", push=args.push)
        
        print("✅ Batch processing complete.")
        
    except Exception as e:
        print(f"❌ Error processing JSON: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate city maps using maptoposter")
    parser.add_argument("--city", "-c", help="City name")
    parser.add_argument("--country", "-C", help="Country name")
    parser.add_argument("--theme", "-t", help="Specific theme (default: all themes if not specified)")
    parser.add_argument("--all-themes", action="store_true", help="Generate maps for all available themes")
    parser.add_argument("--display-city", "-dc", help="Explicit city name to display on the map (overrides auto-detection)")
    parser.add_argument("--display-country", "-dC", help='Custom display name for country (e.g., "日本")')
    parser.add_argument("--source-json", help="Path to cities.json for batch generation")
    parser.add_argument("--push", action="store_true", help="Push changes to git remote")
    
    args = parser.parse_args()

    # Determine paths
    worker_dir = Path(__file__).parent.absolute()

    # 0. Check Python version
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11+ is required.")
        sys.exit(1)

    maptoposter_dir = worker_dir / "maptoposter"
    script_path = maptoposter_dir / "create_map_poster.py"

    # 1. Install / Update maptoposter
    ensure_maptoposter_installed(maptoposter_dir)

    # 2. Ensure venv and dependencies
    python_exe = ensure_venv(worker_dir)

    if not script_path.exists():
        print(f"❌ Error: create_map_poster.py still not found at {script_path} after clone attempt.")
        sys.exit(1)

    # 3. Determine work mode
    if args.source_json:
        json_path = Path(args.source_json)
        if not json_path.exists():
            project_root = worker_dir.parent
            json_path_alt = project_root / args.source_json
            if json_path_alt.exists():
                json_path = json_path_alt
            else:
                print(f"❌ Error: JSON file not found at {json_path} or {json_path_alt}")
                sys.exit(1)
        
        process_batch(json_path, worker_dir, python_exe, maptoposter_dir, args)

    else:
        # Single city mode
        if not args.city or not args.country:
             print("❌ Error: --city and --country are required unless using --source-json")
             sys.exit(1)
             
        success, uploaded_urls, admin_info = run_generation_for_city(
            args.city, args.country, python_exe, maptoposter_dir, worker_dir, 
            args.theme, args.all_themes, args.display_city, args.display_country
        )
        
        if success and uploaded_urls:
             update_city_entry(args.city, args.country, uploaded_urls, admin_info)
             
             # Build detailed location string for commit message
             location_str = build_location_string(admin_info, args.city, args.country)
             
             db_path = get_db_path()
             commit_and_push_changes(db_path, f"🌍 Update data for {location_str}", push=args.push)

if __name__ == "__main__":
    main()
