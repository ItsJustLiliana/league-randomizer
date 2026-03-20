import os
import urllib.request
from PIL import Image

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Cache PIL.Image objects (never PhotoImage)
_image_cache = {}


def clear_assets():
    # Remove downloaded files
    for file in os.listdir(ASSETS_DIR):
        try:
            os.remove(os.path.join(ASSETS_DIR, file))
        except:
            pass
    _image_cache.clear()


def get_splash(champ, skin_id, size=None):
    """
    Returns a PIL.Image object (never ImageTk.PhotoImage)
    size: optional tuple (width, height) for resizing
    """
    key = (champ, skin_id)
    if key in _image_cache:
        img = _image_cache[key]
    else:
        filename = f"{champ}_{skin_id}.jpg".replace(" ", "_")
        path = os.path.join(ASSETS_DIR, filename)

        if not os.path.exists(path) or os.path.getsize(path) == 0:
            try:
                url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ.replace(' ', '')}_{skin_id}.jpg"
                urllib.request.urlretrieve(url, path)
            except:
                # fallback: empty image
                img = Image.new("RGB", (320, 180), "#0A1428")
                _image_cache[key] = img
                if size:
                    return img.resize(size, Image.LANCZOS)
                return img

        try:
            img = Image.open(path).convert("RGBA")
        except:
            img = Image.new("RGB", (320, 180), "#0A1428")

        _image_cache[key] = img

    if size:
        w, h = img.size
        scale = min(size[0] / w, size[1] / h)
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)

    return img  # NEVER return PhotoImage
