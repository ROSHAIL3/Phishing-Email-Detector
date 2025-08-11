import tkinter as tk
from tkinter import ttk, messagebox

# Simple demo credentials; replace with a file-based store if you prefer.
DEMO_USER = "admin"
DEMO_PASS = "1234"

def show_login(root: tk.Tk, on_success):
    # Clear root
    for w in root.winfo_children():
        w.destroy()

    root.title("SecureMail Login")

    container = ttk.Frame(root, padding=24)
    container.pack(fill="both", expand=True)

    title = ttk.Label(container, text="Welcome to Phishing Email Detector", font=("Segoe UI", 16, "bold"))
    title.pack(pady=(0, 16))

    form = ttk.Frame(container)
    form.pack()

    ttk.Label(form, text="Username").grid(row=0, column=0, sticky="e", padx=8, pady=6)
    username = ttk.Entry(form, width=28)
    username.grid(row=0, column=1, pady=6)

    ttk.Label(form, text="Password").grid(row=1, column=0, sticky="e", padx=8, pady=6)
    password = ttk.Entry(form, width=28, show="*")
    password.grid(row=1, column=1, pady=6)

    def do_login(event=None):
        if username.get() == DEMO_USER and password.get() == DEMO_PASS:
            on_success()
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")

    login_btn = ttk.Button(container, text="Login", command=do_login)
    login_btn.pack(pady=12)

    # Enter to submit
    root.bind("<Return>", do_login)

    # Focus
    username.focus_set()
