import tkinter as tk
from ui_champions import ChampionsUI
from theme import BG, ACCENT, TEXT, FONT_HEADER, FONT_BUTTON, APP_PADDING, CARD, BUTTON_BG, BUTTON_FG, BUTTON_PADY

# Credits - easily editable
CREDITS = [
    ("Assets", "Riot Games (Champion Splash Arts)"),
    ("Data", "Data Dragon API"),
    ("", ""),  # Empty line for spacing
    ("Developer", "ItsJustLiliana"),
]

class LandingUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG, padx=APP_PADDING, pady=APP_PADDING)
        self.master = master
        self.main_ui = None  # Create on demand
        
        self.build_layout()
    
    def build_layout(self):
        """Build the landing page layout"""
        # Title
        title = tk.Label(
            self, 
            text="League Randomizer", 
            fg=ACCENT, 
            bg=BG, 
            font=("Arial", 48, "bold")
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            self,
            text="Choose a feature to get started",
            fg=TEXT,
            bg=BG,
            font=("Arial", 14)
        )
        subtitle.pack(pady=(0, 40))
        
        # Cards container
        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack(pady=30)
        
        # Card 1: Skin Randomizer
        card1 = tk.Frame(cards_frame, bg=CARD, width=280, height=200, relief="raised", bd=1)
        card1.pack(side="left", padx=20)
        card1.pack_propagate(False)
        
        tk.Label(card1, text="🎲", fg=ACCENT, bg=CARD, font=("Arial", 40)).pack(pady=10)
        tk.Label(card1, text="Skin Randomizer", fg=ACCENT, bg=CARD, font=("Arial", 16, "bold")).pack()
        tk.Label(card1, text="Randomize champion skins", fg=TEXT, bg=CARD, font=("Arial", 11)).pack(pady=(5, 15))
        tk.Button(card1, text="Open", bg=ACCENT, fg="black", font=FONT_BUTTON, 
                  command=self.go_to_main).pack(pady=(0, BUTTON_PADY))
        
        # Card 2: Coming Soon
        card2 = tk.Frame(cards_frame, bg=CARD, width=280, height=200, relief="raised", bd=1)
        card2.pack(side="left", padx=20)
        card2.pack_propagate(False)
        
        tk.Label(card2, text="⭐", fg=ACCENT, bg=CARD, font=("Arial", 40)).pack(pady=10)
        tk.Label(card2, text="Coming Soon", fg=ACCENT, bg=CARD, font=("Arial", 16, "bold")).pack()
        tk.Label(card2, text="Feature coming soon...", fg=TEXT, bg=CARD, font=("Arial", 11)).pack(pady=(5, 15))
        tk.Button(card2, text="Soon", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, state="disabled").pack(pady=(0, BUTTON_PADY))
        
        # Card 3: Coming Soon
        card3 = tk.Frame(cards_frame, bg=CARD, width=280, height=200, relief="raised", bd=1)
        card3.pack(side="left", padx=20)
        card3.pack_propagate(False)
        
        tk.Label(card3, text="🚀", fg=ACCENT, bg=CARD, font=("Arial", 40)).pack(pady=10)
        tk.Label(card3, text="Coming Soon", fg=ACCENT, bg=CARD, font=("Arial", 16, "bold")).pack()
        tk.Label(card3, text="Feature coming soon...", fg=TEXT, bg=CARD, font=("Arial", 11)).pack(pady=(5, 15))
        tk.Button(card3, text="Soon", bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BUTTON, state="disabled").pack(pady=(0, BUTTON_PADY))
        
        # Bottom bar with credits button
        bottom_frame = tk.Frame(self, bg=BG)
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Button(
            bottom_frame, 
            text="Credits", 
            bg=BUTTON_BG, 
            fg=BUTTON_FG, 
            font=("Segoe UI", 10), 
            command=self.show_credits
        ).pack(side="right", padx=10)
    
    def go_to_main(self):
        """Navigate to the main UI"""
        # Create ChampionsUI on demand
        if self.main_ui is None:
            self.main_ui = ChampionsUI(self.master, landing_ui=self)
        
        self.grid_forget()
        self.main_ui.grid(row=0, column=0, sticky="nsew")
    
    def show_landing(self):
        """Show landing page and clean up ChampionsUI"""
        if self.main_ui is not None:
            # Destroy the old ChampionsUI to free up resources
            self.main_ui.grid_forget()
            self.main_ui.destroy()
            self.main_ui = None
        
        self.grid(row=0, column=0, sticky="nsew")
    
    def show_credits(self):
        """Display credits in a modal window"""
        credits_window = tk.Toplevel(self)
        credits_window.title("Credits")
        credits_window.geometry("500x400")
        credits_window.configure(bg=BG)
        credits_window.resizable(False, False)
        
        # Center the window
        credits_window.transient(self.master)
        credits_window.grab_set()
        
        # Title
        title = tk.Label(
            credits_window, 
            text="Credits", 
            fg=ACCENT, 
            bg=BG, 
            font=("Arial", 24, "bold")
        )
        title.pack(pady=15)
        
        # Scrollable frame for credits
        canvas = tk.Canvas(credits_window, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(credits_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add credits entries
        for title_text, description in CREDITS:
            entry_frame = tk.Frame(scrollable_frame, bg=BG)
            entry_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(
                entry_frame,
                text=title_text,
                fg=ACCENT,
                bg=BG,
                font=("Arial", 12, "bold")
            ).pack(anchor="w")
            
            tk.Label(
                entry_frame,
                text=description,
                fg=TEXT,
                bg=BG,
                font=("Arial", 10),
                wraplength=400,
                justify="left"
            ).pack(anchor="w", pady=(2, 0))
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
