import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import bcrypt
import os

DB_NAME = "database.db"

def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """)
            conn.commit()

def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[0]):
            return True
        return False

def launch_login_gui(on_success):
    def handle_login():
        username = username_entry.get()
        password = password_entry.get()
        if login_user(username, password):
            status_label.config(text=f"Welcome back, {username}!", fg="#2ecc71")
            root.after(1000, lambda: [root.destroy(), on_success(username)])
        else:
            status_label.config(text="Invalid username or password.", fg="#e74c3c")

    def handle_register():
        username = username_entry.get()
        password = password_entry.get()
        if register_user(username, password):
            status_label.config(text="Registration successful. You can now login!", fg="#2ecc71")
        else:
            status_label.config(text="Username already exists.", fg="#e74c3c")

    root = tk.Tk()
    root.title("Smart Library Login")
    root.attributes('-fullscreen', True)
    root.configure(bg="#f0f2f5")

    # Main container with padding
    main_container = tk.Frame(root, bg="#f0f2f5", padx=40, pady=40)
    main_container.pack(expand=True, fill="both")

    # Title section with modern styling
    title_frame = tk.Frame(main_container, bg="#f0f2f5")
    title_frame.pack(pady=(0, 40))

    title = tk.Label(title_frame, 
                    text="A&Y Library",
                    font=("Segoe UI", 48, "bold"),
                    bg="#f0f2f5",
                    fg="#1a73e8")
    title.pack()

    subtitle = tk.Label(title_frame,
                       text="Your Gateway to Knowledge",
                       font=("Segoe UI", 18),
                       bg="#f0f2f5",
                       fg="#5f6368")
    subtitle.pack(pady=(10, 0))

    # Login form with modern card-like appearance
    form_frame = tk.Frame(main_container,
                         bg="white",
                         padx=40,
                         pady=30,
                         relief="flat",
                         highlightbackground="#dadce0",
                         highlightthickness=1)
    form_frame.pack(pady=20)

    # Form title
    form_title = tk.Label(form_frame,
                         text="Sign In",
                         font=("Segoe UI", 24, "bold"),
                         bg="white",
                         fg="#202124")
    form_title.pack(pady=(0, 20))

    # Username field
    username_frame = tk.Frame(form_frame, bg="white")
    username_frame.pack(fill="x", pady=(0, 15))
    
    tk.Label(username_frame,
            text="Username",
            font=("Segoe UI", 12),
            bg="white",
            fg="#5f6368").pack(anchor="w")
    
    username_entry = ttk.Entry(username_frame,
                             font=("Segoe UI", 12),
                             width=30)
    username_entry.pack(fill="x", pady=(5, 0))

    # Password field
    password_frame = tk.Frame(form_frame, bg="white")
    password_frame.pack(fill="x", pady=(0, 25))
    
    tk.Label(password_frame,
            text="Password",
            font=("Segoe UI", 12),
            bg="white",
            fg="#5f6368").pack(anchor="w")
    
    password_entry = ttk.Entry(password_frame,
                             font=("Segoe UI", 12),
                             show="•",
                             width=30)
    password_entry.pack(fill="x", pady=(5, 0))

    # Custom button style with rounded corners
    class RoundedButton(tk.Button):
        def __init__(self, master=None, radius=25, **kwargs):
            super().__init__(master, **kwargs)
            self.radius = radius
            self.configure(relief="flat", borderwidth=0)
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)

        def on_enter(self, e):
            self.configure(bg=self.hover_color)

        def on_leave(self, e):
            self.configure(bg=self.normal_color)

    # Buttons with modern styling and rounded corners
    button_frame = tk.Frame(form_frame, bg="white")
    button_frame.pack(fill="x", pady=(0, 20))

    # Login button
    login_btn = RoundedButton(
        button_frame,
        text="Login",
        command=handle_login,
        font=("Segoe UI", 11, "bold"),
        width=20,
        height=2,
        bg="#1a73e8",
        fg="white",
        cursor="hand2"
    )
    login_btn.normal_color = "#1a73e8"
    login_btn.hover_color = "#1557b0"
    login_btn.pack(side="left", padx=(0, 10))

    # Register button
    register_btn = RoundedButton(
        button_frame,
        text="Register",
        command=handle_register,
        font=("Segoe UI", 11, "bold"),
        width=20,
        height=2,
        bg="#34a853",
        fg="white",
        cursor="hand2"
    )
    register_btn.normal_color = "#34a853"
    register_btn.hover_color = "#2d9249"
    register_btn.pack(side="left", padx=10)

    # Exit button
    exit_btn = RoundedButton(
        button_frame,
        text="Exit",
        command=root.destroy,
        font=("Segoe UI", 11, "bold"),
        width=20,
        height=2,
        bg="#ea4335",
        fg="white",
        cursor="hand2"
    )
    exit_btn.normal_color = "#ea4335"
    exit_btn.hover_color = "#d33426"
    exit_btn.pack(side="left", padx=10)

    # Status label with modern styling
    status_label = tk.Label(main_container,
                           text="",
                           font=("Segoe UI", 12),
                           bg="#f0f2f5",
                           pady=10)
    status_label.pack()

    # Configure ttk styles
    style = ttk.Style()
    style.configure("TEntry",
                   padding=10,
                   relief="flat",
                   borderwidth=1)

    # Bind Enter key to login
    root.bind('<Return>', lambda e: handle_login())

    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

# Initialize DB
init_db()
