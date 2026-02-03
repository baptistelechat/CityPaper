import argparse
import subprocess
import sys
import os
import shutil
import json
from pathlib import Path

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
    Runs the generation for a single city (iterating themes) and moves the output.
    """
    
    # User requested: worker/output/<City>
    safe_city_name = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in city]).strip()
    dest_dir = worker_dir / "output" / safe_city_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Starting generation for {city}, {country}...")
    print(f"📂 Output directory: {dest_dir}")

    themes_to_run = []
    if theme:
        themes_to_run = [theme]
    else:
        # If all_themes is True (default)
        themes_to_run = get_available_themes(maptoposter_dir)
        if not themes_to_run:
            print("⚠️  No themes found. Running with default arguments just in case.")
            themes_to_run = [None] # Will rely on script default

    success_count = 0
    total_themes = len(themes_to_run)
    
    for i, t in enumerate(themes_to_run, 1):
        cmd = [python_exe, "create_map_poster.py", "--city", city, "--country", country]
        if t:
            cmd.extend(["--theme", t])
            print()
            print(f"[{i}/{total_themes}] 🎨 Generating theme: {t}...")
        else:
            print()
            print(f"[{i}/{total_themes}] 🎨 Generating default theme...")

        # Clean source directory before generation to avoid moving old files
        source_dir = maptoposter_dir / "posters"
        if source_dir.exists():
            for f in source_dir.glob("*"):
                try:
                    if f.is_file():
                        f.unlink()
                except Exception:
                    pass

        try:
            # Run generation with Agg backend to avoid GUI windows
            env = os.environ.copy()
            env["MPLBACKEND"] = "Agg"
            subprocess.run(cmd, cwd=maptoposter_dir, check=True, env=env)
            
            # Move files immediately
            source_dir = maptoposter_dir / "posters"
            moved = False
            
            # Wait a bit for file system consistency
            time.sleep(1)
            
            if source_dir.exists():
                # Find files matching the theme (or all files if we just ran one)
                files = list(source_dir.glob("*"))
                
                # Retry loop if no files found immediately (sometimes OS lag)
                if not files:
                    print("⏳ No files found immediately, waiting...")
                    for _ in range(5):
                        time.sleep(1)
                        files = list(source_dir.glob("*"))
                        if files:
                            break
                
                if files:
                    # Filter for image files only
                    image_files = [f for f in files if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']]
                    
                    if image_files:
                        print(f"📦 Found {len(image_files)} image(s) to move.")
                        for file_path in image_files:
                            dest_file = dest_dir / file_path.name
                            # Handle potential overwrites
                            if dest_file.exists():
                                 dest_file.unlink()
                            try:
                                shutil.move(str(file_path), str(dest_file))
                                print(f"      ✅ Moved to: {dest_file.name}")
                                moved = True
                            except Exception as move_err:
                                print(f"      ❌ Failed to move {file_path.name}: {move_err}")
                    else:
                        print(f"⚠️  No image files found in {source_dir} (found: {[f.name for f in files]}).")
                else:
                     print(f"⚠️  Directory {source_dir} is empty after generation.")
            else:
                print(f"⚠️  Directory {source_dir} does not exist.")
            
            if moved:
                success_count += 1
            else:
                print(f"⚠️  No file produced for theme {t}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating theme {t}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    print(f"🏁 Completed {city}. Generated {success_count}/{len(themes_to_run)} maps.")
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
