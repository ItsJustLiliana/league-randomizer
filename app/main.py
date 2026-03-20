import tkinter as tk
from ui_landing import LandingUI
from data_manager import ensure_files

APP_BG = "#0A1428"

def main():
    ensure_files()

    root = tk.Tk()
    root.title("League Randomizer")
    root.geometry("1140x720")
    root.minsize(1140, 720)
    root.maxsize(1140, 720)
    root.configure(bg=APP_BG)

    # Improve resize performance
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    app = LandingUI(root)
    app.grid(row=0, column=0, sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    main()
