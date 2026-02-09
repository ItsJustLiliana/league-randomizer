import json
import os
import threading
import time
import urllib.request

CHAMPIONS_FILE = "champions.json"
USER_FILE = "user_data.json"

DDRAGON_CHAMP_URL = "https://ddragon.leagueoflegends.com/cdn/14.1.1/data/en_US/champion.json"
DDRAGON_CHAMP_DETAIL = "https://ddragon.leagueoflegends.com/cdn/14.1.1/data/en_US/champion/{champ}.json"


# ---------------------------
# File bootstrap
# ---------------------------
def ensure_files():
    if not os.path.exists(CHAMPIONS_FILE):
        with open(CHAMPIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


# ---------------------------
# Loaders
# ---------------------------
def load_champions():
    with open(CHAMPIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_user_data():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_data(data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------
# Champion refresh
# ---------------------------
def refresh_champions(progress_cb=None, done_cb=None):
    """
    Downloads champions + skins from Riot API.
    Runs in background thread.
    """

    def worker():
        try:
            urllib.request.urlretrieve(DDRAGON_CHAMP_URL, "_tmp_champs.json")
            with open("_tmp_champs.json", "r", encoding="utf-8") as f:
                champ_list = json.load(f)["data"]

            total = len(champ_list)
            result = {}

            for i, champ_key in enumerate(sorted(champ_list)):
                if progress_cb:
                    progress_cb(i + 1, total, champ_key)

                url = DDRAGON_CHAMP_DETAIL.format(champ=champ_key)
                urllib.request.urlretrieve(url, "_tmp_detail.json")

                with open("_tmp_detail.json", "r", encoding="utf-8") as f:
                    detail = json.load(f)["data"][champ_key]

                skins = {}
                for skin in detail["skins"]:
                    skins[skin["name"]] = {"id": skin["num"]}

                result[detail["name"]] = skins
                time.sleep(0.01)  # keeps UI responsive

            with open(CHAMPIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            if done_cb:
                done_cb(True)

        except Exception as e:
            print("Refresh error:", e)
            if done_cb:
                done_cb(False)

        finally:
            for tmp in ("_tmp_champs.json", "_tmp_detail.json"):
                if os.path.exists(tmp):
                    os.remove(tmp)

    threading.Thread(target=worker, daemon=True).start()
