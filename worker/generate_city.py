import argparse
import subprocess
import sys
import os
import shutil
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
            print("⚠️  Directory exists but is not a git repo. Skipping update.")

    # Ensure dependencies are installed? 
    # For now we assume the user manages the environment via the root requirements.txt or manually.
    # But ideally, we could check/install them here too.

def main():
    parser = argparse.ArgumentParser(description="Generate city maps using maptoposter")
    parser.add_argument("--city", "-c", required=True, help="City name")
    parser.add_argument("--country", "-C", required=True, help="Country name")
    parser.add_argument("--theme", "-t", help="Specific theme (default: all themes if not specified, or use --all-themes)")
    parser.add_argument("--all-themes", action="store_true", help="Generate maps for all available themes")
    
    args = parser.parse_args()

    # Determine paths
    worker_dir = Path(__file__).parent.absolute()
    maptoposter_dir = worker_dir / "maptoposter"
    script_path = maptoposter_dir / "create_map_poster.py"

    # 1. Install / Update maptoposter
    ensure_maptoposter_installed(maptoposter_dir)

    if not script_path.exists():
        print(f"❌ Error: create_map_poster.py still not found at {script_path} after clone attempt.")
        sys.exit(1)

    # 2. Construct the command
    python_exe = sys.executable
    cmd = [python_exe, "create_map_poster.py", "--city", args.city, "--country", args.country]

    if args.theme:
        cmd.extend(["--theme", args.theme])
    elif args.all_themes:
        cmd.append("--all-themes")
    else:
        print("ℹ️  No theme specified, defaulting to --all-themes.")
        cmd.append("--all-themes")

    print(f"🚀 Executing generation for {args.city}, {args.country}...")
    print(f"   Command: {' '.join(cmd)}")
    print(f"   CWD: {maptoposter_dir}")

    # 3. Execute
    try:
        # Run inside maptoposter dir to resolve relative assets
        result = subprocess.run(cmd, cwd=maptoposter_dir, check=True)
        print("✅ Generation completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during generation: {e}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Generation stopped by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
