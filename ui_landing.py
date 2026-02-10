import tkinter as tk
from ui_champions import ChampionsUI
from theme import BG, ACCENT, TEXT, FONT_HEADER, FONT_BUTTON, APP_PADDING

class LandingUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG, padx=APP_PADDING, pady=APP_PADDING)
        self.master = master
        
        # Create the main UI and pass this landing_ui reference
        self.main_ui = ChampionsUI(master, landing_ui=self)
        
        self.build_layout()
    
    def build_layout(self):
        """Build the landing page layout"""
        # Center container
        center = tk.Frame(self, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = tk.Label(
            center, 
            text="League Randomizer", 
            fg=ACCENT, 
            bg=BG, 
            font=("Arial", 48, "bold")
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            center,
            text="Choose a champion and randomize their skins",
            fg=TEXT,
            bg=BG,
            font=("Arial", 14)
        )
        subtitle.pack(pady=(0, 30))
        
        # Button to go to main UI
        btn = tk.Button(
            center,
            text="Start",
            bg=ACCENT,
            fg="black",
            font=FONT_BUTTON,
            command=self.go_to_main,
            padx=40,
            pady=10
        )
        btn.pack(pady=10)
    
    def go_to_main(self):
        """Navigate to the main UI"""
        self.grid_forget()
        self.main_ui.grid(row=0, column=0, sticky="nsew")
