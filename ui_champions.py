import tkinter as tk
from tkinter import messagebox
from data_manager import load_champions, refresh_champions, load_user_data, save_user_data
from assets_manager import get_splash, clear_assets, ASSETS_DIR
from ui_skins import SkinsUI
import threading
import re
import os
from PIL import ImageTk
from theme import *

HARDCODE_ASSET_MAP = {
    "Bel'Veth": "Belveth",
    "Cho'Gath": "Chogath",
    "Kha'Zix": "Khazix",
    "K'Sante": "KSante",
    "Kai'Sa": "Kaisa",
    "LeBlanc": "Leblanc",
    "Dr. Mundo": "DrMundo",
    "Nunu & Willump": "Nunu",
    "Renata Glasc": "Renata",
    "Vel'Koz": "Velkoz",
}

class ChampionCard:
    def __init__(self, champ_name, frame, lbl, fav_btn):
        self.name = champ_name
        self.frame = frame
        self.lbl = lbl
        self.fav_btn = fav_btn
        self.image_loaded = False
        self.placeholder = frame.children['!label']

class ChampionsUI(tk.Frame):
    def __init__(self, master, landing_ui=None):
        super().__init__(master, bg=BG, padx=APP_PADDING, pady=APP_PADDING)
        self.master = master
        self.landing_ui = landing_ui

        self.champions = {}
        self.filtered_champions = {}
        self.card_refs = {}
        self.favorite_champs = set()
        self.card_image_cache = {}
        self._last_width = None
        self._resize_job = None
        self._lazy_load_job = None
        self._all_cards_loaded = False
        self._cols = 1

        self.build_header()
        self.build_canvas()
        self.load_favorites()

        if not load_champions():
            self.reload_champions()
        else:
            self.load_and_render()

        self.master.bind("<Configure>", self.on_resize)

    # ---------------- HEADER ----------------
    def build_header(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=5)
        
        # Back button (left side)
        if self.landing_ui:
            tk.Button(top, text="← Back to Menu", bg=ACCENT, fg="black", font=FONT_BUTTON,
                      command=self.go_back_to_landing).pack(side="left", padx=10)
        
        tk.Label(top, text="Champions", fg=ACCENT, bg=BG, font=FONT_HEADER).pack(side="left", padx=10, pady=(0,5))

        btn_frame = tk.Frame(top, bg=BG)
        btn_frame.pack(side="right", padx=10)

        tk.Button(btn_frame, text="🗑 Delete Skin Assets", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON,
                  command=self.delete_skin_assets).pack(side="right", padx=5)
        tk.Button(btn_frame, text="🗑 Delete ALL Assets", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON,
                  command=self.delete_all_assets).pack(side="right", padx=5)
        tk.Button(btn_frame, text="🔄 Reload Champions", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON,
                  command=self.reload_champions).pack(side="right", padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.apply_search_filter)
        tk.Entry(btn_frame, textvariable=self.search_var, font=FONT_TEXT).pack(side="right", padx=(5,5))

    # ---------------- CANVAS ----------------
    def build_canvas(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview, width=SCROLLBAR_WIDTH)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.container = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0,0), window=self.container, anchor="nw")
        self.container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Scroll binding
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self.on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    # ---------------- DATA ----------------
    def load_and_render(self):
        def load():
            self.champions = load_champions()
            self.filtered_champions = dict(self.champions)
            self.after(0, self.render_cards)
        threading.Thread(target=load, daemon=True).start()

    # ---------------- SEARCH ----------------
    def apply_search_filter(self, *args):
        query = self.search_var.get().lower()
        self.filtered_champions = {champ: data for champ, data in self.champions.items() if query in champ.lower()}
        # Reset image loading flags for filtered cards
        for champ, card_obj in self.card_refs.items():
            if champ not in self.filtered_champions:
                card_obj.image_loaded = False
        self.reorder_cards()

    # ---------------- RENDER CARDS ----------------
    def render_cards(self):
        for w in self.container.winfo_children():
            w.destroy()
        self.card_refs.clear()
        self._all_cards_loaded = False

        if not self.filtered_champions:
            tk.Label(self.container, text="No champions found.\nPress Reload.", fg=TEXT, bg=BG, font=FONT_TEXT).pack(pady=50)
            return

        sorted_champs = sorted(
            self.filtered_champions.keys(),
            key=lambda c: (c not in self.favorite_champs, c.lower())
        )

        width = max(1, self.canvas.winfo_width())
        card_width = 360
        self._cols = max(1, width // card_width)

        row = col = 0
        for champ in sorted_champs:
            card = tk.Frame(self.container, bg=CARD, width=340, height=250, relief="raised", bd=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            card.grid_propagate(False)

            placeholder = tk.Label(card, bg=PLACEHOLDER_COLOR)
            placeholder.pack(pady=5, fill="both", expand=True)

            lbl = tk.Label(card, bg=CARD)
            lbl.pack()

            tk.Label(card, text=champ, fg=TEXT, bg=CARD, font=FONT_TEXT).pack()

            btn_frame = tk.Frame(card, bg=CARD)
            btn_frame.pack(pady=5)

            open_btn = tk.Button(btn_frame, text="Open Skins", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON,
                                 command=lambda c=champ: self.open_skin(c))
            open_btn.pack(side="left", padx=(0,5))

            fav_btn = tk.Button(btn_frame, text="★" if champ in self.favorite_champs else "☆",
                                bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON)
            fav_btn.config(command=lambda c=champ, b=fav_btn: self.toggle_favorite(c,b))
            fav_btn.pack(side="left")

            card_obj = ChampionCard(champ, card, lbl, fav_btn)
            self.card_refs[champ] = card_obj

            col += 1
            if col >= self._cols:
                col = 0
                row += 1

        self.start_lazy_loading()

    # ---------------- LAZY LOAD ----------------
    def start_lazy_loading(self):
        """Start lazy loading with scroll binding"""
        if self._lazy_load_job:
            self.after_cancel(self._lazy_load_job)
        self.lazy_load_visible_cards()

    def lazy_load_visible_cards(self):
        """Load only visible cards efficiently"""
        if not self.card_refs:
            return
            
        canvas_top = self.canvas.canvasy(0)
        canvas_bottom = canvas_top + self.canvas.winfo_height()
        
        # Buffer zone for preloading cards slightly outside viewport
        buffer = 300
        load_top = max(0, canvas_top - buffer)
        load_bottom = canvas_bottom + buffer

        cards_to_load = []
        for champ, card_obj in self.card_refs.items():
            if card_obj.image_loaded:
                continue
            
            frame_top = card_obj.frame.winfo_y()
            frame_bottom = frame_top + card_obj.frame.winfo_height()
            
            # Only load if in viewport + buffer
            if frame_bottom >= load_top and frame_top <= load_bottom:
                cards_to_load.append(card_obj)

        # Start loading
        for card_obj in cards_to_load:
            card_obj.image_loaded = True
            threading.Thread(target=self.load_card_image, args=(card_obj,), daemon=True).start()

        # Check if all cards are loaded
        if all(card.image_loaded for card in self.card_refs.values()):
            self._all_cards_loaded = True
        else:
            # Schedule next check only if needed
            if self._lazy_load_job:
                self.after_cancel(self._lazy_load_job)
            self._lazy_load_job = self.after(300, self.lazy_load_visible_cards)

    # ---------------- LOAD CARD IMAGE ----------------
    def load_card_image(self, card_obj):
        champ = card_obj.name
        cache_key = champ
        try:
            if cache_key in self.card_image_cache:
                img = self.card_image_cache[cache_key]
            else:
                norm_name = HARDCODE_ASSET_MAP.get(champ, re.sub(r"[^A-Za-z0-9]", "", champ))
                pil_img = get_splash(norm_name, 0, size=(340,210))
                img = ImageTk.PhotoImage(pil_img)
                self.card_image_cache[cache_key] = img
        except Exception:
            img = tk.PhotoImage(width=340, height=210)

        def safe_set():
            if card_obj.lbl.winfo_exists():
                card_obj.placeholder.destroy()
                card_obj.lbl.config(image=img)
                card_obj.lbl.image = img

        self.after(0, safe_set)

    # ---------------- FAVORITES ----------------
    def toggle_favorite(self, champ, btn):
        if champ in self.favorite_champs:
            self.favorite_champs.remove(champ)
            btn.config(text="☆")
        else:
            self.favorite_champs.add(champ)
            btn.config(text="★")
        self.save_favorites()
        self.reorder_cards()

    def reorder_cards(self):
        """Reposition cards without rebuilding them"""
        sorted_champs = sorted(
            self.filtered_champions.keys(),
            key=lambda c: (c not in self.favorite_champs, c.lower())
        )
        width = max(1, self.canvas.winfo_width())
        card_width = 360
        new_cols = max(1, width // card_width)

        # Only rebuild if column count changed
        if new_cols != self._cols:
            self.render_cards()
            return

        row = col = 0
        for champ in sorted_champs:
            if champ in self.card_refs:
                card_obj = self.card_refs[champ]
                card_obj.frame.grid_configure(row=row, column=col)
                col += 1
                if col >= self._cols:
                    col = 0
                    row += 1

    # ---------------- FAVORITE PERSISTENCE ----------------
    def load_favorites(self):
        data = load_user_data()
        self.favorite_champs = set(data.get("favorites", []))

    def save_favorites(self):
        data = load_user_data()
        data["favorites"] = list(self.favorite_champs)
        save_user_data(data)

    # ---------------- ACTIONS ----------------
    def open_skin(self, champ):
        # Clean up before switching screens
        if self._lazy_load_job:
            try:
                self.after_cancel(self._lazy_load_job)
            except:
                pass
        self.grid_forget()
        skin_ui = SkinsUI(self.master, champ, self)
        skin_ui.grid(row=0, column=0, sticky="nsew")

    def go_back_to_landing(self):
        # Clean up before switching screens
        if self._lazy_load_job:
            try:
                self.after_cancel(self._lazy_load_job)
            except:
                pass
        self.grid_forget()
        self.landing_ui.grid(row=0, column=0, sticky="nsew")

    def delete_all_assets(self):
        if messagebox.askyesno("Delete ALL Assets", "Delete ALL downloaded assets?"):
            clear_assets()
            messagebox.showinfo("Done", "All assets deleted.")
            self.champions.clear()
            self.filtered_champions.clear()
            self.render_cards()
            self.reload_champions()

    def delete_skin_assets(self):
        if messagebox.askyesno("Delete Skin Assets", "Delete all skin assets?"):
            deleted_count = 0
            for filename in os.listdir(ASSETS_DIR):
                if re.match(r".+_\d+\.jpg$", filename) and not filename.endswith("_0.jpg"):
                    try:
                        os.remove(os.path.join(ASSETS_DIR, filename))
                        deleted_count += 1
                    except:
                        pass
            messagebox.showinfo("Done", f"Deleted {deleted_count} skin assets.")
            self.reload_champions()

    # ---------------- RELOAD CHAMPIONS ----------------
    def reload_champions(self):
        """Reload champions with overlay and ETA"""
        # Remove existing overlay
        if hasattr(self, 'loading_overlay') and self.loading_overlay.winfo_exists():
            self.loading_overlay.destroy()

        self.loading_overlay = tk.Frame(self.master, bg="black")
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        progress_bar = tk.Label(self.loading_overlay, bg=ACCENT)
        progress_bar.place(relx=0.05, rely=0.45, relwidth=0, relheight=0.03)

        progress_label = tk.Label(self.loading_overlay, text="Loading Champions...", fg=TEXT, bg="black", font=FONT_TEXT)
        progress_label.place(relx=0.5, rely=0.5, anchor="center")

        def progress(current, total, champ):
            pct = current / total
            self.after(0, lambda: [
                progress_bar.place_configure(relwidth=pct*0.9),
                progress_label.config(text=f"Loading Champions... {int(pct*100)}%")
            ])

        def done(success):
            def finish():
                if hasattr(self, 'loading_overlay') and self.loading_overlay.winfo_exists():
                    self.loading_overlay.destroy()
                if success:
                    self.load_and_render()
                else:
                    messagebox.showerror("Error","Failed to reload champions.")
            self.after(0, finish)

        threading.Thread(target=lambda: refresh_champions(progress, done), daemon=True).start()

    # ---------------- EVENTS ----------------
    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")
        
        # Trigger lazy loading on scroll
        if not self._all_cards_loaded:
            self.lazy_load_visible_cards()

    # ---------------- RESIZE ----------------
    def on_resize(self, event=None):
        new_width = self.canvas.winfo_width()
        if getattr(self, "_last_width", None) == new_width:
            return
        self._last_width = new_width
        self.canvas.itemconfig(self.window_id, width=new_width)
        
        # Debounce resize with longer delay
        if getattr(self, "_resize_job", None):
            try:
                self.after_cancel(self._resize_job)
            except:
                pass
        self._resize_job = self.after(400, self.reorder_cards)
