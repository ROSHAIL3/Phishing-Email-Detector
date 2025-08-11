import tkinter as tk
from tkinter import messagebox

from src.login import show_login
from src.gui import show_main_gui

def start_app():
    root = tk.Tk()
    root.title("SecureMail")
    root.geometry("960x680")

    def go_main():
        show_main_gui(root)

    show_login(root, on_success=go_main)
    root.mainloop()

if __name__ == "__main__":
    try:
        start_app()
    except Exception as e:
        # Basic guard so the app doesn't crash silently
        messagebox.showerror("Application Error", str(e))
        raise
