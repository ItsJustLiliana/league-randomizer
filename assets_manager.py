import os
import urllib.request
from PIL import Image, ImageTk

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# Cache resized images to avoid reprocessing
_image_cache = {}


def clear_assets():
    for file in os.listdir(ASSETS_DIR):
        try:
            os.remove(os.path.join(ASSETS_DIR, file))
        except:
            pass
    _image_cache.clear()


def get_splash(champ, skin_id, size=(320, 180)):
    key = (champ, skin_id, size)
    if key in _image_cache:
        return _image_cache[key]

    filename = f"{champ}_{skin_id}.jpg".replace(" ", "_")
    path = os.path.join(ASSETS_DIR, filename)

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        try:
            url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ.replace(' ', '')}_{skin_id}.jpg"
            urllib.request.urlretrieve(url, path)
        except:
            # fallback: leeg plaatje
            img = Image.new("RGB", size, "#0A1428")
            photo = ImageTk.PhotoImage(img)
            _image_cache[key] = photo
            return photo

    try:
        img = Image.open(path).resize(size, Image.LANCZOS)
    except:
        img = Image.new("RGB", size, "#0A1428")

    photo = ImageTk.PhotoImage(img)
    _image_cache[key] = photo
    return photo
