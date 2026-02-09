import tkinter as tk
from tkinter import messagebox
from data_manager import load_champions, refresh_champions
from assets_manager import get_splash, clear_assets
from ui_skin import SkinUI

BG = "#0A1428"
CARD = "#1F2933"
TEXT = "#E5E7EB"
ACCENT = "#C89B3C"


class MainUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.master = master

        self.champions = {}
        self.card_refs = []

        self._last_width = None
        self._resize_job = None

        self.build_header()
        self.build_canvas()
        self.load_and_render()

        self.master.bind("<Configure>", self.on_resize)

    # ---------------- HEADER ----------------
    def build_header(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=5)

        tk.Label(
            top,
            text="Choose your Champion",
            fg=ACCENT,
            bg=BG,
            font=("Segoe UI", 20, "bold"),
        ).pack(side="left", padx=10)

        tk.Button(
            top,
            text="🔄 Refresh champions",
            command=self.refresh_prompt,
            bg=ACCENT,
            fg="black",
        ).pack(side="right", padx=5)

        tk.Button(
            top,
            text="🗑 Delete assets",
            command=self.delete_assets,
            bg=ACCENT,
            fg="black",
        ).pack(side="right", padx=5)

    # ---------------- CANVAS ----------------
    def build_canvas(self):
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.container = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window(
            (0, 0), window=self.container, anchor="nw"
        )

        self.container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    # ---------------- DATA ----------------
    def load_and_render(self):
        self.champions = load_champions()
        self.render_cards()

    # ---------------- RENDER ----------------
    def render_cards(self):
        if not self.winfo_ismapped():
            return

        for w in self.container.winfo_children():
            w.destroy()
        self.card_refs.clear()

        if not self.champions:
            tk.Label(
                self.container,
                text="No champions found.\nPress Refresh.",
                fg=TEXT,
                bg=BG,
                font=("Segoe UI", 14),
            ).pack(pady=50)
            return

        width = max(1, self.canvas.winfo_width())
        card_width = 360
        cols = max(1, width // card_width)

        row = col = 0
        for champ in sorted(self.champions.keys()):
            card = tk.Frame(self.container, bg=CARD, width=340, height=250)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            card.grid_propagate(False)

            img = get_splash(champ, 0)
            lbl = tk.Label(card, image=img, bg=CARD)
            lbl.image = img
            lbl.pack(pady=5)

            tk.Label(
                card,
                text=champ,
                fg=TEXT,
                bg=CARD,
                font=("Segoe UI", 13, "bold"),
            ).pack()

            tk.Button(
                card,
                text="Open Skins",
                bg=ACCENT,
                fg="black",
                command=lambda c=champ: self.open_skin(c),
            ).pack(pady=5)

            self.card_refs.append(lbl)

            col += 1
            if col >= cols:
                col = 0
                row += 1

    # ---------------- ACTIONS ----------------
    def open_skin(self, champ):
        self.grid_forget()  # grid used on root
        skin_ui = SkinUI(self.master, champ, self)
        skin_ui.grid(row=0, column=0, sticky="nsew")

    def delete_assets(self):
        if messagebox.askyesno("Delete assets", "Delete all downloaded images?"):
            clear_assets()
            messagebox.showinfo("Done", "Assets deleted.")

    def refresh_prompt(self):
        if not messagebox.askyesno(
            "Refresh champions",
            "This will download champion & skin data.\nContinue?",
        ):
            return

        self.show_overlay("Refreshing champions…")

        def progress(current, total, champ):
            percent = int((current / total) * 100)
            self.overlay_label.config(
                text=f"Downloading {champ}\n{percent}%"
            )
            self.update_idletasks()

        def done(success):
            self.hide_overlay()
            if success:
                self.load_and_render()
            else:
                messagebox.showerror("Error", "Refresh failed.")

        refresh_champions(progress, done)

    # ---------------- OVERLAY ----------------
    def show_overlay(self, text):
        self.overlay = tk.Frame(self, bg="#000000")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.overlay_label = tk.Label(
            self.overlay,
            text=text,
            fg=TEXT,
            bg="#000000",
            font=("Segoe UI", 16, "bold"),
        )
        self.overlay_label.place(relx=0.5, rely=0.5, anchor="center")

    def hide_overlay(self):
        if hasattr(self, "overlay"):
            self.overlay.destroy()

    # ---------------- EVENTS ----------------
    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")

    def on_resize(self, event=None):
        new_width = self.canvas.winfo_width()
        if getattr(self, "_last_width", None) == new_width:
            return

        self._last_width = new_width
        self.canvas.itemconfig(self.window_id, width=new_width)

        if getattr(self, "_resize_job", None):
            try:
                self.after_cancel(self._resize_job)
            except Exception:
                pass
        self._resize_job = self.after(120, self.render_cards)
