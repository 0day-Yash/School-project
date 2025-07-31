import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import bcrypt
from db_init import init_db, DB_NAME

def register_user(username, password, is_admin=0):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)", (username, hashed, is_admin))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT password_hash, is_admin FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            if row and bcrypt.checkpw(password.encode(), row[0]):
                return True, row[1]
            return False, 0
    except sqlite3.Error:
        return False, 0

def launch_login_gui(on_success):
    def handle_login():
        username = username_entry.get()
        password = password_entry.get()
        success, is_admin = login_user(username, password)
        if success:
            status_label.config(text=f"Welcome back, {username}!", fg="#2ecc71")
            root.after(1000, lambda: [root.destroy(), on_success(username, is_admin)])
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
    root.title("A&Y Library Login")
    root.attributes('-fullscreen', True)
    root.configure(bg="#f0f2f5")

    main_container = tk.Frame(root, bg="#f0f2f5", padx=40, pady=40)
    main_container.pack(expand=True, fill="both")

    title_frame = tk.Frame(main_container, bg="#f0f2f5")
    title_frame.pack(pady=(0, 40))

    title = tk.Label(title_frame, text="A&Y Library", font=("Segoe UI", 48, "bold"), bg="#f0f2f5", fg="#1a73e8")
    title.pack()

    subtitle = tk.Label(title_frame, text="Your Gateway to Knowledge", font=("Segoe UI", 18), bg="#f0f2f5", fg="#5f6368")
    subtitle.pack(pady=(10, 0))

    form_frame = tk.Frame(main_container, bg="white", padx=40, pady=30, relief="flat", highlightbackground="#dadce0", highlightthickness=1)
    form_frame.pack(pady=20)

    form_title = tk.Label(form_frame, text="Sign In", font=("Segoe UI", 24, "bold"), bg="white", fg="#202124")
    form_title.pack(pady=(0, 20))

    username_frame = tk.Frame(form_frame, bg="white")
    username_frame.pack(fill="x", pady=(0, 15))
    tk.Label(username_frame, text="Username", font=("Segoe UI", 12), bg="white", fg="#5f6368").pack(anchor="w")
    username_entry = ttk.Entry(username_frame, font=("Segoe UI", 12), width=30)
    username_entry.pack(fill="x", pady=(5, 0))

    password_frame = tk.Frame(form_frame, bg="white")
    password_frame.pack(fill="x", pady=(0, 25))
    tk.Label(password_frame, text="Password", font=("Segoe UI", 12), bg="white", fg="#5f6368").pack(anchor="w")
    password_entry = ttk.Entry(password_frame, font=("Segoe UI", 12), show="•", width=30)
    password_entry.pack(fill="x", pady=(5, 0))

    button_frame = tk.Frame(form_frame, bg="white")
    button_frame.pack(fill="x", pady=(0, 20))

    login_btn = tk.Button(button_frame, text="Login", command=handle_login, font=("Segoe UI", 11, "bold"), width=20, height=2, bg="#1a73e8", fg="white", cursor="hand2", relief="flat")
    login_btn.pack(side="left", padx=(0, 10))
    login_btn.bind("<Enter>", lambda e: login_btn.configure(bg="#1557b0"))
    login_btn.bind("<Leave>", lambda e: login_btn.configure(bg="#1a73e8"))

    register_btn = tk.Button(button_frame, text="Register", command=handle_register, font=("Segoe UI", 11, "bold"), width=20, height=2, bg="#34a853", fg="white", cursor="hand2", relief="flat")
    register_btn.pack(side="left", padx=10)
    register_btn.bind("<Enter>", lambda e: register_btn.configure(bg="#2d9249"))
    register_btn.bind("<Leave>", lambda e: register_btn.configure(bg="#34a853"))

    exit_btn = tk.Button(button_frame, text="Exit", command=root.destroy, font=("Segoe UI", 11, "bold"), width=20, height=2, bg="#ea4335", fg="white", cursor="hand2", relief="flat")
    exit_btn.pack(side="left", padx=10)
    exit_btn.bind("<Enter>", lambda e: exit_btn.configure(bg="#d33426"))
    exit_btn.bind("<Leave>", lambda e: exit_btn.configure(bg="#ea4335"))

    status_label = tk.Label(main_container, text="", font=("Segoe UI", 12), bg="#f0f2f5", pady=10)
    status_label.pack()

    style = ttk.Style()
    style.configure("TEntry", padding=10, relief="flat", borderwidth=1)

    root.bind('<Return>', lambda e: handle_login())
    root.mainloop()

if __name__ == "__main__":
    init_db()
    launch_login_gui(lambda username, is_admin: print(f"Logged in as {username}, Admin: {is_admin}"))