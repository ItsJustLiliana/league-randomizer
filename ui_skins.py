import tkinter as tk
from data_manager import load_user_data, save_user_data, load_champions
from assets_manager import get_splash
import threading
import random
from PIL import Image, ImageTk
from theme import BG, CARD, TEXT, ACCENT, APP_PADDING, FONT_HEADER, FONT_TEXT, FONT_BUTTON

class SkinsUI(tk.Frame):
    def __init__(self, master, champion, main_ui):
        super().__init__(master, bg=BG, padx=APP_PADDING, pady=APP_PADDING)
        self.master = master
        self.champion = champion
        self.main_ui = main_ui

        self.champions = load_champions()
        self.user_data = load_user_data()
        self.user_data.setdefault(self.champion, {})

        self.image_cache = {}  # PIL.Image
        self.photo_cache = {}  # ImageTk.PhotoImage

        self.build_layout()
        self.populate_skins()
        self.master.bind("<Configure>", self.on_resize)

    # ---------------- LAYOUT ----------------
    def build_layout(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0,5))
        tk.Button(top, text="← Back", bg=ACCENT, fg="black", font=FONT_BUTTON, command=self.go_back).pack(side="left", padx=10)
        tk.Label(top, text=f"{self.champion} Skins", fg=ACCENT, bg=BG, font=FONT_HEADER).pack(side="left", padx=20, pady=5)

        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True)

        # ---- LEFT: scrollable skin list ----
        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="y", pady=10)

        # Select/Deselect All buttons
        btn_frame = tk.Frame(left, bg=BG)
        btn_frame.pack(fill="x", pady=(0,5))
        tk.Button(btn_frame, text="Select All", bg=ACCENT, fg="black", font=FONT_BUTTON, command=self.select_all).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Deselect All", bg=ACCENT, fg="black", font=FONT_BUTTON, command=self.deselect_all).pack(side="left", padx=2)

        # Scrollable canvas
        self.canvas = tk.Canvas(left, bg=BG, highlightthickness=0)
        self.scroll = tk.Scrollbar(left, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set, width=360)

        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="y", expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>", self.on_list_frame_configure)

        # Bind scroll recursively
        self.bind_scroll_recursive(self.list_frame)

        # ---- RIGHT: splash + randomize ----
        right = tk.Frame(content, bg=BG)
        right.pack(side="right", fill="both", expand=True, padx=(10,0))

        self.splash_frame = tk.Frame(right, bg=BG)
        self.splash_frame.pack(fill="both", expand=True, pady=20, padx=20)

        self.splash_label = tk.Label(self.splash_frame, bg=BG, fg=TEXT,
                                     text="Select a skin to preview!", font=FONT_HEADER)
        self.splash_label.place(relx=0.5, rely=0.45, anchor="center")

        self.splash_name_label = tk.Label(self.splash_frame, bg=BG, fg=TEXT,
                                          text="", font=FONT_TEXT)
        self.splash_name_label.place(relx=0.5, rely=0.75, anchor="center")

        self.loading_overlay = tk.Label(self.splash_frame, text="Loading...", fg=TEXT, bg=BG, font=FONT_TEXT)
        self.loading_overlay.place_forget()

        tk.Button(right, text="🎲 Randomize Skin", bg=ACCENT, fg="black",
                  font=FONT_BUTTON, command=self.randomize).pack(pady=10)

    # ---------------- SCROLL ----------------
    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")

    def bind_scroll_recursive(self, widget):
        widget.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self.on_mousewheel))
        widget.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        for child in widget.winfo_children():
            self.bind_scroll_recursive(child)

    def on_list_frame_configure(self, event):
        # Update scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Make canvas width at least as wide as the widest child
        required_width = max(self.list_frame.winfo_reqwidth(), self.canvas.winfo_width())
        self.canvas.itemconfig(self.window_id, width=required_width)

    # ---------------- SKINS ----------------
    def populate_skins(self):
        self.vars = {}
        self.fav_vars = {}
        first_skin_to_show = None

        for skin_name, skin_data in self.champions[self.champion].items():
            display_name = "Default" if skin_name.lower() == "default" else skin_name
            self.user_data[self.champion].setdefault(skin_name, {"owned": False, "favorite": False})

            row = tk.Frame(self.list_frame, bg=CARD)
            row.pack(fill="x", pady=4, padx=4)

            owned = tk.BooleanVar(value=self.user_data[self.champion][skin_name]["owned"])
            fav = tk.BooleanVar(value=self.user_data[self.champion][skin_name]["favorite"])

            chk = tk.Checkbutton(row, variable=owned, bg=CARD, fg=TEXT, selectcolor=CARD,
                                 font=FONT_TEXT, command=self.save, anchor="w")
            chk.pack(side="left", padx=8)

            lbl = tk.Label(row, text=display_name, bg=CARD, fg=TEXT, font=FONT_TEXT)
            lbl.pack(side="left", padx=4, fill="x", expand=True)
            lbl.bind("<Button-1>", lambda e, s=skin_name: self.show_skin(s))

            star = tk.Checkbutton(row, text="⭐", variable=fav, bg=CARD, fg=ACCENT,
                                  selectcolor=CARD, font=FONT_BUTTON, command=self.save)
            star.pack(side="right", padx=8)

            self.vars[skin_name] = owned
            self.fav_vars[skin_name] = fav

            if first_skin_to_show is None and (owned.get() or fav.get()):
                first_skin_to_show = skin_name

        self.bind_scroll_recursive(self.list_frame)
        if first_skin_to_show:
            self.show_skin(first_skin_to_show)

    # ---------------- SELECT / DESELECT ----------------
    def select_all(self):
        for var in self.vars.values(): var.set(True)
        self.save()

    def deselect_all(self):
        for var in self.vars.values(): var.set(False)
        self.save()

    # ---------------- SHOW SPLASH ----------------
    def show_skin(self, skin):
        if skin in self.photo_cache:
            self.splash_label.config(image=self.photo_cache[skin], text="")
            self.splash_label.image = self.photo_cache[skin]
            self.loading_overlay.place_forget()
            display_name = "Default" if skin.lower() == "default" else skin
            self.splash_name_label.config(text=display_name)
            return

        self.loading_overlay.place(relx=0.5, rely=0.5, anchor="center")

        def load_image():
            try:
                skin_id = self.champions[self.champion][skin]["id"]
                max_w = max(self.splash_frame.winfo_width(), 1)
                max_h = max(self.splash_frame.winfo_height(), 1)
                pil_img = get_splash(self.champion, skin_id, size=(max_w, max_h))
                self.image_cache[skin] = pil_img
                photo_img = ImageTk.PhotoImage(pil_img)
                self.photo_cache[skin] = photo_img
                self.after(0, lambda: self._display_photo(skin))
            except Exception as e:
                print(f"Error loading skin {skin}: {e}")
                self.after(0, self.loading_overlay.place_forget)

        threading.Thread(target=load_image, daemon=True).start()

    def _display_photo(self, skin):
        self.splash_label.config(image=self.photo_cache[skin], text="")
        self.splash_label.image = self.photo_cache[skin]
        display_name = "Default" if skin.lower() == "default" else skin
        self.splash_name_label.config(text=display_name)
        self.loading_overlay.place_forget()

    # ---------------- RANDOMIZE ----------------
    def randomize(self):
        pool = [s for s, v in self.user_data[self.champion].items() if v.get("owned") or v.get("favorite")]
        if not pool:
            self.splash_label.config(text="No owned skins!", image="", fg=TEXT)
            self.splash_name_label.config(text="")
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

    # ---------------- RESIZE ----------------
    def on_resize(self, event=None):
        for skin, pil_img in list(self.image_cache.items()):
            try:
                max_w = max(self.splash_frame.winfo_width(), 1)
                max_h = max(self.splash_frame.winfo_height(), 1)
                w, h = pil_img.size
                scale = min(max_w / w, max_h / h)
                new_size = (int(w * scale), int(h * scale))
                pil_resized = pil_img.resize(new_size, Image.LANCZOS)
                self.photo_cache[skin] = ImageTk.PhotoImage(pil_resized)
            except Exception:
                continue

        if hasattr(self.splash_label, "image") and self.splash_label.image:
            for k, v in self.photo_cache.items():
                if v == self.splash_label.image:
                    self.splash_label.config(image=v)
                    break
