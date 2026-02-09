import tkinter as tk
from ui_main import MainUI
from data_manager import ensure_files

APP_BG = "#0A1428"

def main():
    # Ensure JSON files exist before UI starts
    ensure_files()

    root = tk.Tk()
    root.title("League Randomizer")
    root.geometry("1140x730")   # <-- wider default window
    root.minsize(1100, 650)
    root.configure(bg=APP_BG)

    # Improve resize performance
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    app = MainUI(root)
    app.grid(row=0, column=0, sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    main()
