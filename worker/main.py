import argparse
import sys
import json
import time
import subprocess
from pathlib import Path
from src.setup_env import ensure_maptoposter_installed, ensure_venv
from src.map_generator import run_generation_for_city, clean_name
# Defer imports of src.db, src.notify, src.git_ops to avoid ModuleNotFoundError before venv setup

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

def format_detailed_commit_msg(city_name: str, country_name: str, admin_info: dict) -> str:
    """Formats a detailed commit message with all city information."""
    structured = admin_info.get('structured', {})
    
    subject = f"🌍 Request fulfilled: {city_name}, {country_name}"
    
    # Order: Country, Region, State, County, Postcode, City
    parts = [
        structured.get('country') or country_name,
        structured.get('region'),
        structured.get('state'),
        structured.get('county'),
        structured.get('postcode'),
        structured.get('city') or city_name
    ]
    line = ", ".join([p for p in parts if p])
    
    return f"{subject}\n\n- {line}"

def process_batch(json_path: Path, worker_dir: Path, python_exe: str, maptoposter_dir: Path, args):
    """
    Process a batch of cities from a JSON file.
    """
    # Import dependencies here
    from src.db import update_city_entry, get_db_path
    from src.git_ops import commit_and_push_changes

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
            parts = [city_name]
            if postcode: parts.append(postcode)
            if village and village != city_name: parts.append(village)
            if county: parts.append(county)
            if state: parts.append(state)
            
            search_city_param = ", ".join(parts)
            
            if search_city_param != city_name:
                print(f"🎯 Using precise search query: '{search_city_param}' for '{city_name}'")
            
            success, uploaded_urls, admin_info = run_generation_for_city(
                search_city_param, country_name, python_exe, maptoposter_dir, worker_dir, 
                args.theme, args.all_themes or True,
                display_city_override=city_name, # Keep the simple name for the map title
                display_country_override=args.display_country,
                postcode_override=postcode
            )
            
            if success and uploaded_urls:
                # Use the original simple name for the database entry
                update_city_entry(city_name, country_name, admin_info)
                
                # Build detailed location string for commit message
                commit_msg = format_detailed_commit_msg(city_name, country_name, admin_info)
                
                # Commit after each city
                db_path = get_db_path()
                commit_and_push_changes(db_path, commit_msg, push=args.push)
        
        print("✅ Batch processing complete.")
        
    except Exception as e:
        print(f"❌ Error processing JSON: {e}")
        sys.exit(1)

