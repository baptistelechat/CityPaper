import os
from dotenv import load_dotenv

load_dotenv()

FORMATS = {
    "Instagram_Post": {"w": 3.6, "h": 3.6},
    "Mobile_Wallpaper": {"w": 3.6, "h": 6.4},
    "HD_Wallpaper": {"w": 6.4, "h": 3.6},
    "4K_Wallpaper": {"w": 12.8, "h": 7.2},
    "A4_Print": {"w": 8.3, "h": 11.7}
}

MAPTOPOSTER_REPO = "https://github.com/originalankur/maptoposter.git"

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_ID = os.getenv("HF_REPO_ID", "Baptiste/citypaper-maps")
