import tkinter as tk
from ui_champions import ChampionsUI
from theme import BG, ACCENT, TEXT, FONT_HEADER, FONT_BUTTON, APP_PADDING, CARD, BUTTON_BG, BUTTON_FG, BUTTON_PADY

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
