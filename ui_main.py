import tkinter as tk
from tkinter import messagebox
from data_manager import load_champions, refresh_champions, load_user_data, save_user_data
from assets_manager import get_splash, clear_assets, ASSETS_DIR
from ui_skin import SkinUI
import threading
import re
import os

BG = "#0A1428"
CARD = "#1F2933"
TEXT = "#E5E7EB"
ACCENT = "#C89B3C"
PLACEHOLDER_COLOR = "#1F2933"

# Hardcoded mapping for tricky champions
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
    """Wrapper for each champion card widgets"""
    def __init__(self, champ_name, frame, lbl, fav_btn):
        self.name = champ_name
        self.frame = frame
        self.lbl = lbl
        self.fav_btn = fav_btn
        self.image_loaded = False
        self.placeholder = frame.children['!label']

class MainUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.master = master

        self.champions = {}
        self.filtered_champions = {}
        self.card_refs = {}  # champ_name -> ChampionCard
        self.favorite_champs = set()
        self._last_width = None
        self._resize_job = None

        self.build_header()
        self.build_canvas()
        self.load_favorites()
        
        # Load champions or show first-start overlay
        if not load_champions():
            self.show_first_start_overlay()
        else:
            self.load_and_render()

        self.master.bind("<Configure>", self.on_resize)

    # ---------------- HEADER ----------------
    def build_header(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=5)

        tk.Label(top, text="Choose your Champion", fg=ACCENT, bg=BG, font=("Segoe UI", 20, "bold")).pack(side="left", padx=10)

        # Frame for buttons + search
        btn_frame = tk.Frame(top, bg=BG)
        btn_frame.pack(side="right", padx=10)

        btn_delete_skins = tk.Button(btn_frame, text="🗑 Delete Skin Assets", command=self.delete_skin_assets, bg=ACCENT, fg="black")
        btn_delete_skins.pack(side="right", padx=5)

        btn_delete_all = tk.Button(btn_frame, text="🗑 Delete ALL Assets", command=self.delete_all_assets, bg=ACCENT, fg="black")
        btn_delete_all.pack(side="right", padx=5)

        btn_refresh = tk.Button(btn_frame, text="🔄 Refresh Champions", command=self.refresh_prompt, bg=ACCENT, fg="black")
        btn_refresh.pack(side="right", padx=5)

        # Search bar
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.apply_search_filter)
        search_entry = tk.Entry(btn_frame, textvariable=self.search_var, font=("Segoe UI", 12))
        search_entry.pack(side="right", padx=(5,5))

    # ---------------- CANVAS ----------------
    def build_canvas(self):
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.container = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0,0), window=self.container, anchor="nw")
        self.container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Scroll binding
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self.on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)

    # ---------------- DATA ----------------
    def load_and_render(self):
        """Load champions in a separate thread"""
        def load():
            self.champions = load_champions()
            self.filtered_champions = dict(self.champions)
            self.after(0, self.render_cards)
        threading.Thread(target=load, daemon=True).start()

    # ---------------- SEARCH ----------------
    def apply_search_filter(self, *args):
        query = self.search_var.get().lower()
        self.filtered_champions = {
            champ: data for champ, data in self.champions.items()
            if query in champ.lower()
        }
        self.reorder_cards()

    # ---------------- RENDER CARDS ----------------
    def render_cards(self):
        for w in self.container.winfo_children():
            w.destroy()
        self.card_refs.clear()

        if not self.filtered_champions:
            tk.Label(self.container, text="No champions found.\nPress Refresh.", fg=TEXT, bg=BG, font=("Segoe UI",14)).pack(pady=50)
            return

        # Sort champions: favorites first
        sorted_champs = sorted(
            self.filtered_champions.keys(),
            key=lambda c: (c not in self.favorite_champs, c.lower())
        )

        width = max(1, self.canvas.winfo_width())
        card_width = 360
        cols = max(1, width // card_width)

        row = col = 0
        for champ in sorted_champs:
            card = tk.Frame(self.container, bg=CARD, width=340, height=250)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            card.grid_propagate(False)

            placeholder = tk.Label(card, bg=PLACEHOLDER_COLOR)
            placeholder.pack(pady=5, fill="both", expand=True)

            lbl = tk.Label(card, bg=CARD)
            lbl.pack()

            tk.Label(card, text=champ, fg=TEXT, bg=CARD, font=("Segoe UI",13,"bold")).pack()

            btn_frame = tk.Frame(card, bg=CARD)
            btn_frame.pack(pady=5)

            open_btn = tk.Button(btn_frame, text="Open Skins", bg=ACCENT, fg="black", command=lambda c=champ: self.open_skin(c))
            open_btn.pack(side="left", padx=(0,5))

            fav_btn = tk.Button(btn_frame, text="★" if champ in self.favorite_champs else "☆", bg=ACCENT, fg="black")
            fav_btn.config(command=lambda c=champ, b=fav_btn: self.toggle_favorite(c, b))
            fav_btn.pack(side="left")

            card_obj = ChampionCard(champ, card, lbl, fav_btn)
            self.card_refs[champ] = card_obj

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Start lazy-loading visible images
        self.after(100, self.lazy_load_visible_cards)

    # ---------------- LAZY LOAD ----------------
    def lazy_load_visible_cards(self):
        canvas_top = self.canvas.canvasy(0)
        canvas_bottom = canvas_top + self.canvas.winfo_height()

        for champ, card_obj in self.card_refs.items():
            frame_top = card_obj.frame.winfo_y()
            frame_bottom = frame_top + card_obj.frame.winfo_height()
            if frame_bottom >= canvas_top and frame_top <= canvas_bottom:
                if not card_obj.image_loaded:
                    card_obj.image_loaded = True
                    threading.Thread(target=self.load_card_image, args=(card_obj,), daemon=True).start()
        self.after(200, self.lazy_load_visible_cards)

    def load_card_image(self, card_obj):
        champ = card_obj.name
        try:
            norm_name = HARDCODE_ASSET_MAP.get(champ, re.sub(r"[^A-Za-z0-9]","",champ))
            img = get_splash(norm_name,0)
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
        """Reorder the card frames to show favorites on top without destroying them"""
        sorted_champs = sorted(
            self.filtered_champions.keys(),
            key=lambda c: (c not in self.favorite_champs, c.lower())
        )
        width = max(1, self.canvas.winfo_width())
        card_width = 360
        cols = max(1, width // card_width)

        row = col = 0
        for champ in sorted_champs:
            card_obj = self.card_refs[champ]
            card_obj.frame.grid_configure(row=row, column=col)
            col += 1
            if col >= cols:
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
        self.grid_forget()
        skin_ui = SkinUI(self.master, champ, self)
        skin_ui.grid(row=0, column=0, sticky="nsew")

    def delete_all_assets(self):
        if messagebox.askyesno("Delete ALL Assets", "Delete ALL downloaded assets?"):
            clear_assets()
            messagebox.showinfo("Done", "All assets deleted.")
            self.champions.clear()
            self.filtered_champions.clear()
            self.render_cards()
            self.show_first_start_overlay()

    def delete_skin_assets(self):
        if messagebox.askyesno("Delete Skin Assets", "Delete all skin assets?"):
            deleted_count = 0
            for filename in os.listdir(ASSETS_DIR):
                if re.match(r".+_\d+\.jpg$", filename) and not filename.endswith("_0.jpg"):
                    try:
                        os.remove(os.path.join(ASSETS_DIR, filename))
                        deleted_count += 1
                    except Exception:
                        pass
            messagebox.showinfo("Done", f"Deleted {deleted_count} skin assets.")
            self.load_and_render()

    # ---------------- REFRESH ----------------
    def refresh_prompt(self):
        if not messagebox.askyesno("Refresh champions", "This will download champion & skin data.\nContinue?"):
            return
        def progress(current,total,champ):
            self.update_idletasks()
        def done(success):
            if success:
                self.load_and_render()
            else:
                messagebox.showerror("Error","Refresh failed.")
        refresh_champions(progress,done)

    # ---------------- FIRST START ----------------
    def show_first_start_overlay(self):
        self.overlay = tk.Frame(self, bg="#000000")
        self.overlay.place(relx=0,rely=0,relwidth=1,relheight=1)
        lbl = tk.Label(self.overlay,text="No champions found.\nPress the button below to load them for the first time.",
                       fg="white",bg="#000000",font=("Segoe UI",16,"bold"),justify="center")
        lbl.pack(pady=30)
        btn = tk.Button(self.overlay,text="🔄 Load Champions",bg=ACCENT,fg="black",
                        font=("Segoe UI",14,"bold"),command=self.first_start_refresh)
        btn.pack(pady=20)

    def first_start_refresh(self):
        self.overlay.destroy()
        def progress(current,total,champ): self.update_idletasks()
        def done(success):
            if success: self.load_and_render()
            else:
                messagebox.showerror("Error","Failed to download champions. Try again.")
                self.show_first_start_overlay()
        refresh_champions(progress,done)

    # ---------------- EVENTS ----------------
    def on_mousewheel(self,event):
        if event.delta: self.canvas.yview_scroll(int(-1*(event.delta/120)),"units")
        elif event.num==4: self.canvas.yview_scroll(-3,"units")
        elif event.num==5: self.canvas.yview_scroll(3,"units")

    # ---------------- RESIZE ----------------
    def on_resize(self,event=None):
        new_width = self.canvas.winfo_width()
        if getattr(self,"_last_width",None)==new_width: return
        self._last_width = new_width
        self.canvas.itemconfig(self.window_id,width=new_width)
        if getattr(self,"_resize_job",None):
            try: self.after_cancel(self._resize_job)
            except Exception: pass
        self._resize_job = self.after(120,self.render_cards)
