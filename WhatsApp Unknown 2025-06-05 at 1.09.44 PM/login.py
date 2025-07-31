import tkinter as tk
from tkinter import messagebox
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
            status_label.config(text=f"Welcome back, {username}!", fg="green")
            root.after(1000, lambda: [root.destroy(), on_success(username)])
        else:
            status_label.config(text="Invalid username or password.", fg="red")

    def handle_register():
        username = username_entry.get()
        password = password_entry.get()
        if register_user(username, password):
            status_label.config(text="Registration successful. You can now login!", fg="green")
        else:
            status_label.config(text="Username already exists.", fg="red")

    root = tk.Tk()
    root.title("Smart Library Login")
    root.attributes('-fullscreen', True)
    root.configure(bg="green")

    # Title
    title = tk.Label(root, text="Welcome to A&Y Library ",font=("Helvetica", 52, "bold"), bg="green", fg="red")
    title.pack(pady=40)

    subtitle = tk.Label(root, text="Please login or register to continue", font=("Helvetica", 18,"bold"), bg="green", fg="white")
    subtitle.pack(pady=10)

    # Form
    form_frame = tk.Frame(root, bg="green")
    form_frame.pack(pady=20)

    tk.Label(form_frame, text="Username:", font=("Helvetica", 16), bg="green",fg="tan").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    username_entry = tk.Entry(form_frame, font=("Helvetica", 16), width=25)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Password:", font=("Helvetica", 16), bg="green",fg="tan").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    password_entry = tk.Entry(form_frame, font=("Helvetica", 16), show="*", width=25)
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Buttons
    button_frame = tk.Frame(root, bg="green")
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Login", command=handle_login, font=("Helvetica", 14), width=15, bg="#4CAF50", fg="green").grid(row=0, column=0, padx=20)
    tk.Button(button_frame, text="Register", command=handle_register, font=("Helvetica", 14), width=15, bg="#2196F3", fg="green").grid(row=0, column=1, padx=20)
    tk.Button(button_frame, text="Exit", command=root.destroy, font=("Helvetica", 14), width=15, bg="#f44336", fg="green").grid(row=0, column=2, padx=20)

    # Status label
    status_label = tk.Label(root, text="", font=("Helvetica", 14), bg="green")
    status_label.pack(pady=10)

    root.mainloop()

# Initialize DB
init_db()
