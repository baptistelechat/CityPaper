import json
import subprocess
import os
import shutil
import time
from pathlib import Path
from .config import FORMATS
from .setup_env import get_available_themes
from .storage import HuggingFaceClient

def clean_name(n):
    return "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in n]).strip()

def calculate_bounds(city: str, country: str, python_exe: str, worker_dir: Path):
    """
    Calculates the smart bounds for a given city and country.
    """
    print(f"🧠 Calculating smart bounds for {city}, {country}...")
    calc_script = worker_dir / "src" / "calculate_bounds.py"
    try:
        # Run the calculation script using the venv python
        result = subprocess.run(
            [python_exe, str(calc_script), "--city", city, "--country", country],
            capture_output=True, text=True, check=True
        )
        # Parse the JSON output (stdout)
        bounds_data = json.loads(result.stdout.strip())
        
        lat = bounds_data['latitude']
        lon = bounds_data['longitude']
        dist = bounds_data['distance']
        admin_info = bounds_data['admin_info']
        
        print(f"✅ Bounds calculated: Lat={lat:.4f}, Lon={lon:.4f}, Dist={dist:.2f}km")
        return lat, lon, dist, admin_info
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error calculating bounds: {e}")
        print(f"   Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing bounds output: {e}")
        print(f"   Output was: {result.stdout}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during bounds calculation: {e}")
        return None

def determine_output_path(worker_dir: Path, city: str, country: str, admin_info: dict):
    """
    Determines the output directory structure based on admin info.
    Structure: output/{Country}/{Region}/{State}/{County}/{Postcode}/{City}
    (Skipping empty levels)
    """
    safe_country = clean_name(country)
    safe_city = clean_name(city)
    
    # Try to get structured info first
    structured = admin_info.get('structured', {})
    
    path_parts = []
    
    if structured:
        # 1. Country
        if structured.get('country'):
             safe_country = clean_name(structured.get('country'))
        path_parts.append(safe_country)

        # 2. Region (optional)
        if structured.get('region'):
             path_parts.append(clean_name(structured.get('region')))
             
        # 3. State (optional)
        if structured.get('state'):
             path_parts.append(clean_name(structured.get('state')))
        
        # 4. County (optional)
        if structured.get('county'):
             path_parts.append(clean_name(structured.get('county')))
        
        # 5. Postcode (optional)
        if structured.get('postcode'):
             path_parts.append(clean_name(structured.get('postcode')))

        # 6. City
        if structured.get('city'):
             safe_city = clean_name(structured.get('city'))
             print(f"🏙️  Using Structured City Name for folder: {structured.get('city')}")
        path_parts.append(safe_city)
         
    else:
        # Fallback to heuristics on parts
        # This path is less reliable but we try to map it roughly
        # Heuristic: Country is first (or last depending on list order?), City is last
        # Actually Nominatim parts are usually specific -> general (City, ..., Country) or reverse?
        # In calculate_bounds we did: parts = [p.strip() for p in display_name.split(',')]
        # display_name is usually "City, County, State, Country" or similar.
        
        # Let's just use Country / City if structured fails, or try to fill gaps
        # But we previously had logic for Region/Dept.
        
        parts = admin_info.get('parts', [])
        # Assume parts are in display_name order (usually Specific -> General)
        # So: City, ..., Country
        
        path_parts.append(safe_country) # Country
        
        # We can't reliably guess region/state/county from a flat list without structured data
        # So we just append City
        path_parts.append(safe_city)

    # Construct path
    base_output_path = worker_dir / "output"
    for part in path_parts:
        base_output_path = base_output_path / part
        
    print(f"📂 Base Output directory: {base_output_path}")
    return base_output_path

