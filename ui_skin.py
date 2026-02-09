import tkinter as tk
from data_manager import load_user_data, save_user_data, load_champions
from assets_manager import get_splash
import threading
import random
from PIL import Image, ImageTk

BG = "#0A1428"
CARD = "#1F2933"
TEXT = "#E5E7EB"
ACCENT = "#C89B3C"


class SkinUI(tk.Frame):
    def __init__(self, master, champion, main_ui):
        super().__init__(master, bg=BG)
        self.master = master
        self.champion = champion
        self.main_ui = main_ui

        self.champions = load_champions()
        self.user_data = load_user_data()
        self.user_data.setdefault(self.champion, {})

        self.image_cache = {}  # Cache voor loaded images

        self.build_layout()
        self.populate_skins()

        self.master.bind("<Configure>", self.on_resize)

    # ---------------- LAYOUT ----------------
    def build_layout(self):
        # Top: back button + title
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=5)
        tk.Button(top, text="← Back", bg=ACCENT, fg="black", command=self.go_back).pack(side="left", padx=10)
        tk.Label(top, text=f"{self.champion} Skins", fg=ACCENT, bg=BG, font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)

        # Content: left skin list, right splash + randomize
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True)

        # ---- LEFT: scrollable skin list ----
        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="y", padx=10, pady=10)

        self.canvas = tk.Canvas(left, bg=BG, highlightthickness=0, width=360)
        scroll = tk.Scrollbar(left, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="y", expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

        # ---- RIGHT: splash + randomize ----
        right = tk.Frame(content, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        # Splash frame
        self.splash_frame = tk.Frame(right, bg=BG)
        self.splash_frame.pack(fill="both", expand=True, pady=20, padx=20)

        self.splash_label = tk.Label(self.splash_frame, bg=BG, fg=TEXT, text="Select a skin to preview!", font=("Segoe UI", 20, "bold"))
        self.splash_label.place(relx=0.5, rely=0.5, anchor="center")

        # Loading overlay
        self.loading_overlay = tk.Label(
            self.splash_frame,
            text="Loading...",
            fg=TEXT,
            bg="#000000",
            font=("Segoe UI", 16, "bold")
        )
        self.loading_overlay.place(relx=0.5, rely=0.5, anchor="center")
        self.loading_overlay.lower()

        # Randomize button
        tk.Button(right, text="🎲 Randomize Skin", bg=ACCENT, fg="black", font=("Segoe UI", 12, "bold"),
                  command=self.randomize).pack(pady=10)

    # ---------------- SKINS ----------------
    def populate_skins(self):
        self.vars = {}
        self.fav_vars = {}

        first_skin_to_show = None

        for skin_name, skin_data in self.champions[self.champion].items():
            # Capitalize default
            if skin_name.lower() == "default":
                skin_name_display = "Default"
            else:
                skin_name_display = skin_name

            self.user_data[self.champion].setdefault(skin_name, {"owned": False, "favorite": False})

            row = tk.Frame(self.list_frame, bg=CARD)
            row.pack(fill="x", pady=4, padx=4)

            owned = tk.BooleanVar(value=self.user_data[self.champion][skin_name]["owned"])
            fav = tk.BooleanVar(value=self.user_data[self.champion][skin_name]["favorite"])

            chk = tk.Checkbutton(row, text=skin_name_display, variable=owned, bg=CARD, fg=TEXT, selectcolor=CARD,
                                 font=("Segoe UI", 11, "bold"), command=self.save, anchor="w")
            chk.pack(side="left", fill="x", expand=True, padx=8)

            star = tk.Checkbutton(row, text="⭐", variable=fav, bg=CARD, fg=ACCENT, selectcolor=CARD,
                                  font=("Segoe UI", 14, "bold"), command=self.save)
            star.pack(side="right", padx=8)

            chk.bind("<Button-1>", lambda e, s=skin_name: self.show_skin(s))

            self.vars[skin_name] = owned
            self.fav_vars[skin_name] = fav

            if first_skin_to_show is None and (owned.get() or fav.get()):
                first_skin_to_show = skin_name

        # Toon skin of placeholder
        if first_skin_to_show:
            self.show_skin(first_skin_to_show)
        else:
            self.splash_label.config(text="Select a skin to preview!", image="", fg=TEXT, font=("Segoe UI", 20, "bold"))
            self.loading_overlay.lower()

    # ---------------- SHOW SPLASH ----------------
    def show_skin(self, skin):
        self.loading_overlay.lift()

        if skin in self.image_cache:
            self.set_splash(self.image_cache[skin])
            return

        def load_image():
            skin_id = self.champions[self.champion][skin]["id"]
            max_w = self.splash_frame.winfo_width() or 600
            max_h = self.splash_frame.winfo_height() or 340

            # Load and scale without stretching
            img = get_splash(self.champion, skin_id, size=(max_w, max_h))
            self.image_cache[skin] = img
            self.after(0, lambda: self.set_splash(img))

        threading.Thread(target=load_image, daemon=True).start()

    def set_splash(self, img):
        self.splash_label.config(image=img, text="")
        self.splash_label.image = img
        self.loading_overlay.lower()

    # ---------------- RANDOMIZE ----------------
    def randomize(self):
        pool = [s for s, v in self.user_data[self.champion].items() if v.get("owned") or v.get("favorite")]
        if not pool:
            self.splash_label.config(text="No owned skins!", image="", fg=TEXT)
            return
        self.show_skin(random.choice(pool))

    # ---------------- SAVE ----------------
    def save(self):
        for skin in self.vars:
            self.user_data[self.champion][skin]["owned"] = self.vars[skin].get()
            self.user_data[self.champion][skin]["favorite"] = self.fav_vars[skin].get()
        save_user_data(self.user_data)

    # ---------------- BACK ----------------
    def go_back(self):
        self.grid_forget()
        self.main_ui.grid(row=0, column=0, sticky="nsew")

    # ---------------- SCROLL ----------------
    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")

    # ---------------- RESIZE ----------------
    def on_resize(self, event):
        # Huidige skin
        current_skin = None
        if hasattr(self.splash_label, "image") and self.splash_label.image:
            for k, v in self.image_cache.items():
                if v == self.splash_label.image:
                    current_skin = k
                    break

        for skin, img in list(self.image_cache.items()):
            skin_id = self.champions[self.champion][skin]["id"]
            max_w = self.splash_frame.winfo_width() or 600
            max_h = self.splash_frame.winfo_height() or 340
            self.image_cache[skin] = get_splash(self.champion, skin_id, size=(max_w, max_h))

        if current_skin:
            self.show_skin(current_skin)
