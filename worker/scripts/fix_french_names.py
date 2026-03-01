
import json
import sys
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Try to import required modules
try:
    from geopy.geocoders import Nominatim
    import unicodedata
    from huggingface_hub import HfApi, HfFileSystem, CommitOperationCopy, CommitOperationDelete
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("👉 Please run this script using the worker virtual environment:")
    print(r"   .\worker\.venv\Scripts\python worker/scripts/fix_french_names.py")
    sys.exit(1)

# Load environment variables
root_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(root_dir / '.env.local')

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_ID = os.getenv("HF_REPO_ID")

# Add worker to path to import src modules if needed, 
# but for this standalone script we can just replicate the logic to be safe/simple
# or we can try to import.
# Let's try to import from src.db if possible, but path manipulation is needed.
sys.path.append(str(Path(__file__).parent.parent))

from src.db import slugify

def get_db_path():
    # worker/scripts/fix_french_names.py -> worker/scripts -> worker -> CityPaper
    root = Path(__file__).parent.parent.parent
    return root / "src" / "data" / "cities.json"

def clean_name(n):
    if not n: return ""
    return "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in n]).strip()

def get_folder_path(admin_info, city_name, country_name):
    """Reconstructs the folder path based on admin info."""
    structured = admin_info.get('structured', {})
    parts = []
    
    # 1. Country
    parts.append(clean_name(structured.get('country') or country_name))
    
    # 2. Region
    if structured.get('region'):
        parts.append(clean_name(structured.get('region')))
        
    # 3. State
    if structured.get('state'):
        parts.append(clean_name(structured.get('state')))
    
    # 4. County
    if structured.get('county'):
        parts.append(clean_name(structured.get('county')))
    
    # 5. Postcode
    if structured.get('postcode'):
        parts.append(clean_name(structured.get('postcode')))

    # 6. City
    city_part = clean_name(structured.get('city') or city_name)
    parts.append(city_part)
    
    return "/".join(parts)

