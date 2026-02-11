import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env.local from project root (CityPaper/.env.local)
# worker/src/config.py -> worker/src -> worker -> CityPaper
env_path = Path(__file__).resolve().parent.parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

FORMATS = {
    "Instagram_Post": {"w": 3.6, "h": 3.6},
    # "Mobile_Wallpaper": {"w": 3.6, "h": 6.4},
    # "HD_Wallpaper": {"w": 6.4, "h": 3.6},
    # "4K_Wallpaper": {"w": 12.8, "h": 7.2},
    # "A4_Print": {"w": 8.3, "h": 11.7}
}

MAPTOPOSTER_REPO = "https://github.com/originalankur/maptoposter.git"

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_ID = os.getenv("HF_REPO_ID", "Baptiste/citypaper-maps")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # Service Role Key for Worker (preferred) or Anon Key
