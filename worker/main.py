import argparse
import sys
import json
from pathlib import Path
from src.setup_env import ensure_maptoposter_installed, ensure_venv
from src.map_generator import run_generation_for_city

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
            
            if not city_name or not country_name:
                print(f"⚠️  Skipping invalid item: {item}")
                continue
            
            run_generation_for_city(city_name, country_name, python_exe, maptoposter_dir, worker_dir, args.theme, args.all_themes or True)
        
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
             
        run_generation_for_city(args.city, args.country, python_exe, maptoposter_dir, worker_dir, args.theme, args.all_themes, args.display_city, args.display_country)

if __name__ == "__main__":
    main()