def run_worker_loop(python_exe: str, maptoposter_dir: Path, worker_dir: Path, args):
    """
    Runs the main worker polling loop.
    """
    # Import dependencies here
    from src.db import update_city_entry, get_db_path, poll_pending_requests, update_request_status, reset_stale_requests
    from src.git_ops import commit_and_push_changes

    print("🚀 Starting Worker Polling Loop...")
    print("   Press Ctrl+C to stop.")
    
    # Initial cleanup of stale requests
    reset_stale_requests(minutes=30)
    
    while True:
        try:
            # 1. Poll for pending requests (batch of 5)
            requests = poll_pending_requests(limit=5)
            
            if not requests:
                # Sleep and retry
                print("💤 No pending requests. Waiting...", end="\r", flush=True)
                time.sleep(10)
                continue
            
            print(f"\n🔔 Found {len(requests)} pending requests.                ")
            
            successful_generations = []
            
            for request in requests:
                req_id = request['id']
                city_name = request['city']
                country_name = request['country']
                postcode = request.get('postcode')
                
                # Construct search query with postcode if available
                search_city = city_name
                if postcode:
                    search_city = f"{city_name} {postcode}"
                
                print(f"👉 Processing request: {city_name} ({req_id}) [Search: {search_city}]")
                
                # 2. Update status to processing
                if not update_request_status(req_id, 'processing'):
                    print("❌ Failed to update status to processing. Skipping.")
                    continue
                
                # 3. Generate Map
                print(f"🎨 Generating map for {search_city}, {country_name}...")
                
                # Force all themes for user requests unless specified otherwise
                success, uploaded_urls, admin_info = run_generation_for_city(
                    search_city, country_name, python_exe, maptoposter_dir, worker_dir, 
                    theme=args.theme, all_themes=True,
                    display_city_override=city_name,
                    display_country_override=args.display_country,
                    postcode_override=postcode
                )
                
                if success and uploaded_urls:
                    # 4. Success handling
                    print("✅ Generation successful!")
                    
                    # Update local DB (Git)
                    update_city_entry(city_name, country_name, admin_info)
                    
                    # Calculate City Page URL
                    slug_city = clean_name(city_name).lower().replace(" ", "-").replace("_", "-")
                    slug_country = clean_name(country_name).lower().replace(" ", "-").replace("_", "-")
                    slug = f"{slug_city}-{slug_country}"
                    
                    base_url = "https://citypaper-v1.vercel.app" 
                    city_page_url = f"{base_url}/city/{slug}"
                    
                    # Update Supabase
                    metadata_update = {
                        "result_urls": uploaded_urls,
                        "city_page_url": city_page_url,
                        "admin_info": admin_info
                    }
                    update_request_status(req_id, 'completed', metadata=metadata_update)
                    
                    # Store success info for batch commit
                    successful_generations.append({
                        "city": city_name,
                        "country": country_name,
                        "admin_info": admin_info
                    })
                    
                else:
                    # 6. Failure handling
                    print("❌ Generation failed.")
                    update_request_status(req_id, 'failed', metadata={"error": "Generation failed"})

            # 7. Batch Commit
            if successful_generations:
                count = len(successful_generations)
                
                # Construct Aggregate Commit Message
                subject = f"🌍 Added {count} new cities"
                body_lines = []
                
                for item in successful_generations:
                    city = item['city']
                    country = item['country']
                    admin = item['admin_info']
                    structured = admin.get('structured', {})
                    
                    # Order: Country, Region, State, County, Postcode, City
                    parts = [
                        structured.get('country') or country,
                        structured.get('region'),
                        structured.get('state'),
                        structured.get('county'),
                        structured.get('postcode'),
                        structured.get('city') or city
                    ]
                    line = ", ".join([p for p in parts if p])
                    body_lines.append(f"- {line}")
                
                commit_msg = f"{subject}\n\n" + "\n".join(body_lines)
                
                print(f"💾 Committing batch changes ({count} cities)...")
                db_path = get_db_path()
                commit_and_push_changes(db_path, commit_msg, push=args.push)
                
        except KeyboardInterrupt:
            print("\n🛑 Worker stopping...")
            break
        except Exception as e:
            print(f"❌ Unexpected error in worker loop: {e}")
            time.sleep(5)

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
    parser.add_argument("--worker", "-w", action="store_true", help="Run in worker polling mode")
    
    args = parser.parse_args()

    # Determine paths
    worker_dir = Path(__file__).parent.absolute()

    # 0. Check Python version (Basic check)
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11+ is required.")
        sys.exit(1)

    maptoposter_dir = worker_dir / "maptoposter"
    script_path = maptoposter_dir / "create_map_poster.py"

    # 1. Install / Update maptoposter
    ensure_maptoposter_installed(maptoposter_dir)

    # 2. Ensure venv and dependencies
    python_exe = ensure_venv(worker_dir)
    
    # --- AUTO-RESTART IN VENV ---
    # Check if we are running with the venv python
    current_exe = Path(sys.executable).resolve()
    target_exe = Path(python_exe).resolve()
    
    # On Windows, target_exe might be 'python.exe' and current might be 'Python.exe'
    if current_exe != target_exe:
        # Avoid infinite loop if paths resolve differently but are same file (unlikely with venv)
        # But if we are already in venv, sys.executable should point to it.
        # However, if we run 'python worker/main.py', sys.executable is system python.
        
        print(f"🔄 Restarting in virtual environment: {target_exe}")
        try:
            # We must use the script path as the first argument
            script_file = Path(__file__).absolute()
            subprocess.run([str(target_exe), str(script_file), *sys.argv[1:]], check=True)
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            sys.exit(0)
    # ----------------------------

    if not script_path.exists():
        print(f"❌ Error: create_map_poster.py still not found at {script_path} after clone attempt.")
        sys.exit(1)
        
    # From here on, we are in the venv, so we can import modules that depend on requirements.txt
    from src.db import update_city_entry, get_db_path
    from src.git_ops import commit_and_push_changes

    # 3. Determine work mode
    if args.worker:
        run_worker_loop(python_exe, maptoposter_dir, worker_dir, args)
        
    elif args.source_json:
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
             print("❌ Error: --city and --country are required unless using --source-json or --worker")
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
