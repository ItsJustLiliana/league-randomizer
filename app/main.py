import ctypes
import sys
import tkinter as tk
from ui_landing import LandingUI
from data_manager import ensure_files

APP_BG = "#0A1428"


def remove_maximize_button(window):
    if sys.platform != "win32":
        return

    window.update_idletasks()

    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    g_wl_style = -16
    ws_maximizebox = 0x00010000
    ws_thickframe = 0x00040000

    style = ctypes.windll.user32.GetWindowLongW(hwnd, g_wl_style)
    style &= ~ws_maximizebox
    style &= ~ws_thickframe
    ctypes.windll.user32.SetWindowLongW(hwnd, g_wl_style, style)

    swp_nosize = 0x0001
    swp_nomove = 0x0002
    swp_nozorder = 0x0004
    swp_framechanged = 0x0020
    ctypes.windll.user32.SetWindowPos(
        hwnd,
        0,
        0,
        0,
        0,
        0,
        swp_nosize | swp_nomove | swp_nozorder | swp_framechanged,
    )

def main():
    ensure_files()

    root = tk.Tk()
    root.title("League Randomizer")
    root.geometry("1140x720")
    root.minsize(1140, 720)
    root.maxsize(1140, 720)
    root.configure(bg=APP_BG)
    remove_maximize_button(root)

    # Improve resize performance
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    app = LandingUI(root)
    app.grid(row=0, column=0, sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    main()