def run_generation_for_city(city: str, country: str, python_exe: str, maptoposter_dir: Path, worker_dir: Path, theme: str = None, all_themes: bool = True, display_city_override: str = None, display_country_override: str = None):
    """
    Runs the generation for a single city (iterating formats and themes) and moves the output.
    """
    
    # 1. Calculate Smart Bounds
    bounds_result = calculate_bounds(city, country, python_exe, worker_dir)
    if not bounds_result:
        return False
    
    lat, lon, dist, admin_info = bounds_result

    # Determine Display City Name
    display_city = city # Default to input
    
    if display_city_override:
        display_city = display_city_override
        print(f"🏷️  Using Manual Display City Name: {display_city}")
    elif admin_info and 'structured' in admin_info and admin_info['structured'].get('city'):
        display_city = admin_info['structured']['city']
        print(f"🏷️  Auto-detected Display City Name (Structured): {display_city}")
    elif admin_info and 'parts' in admin_info and admin_info['parts']:
        display_city = admin_info['parts'][0]
        print(f"🏷️  Auto-detected Display City Name (Parts): {display_city}")

    # Determine Display Country Name
    display_country = country
    if display_country_override:
        display_country = display_country_override
        print(f"🏷️  Using Manual Display Country Name: {display_country}")

    # 2. Determine Folder Structure
    base_output_path = determine_output_path(worker_dir, city, country, admin_info)

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
         # Default to all themes if no specific theme is requested
         print("ℹ️  No specific theme selected. Generating all available themes...")
         themes_to_run = available_themes
         
         if not themes_to_run:
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
            
            cmd = [
                 python_exe, "create_map_poster.py",
                 "--latitude", str(lat),
                 "--longitude", str(lon),
                 # The --distance argument in create_map_poster.py acts as the "View Size" (Diameter).
                 # It divides this by 2 internally for cropping, so we must pass the Diameter.
                 "--distance", str(int(dist * 2000)), # Convert KM radius to Meters * 2 (Diameter)
                 "--width", str(width),
                 "--height", str(height),
                 "--city", city, 
                 "--country", country,
                 "--display-city", display_city,
                 "--display-country", display_country,
             ]
            
            if t:
                cmd.extend(["--theme", t])
                
            # Retry loop for generation
            max_retries = 3
            retry_delay = 5 # seconds
            
            for attempt in range(1, max_retries + 1):
                # Clean source folder before each attempt to avoid mixing files
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
                    if attempt > 1:
                        print(f"   🔄 Attempt {attempt}/{max_retries} for {fmt_name} - {theme_label}...")
                    else:
                        print(f"   ... Generating {fmt_name} with theme {theme_label} ...")
                        
                    subprocess.run(cmd, cwd=maptoposter_dir, check=True, env=env, text=True, encoding='utf-8')
                    
                    # Move files
                    # Wait for FS
                    time.sleep(1)
                    
                    files = list(source_dir.glob("*"))
                    if not files:
                        # Retry listing files (fs latency)
                        for _ in range(5):
                            time.sleep(1)
                            files = list(source_dir.glob("*"))
                            if files: break
                    
                    if files:
                        image_files = [f for f in files if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']]
                        if image_files:
                            for file_path in image_files:
                                safe_fmt = clean_name(fmt_name).lower()
                                safe_theme = clean_name(theme_label).lower()
                                
                                # Use display_city for filename if available (cleaner name)
                                # otherwise fall back to input city
                                filename_city_base = display_city if display_city else city
                                safe_city_name = clean_name(filename_city_base)
                                
                                new_filename = f"{safe_city_name}-{safe_fmt}-{safe_theme}{file_path.suffix}"
                                
                                dest_file = fmt_dir / new_filename
                                if dest_file.exists(): dest_file.unlink()
                                
                                shutil.move(str(file_path), str(dest_file))
                                success_count += 1
                            # Success! Break the retry loop
                            break
                        else:
                            # Files exist but not images? strange, treat as failure to retry
                            print(f"⚠️  No images generated for {fmt_name} / {theme_label} (found: {files})")
                            raise Exception("Output files found but no images")
                    else:
                        print(f"⚠️  No output files for {fmt_name} / {theme_label}")
                        raise Exception("No output files generated")

                except subprocess.CalledProcessError as e:
                    print(f"❌ Error generating {fmt_name} / {theme_label}: {e}")
                    if attempt < max_retries:
                        print(f"   ⏳ Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"   ❌ Failed after {max_retries} attempts.")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    if attempt < max_retries:
                        print(f"   ⏳ Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"   ❌ Failed after {max_retries} attempts.")

    print(f"🏁 Completed {city}. Generated {success_count}/{total_ops} maps.")

    uploaded_urls = {}
    # HF Upload
    if success_count > 0:
        print("☁️  Starting upload to Hugging Face...")
        hf = HuggingFaceClient()
        output_root = worker_dir / "output"
        
        try:
            relative_prefix = base_output_path.relative_to(output_root)
            hf_prefix = relative_prefix.as_posix()
        except ValueError:
             hf_prefix = f"{clean_name(country)}/{clean_name(city)}"
             
        print(f"📦 Uploading to HF prefix: {hf_prefix}")
        
        # Construct detailed location string for commit message
        location_parts = []
        if admin_info and 'structured' in admin_info:
            s = admin_info['structured']
            # Order: Country / Region / State / County / Postcode / City (or Town/Village)
            # We use the raw values for a pretty commit message
            keys_to_check = ['country', 'region', 'state', 'county', 'postcode', 'city', 'town', 'village']
            for key in keys_to_check:
                val = s.get(key)
                if val and val not in location_parts:
                    location_parts.append(val)
        
        if location_parts:
            location_str = "_".join(location_parts)
        else:
            # Fallback to display names
            location_str = f"{display_country}_{display_city}"

        commit_msg = f"🖼️ Add maps for {location_str}"
        uploaded_urls = hf.upload_directory(base_output_path, hf_prefix, commit_message=commit_msg)
        
        if uploaded_urls:
            print("🚀 HF Upload Summary:")
            for path, url in uploaded_urls.items():
                print(f"   - {path}: {url}")
            
            # Auto-purge logic
            try:
                # IMPORTANT: Only purge the specific city folder we just generated and uploaded
                # NEVER delete the entire output_root or "demo" folder
                if base_output_path.exists() and "demo" not in base_output_path.parts:
                    print(f"🧹 Purging local cache for {city} to free up space...")
                    shutil.rmtree(base_output_path)
                    
                    # Also remove empty parent directories up to 'output'
                    parent = base_output_path.parent
                    while parent != output_root and parent != worker_dir:
                        try:
                            parent.rmdir() # Only removes if empty
                            parent = parent.parent
                        except OSError:
                            # Directory not empty or other error
                            break
                            
                    print("✅ Local cache cleared.")
            except Exception as e:
                print(f"⚠️  Failed to purge local cache: {e}")

    return success_count > 0, uploaded_urls, admin_info
