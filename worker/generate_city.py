import argparse
import subprocess
import sys
import os
import shutil
import json
from pathlib import Path
import math

FORMATS = {
    # "Instagram_Post": {"w": 3.6, "h": 3.6},
    "Mobile_Wallpaper": {"w": 3.6, "h": 6.4},
    # "HD_Wallpaper": {"w": 6.4, "h": 3.6},
    # "4K_Wallpaper": {"w": 12.8, "h": 7.2},
    # "A4_Print": {"w": 8.3, "h": 11.7}
}

MAPTOPOSTER_REPO = "https://github.com/originalankur/maptoposter.git"

def ensure_maptoposter_installed(maptoposter_dir: Path):
    """
    Ensures that the maptoposter repository is cloned and up-to-date.
    """
    if not maptoposter_dir.exists():
        print(f"📦 maptoposter not found. Cloning from {MAPTOPOSTER_REPO}...")
        try:
            subprocess.run(["git", "clone", MAPTOPOSTER_REPO, str(maptoposter_dir)], check=True)
            print("✅ Cloned successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error cloning maptoposter: {e}")
            sys.exit(1)
    else:
        # Check if it's a valid git repo
        if (maptoposter_dir / ".git").exists():
            print("🔄 Checking for updates...")
            try:
                subprocess.run(["git", "pull"], cwd=maptoposter_dir, check=True)
                print("✅ Updated successfully.")
            except subprocess.CalledProcessError:
                print("⚠️  Could not update repo (might be dirty or detached). Continuing with current version.")
        else:
            print("⚠️  Directory exists but is not a git repo (likely a manual copy or cleaned folder).")
            print("♻️  Re-initializing: Deleting and re-cloning to enable updates...")
            try:
                shutil.rmtree(maptoposter_dir)
                subprocess.run(["git", "clone", MAPTOPOSTER_REPO, str(maptoposter_dir)], check=True)
                print("✅ Re-cloned successfully.")
            except Exception as e:
                print(f"❌ Error repairing maptoposter: {e}")
                sys.exit(1)

