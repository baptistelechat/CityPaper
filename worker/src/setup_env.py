import sys
import os
import shutil
import subprocess
from pathlib import Path
from .config import MAPTOPOSTER_REPO

def apply_custom_patches(maptoposter_dir: Path):
    """
    Applies custom overrides from worker/custom_overrides to the maptoposter directory.
    This allows persisting modifications even after a git pull.
    """
    worker_dir = maptoposter_dir.parent
    overrides_dir = worker_dir / "src/custom_overrides"
    if not overrides_dir.exists():
        return

    print("🔧 Checking for custom patches...")
    count = 0
    # Use rglob to find all files in subdirectories
    for file_path in overrides_dir.rglob("*"):
        if file_path.is_file():
            # Calculate relative path to preserve structure
            rel_path = file_path.relative_to(overrides_dir)
            target_path = maptoposter_dir / rel_path
            
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"   ✨ Patching {rel_path}...")
            shutil.copy2(file_path, target_path)
            count += 1
    
    if count > 0:
        print(f"✅ Applied {count} custom patch(es).")
    else:
        print("   No patches found to apply.")

def ensure_maptoposter_installed(maptoposter_dir: Path):
    """
    Ensures that the maptoposter repository is cloned and up-to-date.
    Then applies any custom patches.
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

    # Always apply patches after update/clone check
    apply_custom_patches(maptoposter_dir)

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