def fix_city_names():
    db_path = get_db_path()
    print(f"📂 Loading database from {db_path}...")
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    geolocator = Nominatim(user_agent="CityPaper_Fix_Names_v1", timeout=10)
    
    # Initialize HF FileSystem and API
    fs = None
    api = None
    if HF_TOKEN and HF_REPO_ID:
        print(f"☁️  Connecting to Hugging Face ({HF_REPO_ID})...")
        fs = HfFileSystem(token=HF_TOKEN)
        api = HfApi(token=HF_TOKEN)
    else:
        print("⚠️  HF_TOKEN or HF_REPO_ID missing. Skipping remote folder renaming.")
    
    updates = []
    renames = [] # List of (old_path, new_path) tuples for folders

    print(f"🔍 Checking {len(cities)} cities...")
    
    # Accumulate all moves for a single commit to avoid rate limits
    all_commit_operations = []
    
    for city in cities:
        original_name = city['name']
        country = city['country']
        
        # Calculate OLD path before modification
        old_admin = city.get('admin_info', {})
        old_folder_path = get_folder_path(old_admin, original_name, country)

        # We want to force French names
        query = f"{original_name}, {country}"
        print(f"   Processing {query}...", end="", flush=True)
        
        try:
            location = geolocator.geocode(query, addressdetails=True, language='fr')
            if not location:
                print(" ❌ Not found via geocode.")
                continue
                
            addr = location.raw.get('address', {})
            
            # Construct new structured admin info
            new_admin_info = {
                "structured": {
                    "country": addr.get('country'),
                    "state": addr.get('state') or addr.get('region'),
                    "county": addr.get('county'),
                    "postcode": addr.get('postcode') or city['admin_info']['structured'].get('postcode'), # Keep original postcode if missing
                    "city": addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality') or original_name
                }
            }
            
            # RULE: If county is null, use state value
            if not new_admin_info['structured']['county']:
                new_admin_info['structured']['county'] = new_admin_info['structured']['state']
            
            # Compare with old
            old_structured = old_admin.get('structured', {})
            new_structured = new_admin_info['structured']
            
            # Check for changes in key fields
            changes = []
            if old_structured.get('state') != new_structured.get('state'):
                changes.append(f"State: {old_structured.get('state')} -> {new_structured.get('state')}")
            if old_structured.get('county') != new_structured.get('county'):
                changes.append(f"County: {old_structured.get('county')} -> {new_structured.get('county')}")
            if old_structured.get('region') != new_structured.get('region'): # Check region too if present
                 changes.append(f"Region: {old_structured.get('region')} -> {new_structured.get('region')}")

            if changes:
                print(f" ✅ Found updates: {', '.join(changes)}")
                
                # Calculate NEW path
                new_folder_path = get_folder_path(new_admin_info, original_name, country)
                
                if old_folder_path != new_folder_path:
                    renames.append((old_folder_path, new_folder_path))
                    print(f"      📂 Path Change: {old_folder_path} -> {new_folder_path}")

                # Generate new ID (Slug)
                slug_parts = []
                s_country = new_structured.get("country") or country
                s_state = new_structured.get("state")
                s_county = new_structured.get("county")
                s_postcode = new_structured.get("postcode")
                s_city = new_structured.get("city") or original_name
                
                if s_country: slug_parts.append(slugify(s_country))
                if s_state: slug_parts.append(slugify(s_state))
                if s_county: slug_parts.append(slugify(s_county))
                if s_postcode: slug_parts.append(slugify(s_postcode))
                if s_city: slug_parts.append(slugify(s_city))
                
                new_id = "-".join([p for p in slug_parts if p])
                
                # Update the city object
                city['admin_info'] = new_admin_info
                city['id'] = new_id
                
                updates.append(city['name'])
            else:
                print(" (No changes)")
            
            # Be nice to Nominatim
            time.sleep(1.1)
            
        except Exception as e:
            print(f" ❌ Error: {e}")

    # Process Remote Renames
    # Optimized to use batch operations instead of fs.mv/fs.rename which trigger commits
    if renames and fs:
        print(f"\n☁️  Processing {len(renames)} remote folder renames...")
        
        # We need to collect all unique moves.
        unique_moves = set()
        
        for old_p, new_p in renames:
            old_parts = old_p.split('/')
            new_parts = new_p.split('/')
            
            # Find the first index where they differ
            diff_index = -1
            for i in range(min(len(old_parts), len(new_parts))):
                if old_parts[i] != new_parts[i]:
                    diff_index = i
                    break
            
            if diff_index != -1:
                # Construct the path up to the difference
                old_parent = "/".join(old_parts[:diff_index+1])
                new_parent = "/".join(new_parts[:diff_index+1])
                unique_moves.add((old_parent, new_parent))
        
        print(f"ℹ️  Identified {len(unique_moves)} parent folder moves.")
        
        for old_p, new_p in sorted(list(unique_moves)):
            full_old_path = f"datasets/{HF_REPO_ID}/{old_p}"
            full_new_path = f"datasets/{HF_REPO_ID}/{new_p}"
            
            print(f"   🔄 Queueing move {old_p} -> {new_p} ...", end="")
            try:
                if fs.exists(full_old_path):
                     # Glob all files in old path
                     all_files_rename = fs.glob(f"{full_old_path}/**/*")
                     files_to_rename = [f for f in all_files_rename if fs.isfile(f)]
                     
                     rename_ops = []
                     for source_file in files_to_rename:
                         if source_file.startswith(full_old_path):
                             rel_path = source_file[len(full_old_path):].lstrip('/')
                         else:
                             rel_path = os.path.basename(source_file)
                         
                         dest_file = f"{full_new_path}/{rel_path}"
                         
                         prefix = f"datasets/{HF_REPO_ID}/"
                         if source_file.startswith(prefix): repo_src = source_file[len(prefix):]
                         else: repo_src = source_file
                         
                         if dest_file.startswith(prefix): repo_dest = dest_file[len(prefix):]
                         else: repo_dest = dest_file
                         
                         rename_ops.append(CommitOperationCopy(src_path_in_repo=repo_src, path_in_repo=repo_dest))
                         rename_ops.append(CommitOperationDelete(path_in_repo=repo_src))
                     
                     if rename_ops:
                         all_commit_operations.extend(rename_ops)
                         print(f" ✅ Queued {len(rename_ops)//2} files.")
                     else:
                         print(" ⚠️  No files found to move.")
                else:
                    print(f" ⚠️  Source {old_p} not found.")
            except Exception as e:
                print(f" ❌ Failed: {e}")

    if updates:
        # Backup first
        backup_path = db_path.with_suffix('.json.bak')
        import shutil
        shutil.copy(db_path, backup_path)
        print(f"📦 Backup saved to {backup_path}")

        print(f"\n📝 Saving {len(updates)} updates to {db_path}...")
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(cities, f, indent=2, ensure_ascii=False)
        print("✅ Database updated.")
    
    # REPAIR MODE: Check for English folders even if DB is up to date
    if fs:
        print("\n🔧 Checking remote folder consistency...")
        
        for city in cities:
            original_name = city['name']
            country = city['country']
            
            # 1. Calculate Expected (French) Path
            current_admin = city.get('admin_info', {})
            expected_path = "datasets/" + HF_REPO_ID + "/" + get_folder_path(current_admin, original_name, country)
            
            # Check if it exists
            if fs.exists(expected_path):
                # print(f"   ✅ {original_name}: OK")
                continue
            
            print(f"   ⚠️  {original_name}: Folder not found at expected path.")
            print(f"      Target: {expected_path}")
            
            # 2. Try to find the English path (Legacy)
            # More robust: search recursively for the city folder in the country
            try:
                print(f"      🕵️  Searching for ANY folder named '{original_name}' in {country}...")
                
                # Glob pattern: datasets/REPO/Country/**/CityName
                search_pattern = f"datasets/{HF_REPO_ID}/{clean_name(country)}/**/{clean_name(original_name)}"
                matches = fs.glob(search_pattern)
                
                found_legacy = False
                for match in matches:
                    # Match format usually: datasets/repo/path/to/folder
                    # Check if it's a directory? glob returns both files and dirs
                    if fs.isdir(match):
                        if match == expected_path:
                            continue # Skip if it's already correct (should have been caught above)
                        
                        print(f"      ✅ Found candidate folder: {match}")
                        print(f"      🔄 Moving content to: {expected_path}")
                        
                        try:
                            # Move files individually to ensure reliability and visibility
                            # glob returns full paths starting with datasets/REPO/...
                            # Note: HfFileSystem.glob with ** implies recursive, removing explicit recursive=True to avoid error
                            all_files = fs.glob(f"{match}/**/*")
                            files_to_move = [f for f in all_files if fs.isfile(f)]
                            
                            if not files_to_move:
                                print("      ⚠️  Folder seems empty.")
                                # Try to remove empty dir
                                try:
                                    fs.rm(match, recursive=True)
                                    print("      🗑️  Removed empty old directory.")
                                except:
                                    pass
                                continue

                            print(f"      📄 Found {len(files_to_move)} files to move...")
                            
                            operations = []
                            
                            for source_file in files_to_move:
                                # source_file: datasets/repo/path/to/old/file.png
                                # match: datasets/repo/path/to/old
                                
                                # Calculate relative path correctly
                                if source_file.startswith(match):
                                    rel_path = source_file[len(match):].lstrip('/')
                                else:
                                    # Should not happen with glob logic
                                    rel_path = os.path.basename(source_file)
                                    
                                dest_file = f"{expected_path}/{rel_path}"
                                
                                # Convert to repo-relative paths for API
                                prefix = f"datasets/{HF_REPO_ID}/"
                                if source_file.startswith(prefix):
                                    repo_src = source_file[len(prefix):]
                                else:
                                    repo_src = source_file # fallback?
                                    
                                if dest_file.startswith(prefix):
                                    repo_dest = dest_file[len(prefix):]
                                else:
                                    repo_dest = dest_file # fallback?
                                
                                # print(f"         Plan: {repo_src} -> {repo_dest}")
                                operations.append(CommitOperationCopy(src_path_in_repo=repo_src, path_in_repo=repo_dest))
                                operations.append(CommitOperationDelete(path_in_repo=repo_src))
                            
                            if operations:
                                print(f"      ✅ Queued {len(operations)//2} file moves for commit.")
                                all_commit_operations.extend(operations)
                                found_legacy = True
                                
                                # Do NOT delete manually, CommitOperationDelete handles it
                                print("      ✅ Scheduled for batch move.")
                                
                                break
                            else:
                                print("      ❌ No valid operations generated.")
                                
                        except Exception as move_err:
                            print(f"      ❌ Batch move failed: {move_err}")
                            pass
                
                if not found_legacy:
                    print(f"      ❌ No folder named '{original_name}' found in {country} tree.")
                    # Fallback to English geocoding guess if glob failed (e.g. name mismatch)?
                    # No, glob is better. If name changed (e.g. English vs French spelling), glob fails.
                    # Let's add English name fallback for glob.
                    
                    # Check if English name is different
                    try:
                        query = f"{original_name}, {country}"
                        location_en = geolocator.geocode(query, addressdetails=True, language='en')
                        if location_en:
                            addr_en = location_en.raw.get('address', {})
                            name_en = addr_en.get('city') or addr_en.get('town') or addr_en.get('village') or original_name
                            name_en_clean = clean_name(name_en)
                            
                            if name_en_clean != clean_name(original_name):
                                print(f"      🕵️  Trying English name: '{name_en_clean}'...")
                                search_pattern_en = f"datasets/{HF_REPO_ID}/{clean_name(country)}/**/{name_en_clean}"
                                matches_en = fs.glob(search_pattern_en)
                                for match in matches_en:
                                    if fs.isdir(match):
                                        print(f"      ✅ Found English candidate: {match}")
                                        print(f"      🔄 Moving to: {expected_path}")
                                        
                                        # Use batch operations for English fallback too
                                        try:
                                            all_files_en = fs.glob(f"{match}/**/*")
                                            files_to_move_en = [f for f in all_files_en if fs.isfile(f)]
                                            
                                            ops_en = []
                                            for source_file in files_to_move_en:
                                                if source_file.startswith(match):
                                                    rel_path = source_file[len(match):].lstrip('/')
                                                else:
                                                    rel_path = os.path.basename(source_file)
                                                
                                                dest_file = f"{expected_path}/{rel_path}"
                                                
                                                prefix = f"datasets/{HF_REPO_ID}/"
                                                if source_file.startswith(prefix): repo_src = source_file[len(prefix):]
                                                else: repo_src = source_file
                                                
                                                if dest_file.startswith(prefix): repo_dest = dest_file[len(prefix):]
                                                else: repo_dest = dest_file
                                                
                                                ops_en.append(CommitOperationCopy(src_path_in_repo=repo_src, path_in_repo=repo_dest))
                                                ops_en.append(CommitOperationDelete(path_in_repo=repo_src))
                                            
                                            if ops_en:
                                                all_commit_operations.extend(ops_en)
                                                print(f"      ✅ Queued {len(ops_en)//2} moves from English path.")
                                        except Exception as e:
                                            print(f"      ❌ Queue failed: {e}")
                                        break
                    except:
                        pass

                time.sleep(1.0) # Respect rate limits
                
            except Exception as e:
                print(f"      ❌ Error searching legacy path: {e}")

    # Commit all accumulated operations at once
    if all_commit_operations:
        print(f"\n🚀 Committing {len(all_commit_operations)} operations (moves/deletes) for {len(all_commit_operations)//2} files...")
        
        # Safe guard: Dry run if needed, but user wants to fix it.
        # Given rate limit, we must wait.
        
        try:
            api.create_commit(
                repo_id=HF_REPO_ID,
                operations=all_commit_operations,
                commit_message="Batch move of city folders to correct French paths",
                repo_type="dataset"
            )
            print("✨ Batch commit successful!")
        except Exception as e:
            print(f"❌ Batch commit failed: {e}")
            if "429" in str(e):
                print("⏳ Rate limit exceeded. Please wait ~1 hour before running this script again.")

    if not updates and not renames:
         print("\n✨ No metadata updates needed.")

if __name__ == "__main__":
    fix_city_names()