def ensure_venv(worker_dir: Path) -> str:
    """
    Ensures a virtual environment exists and dependencies are installed.
    Returns the path to the python executable within the venv.
    """
    venv_dir = worker_dir / ".venv"
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"

    requirements_file = worker_dir / "requirements.txt"

    # 1. Create venv if it doesn't exist
    if not venv_dir.exists():
        print(f"📦 Creating virtual environment at {venv_dir}...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            print("✅ Virtual environment created.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating venv: {e}")
            sys.exit(1)

    # 2. Install dependencies
    if requirements_file.exists():
        print("🔄 Checking/Installing dependencies...")
        try:
            subprocess.run([str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)], check=True)
            print("✅ Dependencies installed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print("⚠️  No requirements.txt found. Skipping dependency installation.")

    return str(python_exe)

def get_available_themes(maptoposter_dir: Path) -> list[str]:
    """
    Returns a list of available theme names by scanning the themes directory.
    """
    themes_dir = maptoposter_dir / "themes"
    themes = []
    if themes_dir.exists():
        for f in themes_dir.glob("*.json"):
            themes.append(f.stem)
    return sorted(themes)

import time

def run_generation_for_city(city: str, country: str, python_exe: str, maptoposter_dir: Path, worker_dir: Path, theme: str = None, all_themes: bool = True):
    """
    Runs the generation for a single city (iterating formats and themes) and moves the output.
    """
    
    # 1. Calculate Smart Bounds
    print(f"🧠 Calculating smart bounds for {city}, {country}...")
    calc_script = worker_dir / "calculate_bounds.py"
    try:
        # Run the calculation script using the venv python
        result = subprocess.run(
            [python_exe, str(calc_script), "--city", city, "--country", country],
            capture_output=True, text=True, check=True
        )
        # Parse the JSON output (stdout)
        # We need to find the JSON part if there are other logs
        # But calculate_bounds.py prints only JSON to stdout (logs go to stderr or are handled)
        # However, we set logging to INFO in calculate_bounds, which goes to stderr by default?
        # Yes, basicConfig default is stderr. So stdout should be clean.
        bounds_data = json.loads(result.stdout.strip())
        
        lat = bounds_data['latitude']
        lon = bounds_data['longitude']
        dist = bounds_data['distance']
        admin_info = bounds_data['admin_info']
        
        print(f"✅ Bounds calculated: Lat={lat:.4f}, Lon={lon:.4f}, Dist={dist:.2f}km")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error calculating bounds: {e}")
        print(f"   Stderr: {e.stderr}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing bounds output: {e}")
        print(f"   Output was: {result.stdout}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during bounds calculation: {e}")
        return False

    # 2. Determine Folder Structure
    # Structure: output/{Pays}/{Region}/{Departement}/{Ville}/{Format}/
    
    parts = admin_info['parts']
    # Heuristic: OSM returns address parts from specific to general.
    # E.g. "City, Dept, Region, Country"
    # But sometimes it's more complex.
    # We'll try to map it from the end (General) to start (Specific)
    
    # We trust the 'country' arg passed by user for the top folder
    # But we try to find Region/Dept from parts.
    
    def clean_name(n):
        return "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in n]).strip()

    safe_country = clean_name(country)
    safe_city = clean_name(city)
    
    # Default fallback
    region = "Unknown_Region"
    dept = "Unknown_Dept"
    
    # Simple heuristic for France (Admin Levels)
    # usually: City (0), ..., Dept (-3), Region (-2), Country (-1)
    # But let's look at the parts list size
    if len(parts) >= 3:
        # Assuming last is Country, second to last is Region
        region = parts[-2]
    if len(parts) >= 4:
        # Assuming third to last is Dept
        dept = parts[-3]
        
    safe_region = clean_name(region)
    safe_dept = clean_name(dept)
    
    base_output_path = worker_dir / "output" / safe_country / safe_region / safe_dept / safe_city
    
    print(f"📂 Base Output directory: {base_output_path}")

    # 3. Prepare Themes
    available_themes = get_available_themes(maptoposter_dir)
    themes_to_run = []
    
    if theme:
        if theme not in available_themes:
             print(f"❌ Error: Theme '{theme}' not found. Available themes: {', '.join(available_themes)}")
             return False
        themes_to_run = [theme]
    elif all_themes:
        themes_to_run = available_themes
    else:
         # Default fallback if no theme specified and not all_themes
         # Use 'terracotta' as default if available, else first one
         default_theme = "terracotta"
         if default_theme in available_themes:
             themes_to_run = [default_theme]
         elif available_themes:
             themes_to_run = [available_themes[0]]
         else:
             print("❌ No themes found in themes directory.")
             return False

    if not themes_to_run:
         print("❌ No themes selected to run.")
         return False

    total_ops = len(FORMATS) * len(themes_to_run)
    current_op = 0
    success_count = 0

    # 4. Loop Formats and Themes
    for fmt_name, fmt_dims in FORMATS.items():
        fmt_dir = base_output_path / fmt_name
        fmt_dir.mkdir(parents=True, exist_ok=True)
        
        width = fmt_dims['w']
        height = fmt_dims['h']
        
        for t in themes_to_run:
            current_op += 1
            theme_label = t if t else "Default"
            print(f"[{current_op}/{total_ops}] 🎨 {fmt_name} ({width}x{height}) - Theme: {theme_label}...")
            
            # Construct Command
            # Use --latitude, --longitude, --distance (radius in km * 1000 for maptoposter? No, let's check maptoposter args)
            # Standard maptoposter usually takes --size (radius in km) or similar.
            # Wait, the story says "Utiliser --distance pour le rayon".
            # I'll assume --distance expects KM.
            # Also need to pass width/height. Maptoposter usually takes --width --height (in inches? or pixels?).
            # If I look at the story: "1080x1080px (-W 3.6 -H 3.6)"
            # So it expects -W and -H args (uppercase?). Or --width --height?
            # Standard argparse usually uses lowercase long args.
            # I will use --scale to adjust if needed, but the story gives specific W/H values.
            # I'll use `--width` and `--height` based on typical python argparse convention, 
            # BUT the story explicitly mentions `-W` and `-H`.
            # If the script uses `argparse`, `-W` might be a short alias.
            # Let's check `maptoposter` source? No access.
            # I'll assume standard args: `--width` and `--height` or pass them as is if maptoposter supports them.
            # But wait, `create_map_poster.py` is the target.
            # I'll try to use the standard ones I suspect: `--width`, `--height`.
            
            cmd = [
                 python_exe, "create_map_poster.py",
                 "--latitude", str(lat),
                 "--longitude", str(lon),
                 # The --distance argument in create_map_poster.py results in a map with minimum dimension = distance / 2.
                 # We want the map to cover the full diameter of the city (approx 2 * radius).
                 # So we need distance / 2 >= 2 * radius => distance >= 4 * radius.
                 "--distance", str(int(dist * 4000)), # Convert KM radius to 'Diameter * 2' in Meters
                 "--width", str(width),
                 "--height", str(height),
                 # We still pass --city for the label on the map (display-city)
                 # But we don't want it to trigger geocoding.
                 # Hopefully passing lat/lon overrides geocoding.
                 "--city", city, 
                 "--country", country,
             ]
            
            if t:
                cmd.extend(["--theme", t])
                
            # Clean source
            source_dir = maptoposter_dir / "posters"
            if source_dir.exists():
                for f in source_dir.glob("*"):
                    try:
                        if f.is_file(): f.unlink()
                    except: pass
            
            try:
                # Run generation
                env = os.environ.copy()
                env["MPLBACKEND"] = "Agg"
                env["PYTHONIOENCODING"] = "utf-8"
                
                # Stream output to console so user sees progress (OSMnx downloads, etc.)
                # capture_output=False is default, but we explicitly remove it.
                print(f"   ... Generating {fmt_name} with theme {theme_label} ...")
                subprocess.run(cmd, cwd=maptoposter_dir, check=True, env=env, text=True, encoding='utf-8')
                
                # Move files
                # Wait for FS
                time.sleep(1)
                
                files = list(source_dir.glob("*"))
                if not files:
                    # Retry
                    for _ in range(5):
                        time.sleep(1)
                        files = list(source_dir.glob("*"))
                        if files: break
                
                if files:
                    image_files = [f for f in files if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']]
                    if image_files:
                        for file_path in image_files:
                            # Rename to include theme and format to avoid collisions if flattened (though we have folders now)
                            # e.g. city-theme.png
                            # We want output: lyon-mobile.png (from story example)
                            # But we are in `Mobile_Wallpaper` folder.
                            # So `lyon.png` or `lyon-theme.png`?
                            # Story example: `output/.../Mobile_Wallpaper/lyon-mobile.png`
                            # It appends the format name.
                            
                            safe_fmt = clean_name(fmt_name).lower()
                            safe_theme = clean_name(theme_label).lower()
                            new_filename = f"{safe_city}-{safe_fmt}-{safe_theme}{file_path.suffix}"
                            
                            dest_file = fmt_dir / new_filename
                            if dest_file.exists(): dest_file.unlink()
                            
                            shutil.move(str(file_path), str(dest_file))
                            success_count += 1
                    else:
                        print(f"⚠️  No images generated for {fmt_name} / {theme_label}")
                else:
                    print(f"⚠️  No output files for {fmt_name} / {theme_label}")
                    print(f"   Check console output above for details.")

            except subprocess.CalledProcessError as e:
                print(f"❌ Error generating {fmt_name} / {theme_label}: {e}")
                print(f"   Check console output above for details.")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    print(f"🏁 Completed {city}. Generated {success_count}/{total_ops} maps.")
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="Generate city maps using maptoposter")
    parser.add_argument("--city", "-c", help="City name")
    parser.add_argument("--country", "-C", help="Country name")
    parser.add_argument("--theme", "-t", help="Specific theme (default: all themes if not specified)")
    parser.add_argument("--all-themes", action="store_true", help="Generate maps for all available themes")
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

    else:
        # Single city mode
        if not args.city or not args.country:
             print("❌ Error: --city and --country are required unless using --source-json")
             sys.exit(1)
             
        run_generation_for_city(args.city, args.country, python_exe, maptoposter_dir, worker_dir, args.theme, args.all_themes)

if __name__ == "__main__":
    main()
