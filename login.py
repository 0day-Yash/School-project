import logging
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import bcrypt
from db_init import init_db, DB_NAME
import os
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

def register_user(username, password, is_admin=0):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)", (username, hashed, is_admin))
            conn.commit()
            logger.info("Registered user %s admin=%s", username, is_admin)
            return True
    except sqlite3.IntegrityError:
        logger.warning("Attempt to register duplicate username %s", username)
        return False

def login_user(username, password):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT password_hash, is_admin FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            if row and bcrypt.checkpw(password.encode(), row[0]):
                logger.info("User %s logged in (admin=%s)", username, row[1])
                return True, row[1]
            logger.info("Failed login attempt for user %s", username)
            return False, 0
    except sqlite3.Error as e:
        logger.exception("Database error during login for %s: %s", username, e)
        return False, 0

def launch_login_gui(on_success):
    def handle_login():
        username = username_entry.get().strip()
        password = password_entry.get()
        
        # Validate input
        if not username or not password:
            status_label.config(text="Please enter both username and password.", fg="#e74c3c")
            return
        
        success, is_admin = login_user(username, password)
        if success:
            status_label.config(text=f"Welcome back, {username}!", fg="#2ecc71")
            # Disable buttons to prevent double-clicks
            login_btn.config(state="disabled")
            register_btn.config(state="disabled")
            root.after(1000, lambda: [root.destroy(), on_success(username, is_admin)])
        else:
            status_label.config(text="Invalid username or password.", fg="#e74c3c")
            password_entry.delete(0, tk.END)
            password_entry.focus()

    def handle_register():
        username = username_entry.get().strip()
        password = password_entry.get()
        
        # Validate input
        if not username or not password:
            status_label.config(text="Please enter both username and password.", fg="#e74c3c")
            return
        
        if len(username) < 3:
            status_label.config(text="Username must be at least 3 characters.", fg="#e74c3c")
            return
        
        if len(password) < 6:
            status_label.config(text="Password must be at least 6 characters.", fg="#e74c3c")
            return
        
        if register_user(username, password):
            status_label.config(text="Registration successful! Please login.", fg="#2ecc71")
            password_entry.delete(0, tk.END)
            username_entry.focus()
        else:
            status_label.config(text="Username already exists. Try another.", fg="#e74c3c")

    def toggle_password():
        if password_entry.cget('show') == '•':
            password_entry.config(show='')
            toggle_btn.config(text="🔒")
        else:
            password_entry.config(show='•')
            toggle_btn.config(text="👁")

    def on_exit():
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            root.destroy()

    root = tk.Tk()
    root.title("A&Y Library Login")
    root.attributes('-fullscreen', True)

    # Attempt to load background image (assets/library_bg.jpg). If Pillow not available
    # or file missing, fall back to a plain background color.
    bg_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'library_bg.jpg')
    if PIL_AVAILABLE and os.path.exists(bg_image_path):
        try:
            # Get screen size and prepare background with dim overlay (~30%)
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            img = Image.open(bg_image_path).convert('RGBA')
            img = img.resize((sw, sh), Image.LANCZOS)
            overlay = Image.new('RGBA', (sw, sh), (0, 0, 0, int(255 * 0.30)))
            img = Image.alpha_composite(img, overlay)

            # Convert to RGB and create PhotoImage with explicit master to avoid Tkinter image lifecycle issues
            rgb_img = img.convert('RGB')

            canvas = tk.Canvas(root, width=sw, height=sh, highlightthickness=0)
            canvas.pack(fill='both', expand=True)

            bg_photo = ImageTk.PhotoImage(rgb_img, master=root)
            # Keep a strong reference on the root and canvas to avoid GC and Tcl image disposal
            root._bg_photo = bg_photo
            canvas.bg_photo = bg_photo  # also keep on canvas

            # Ensure Tk has registered the image before creating the canvas item
            root.update_idletasks()
            canvas.create_image(0, 0, image=root._bg_photo, anchor='nw')

            # main content will be placed on the canvas (centered)
            main_container_parent = canvas
            create_window_fn = lambda widget: canvas.create_window(sw // 2, sh // 2, window=widget)
        except Exception as e:
            logger.exception("Failed to load background image: %s", e)
            root.configure(bg="#f0f2f5")
            main_container_parent = root
            create_window_fn = lambda widget: widget.pack(expand=True, fill='both')
    else:
        root.configure(bg="#f0f2f5")
        main_container_parent = root
        create_window_fn = lambda widget: widget.pack(expand=True, fill='both')

    # Add exit button in top-right corner
    exit_fullscreen_btn = tk.Button(root, text="✕", command=on_exit, font=("Segoe UI", 16), 
                                    bg="#f0f2f5", fg="#5f6368", relief="flat", cursor="hand2",
                                    padx=15, pady=5)
    exit_fullscreen_btn.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)
    exit_fullscreen_btn.bind("<Enter>", lambda e: exit_fullscreen_btn.configure(fg="#e74c3c"))
    exit_fullscreen_btn.bind("<Leave>", lambda e: exit_fullscreen_btn.configure(fg="#5f6368"))

    # Create the main container (placed on top of the canvas if present)
    main_container = tk.Frame(main_container_parent, bg="#f0f2f5", padx=40, pady=40)
    create_window_fn(main_container)

    title_frame = tk.Frame(main_container, bg="#f0f2f5")
    title_frame.pack(pady=(0, 40))

    title = tk.Label(title_frame, text="A&Y Library", font=("Segoe UI", 48, "bold"), bg="#f0f2f5", fg="#1a73e8")
    title.pack()

    subtitle = tk.Label(title_frame, text="Your Gateway to Knowledge", font=("Segoe UI", 18), bg="#f0f2f5", fg="#5f6368")
    subtitle.pack(pady=(10, 0))

    form_frame = tk.Frame(main_container, bg="white", padx=40, pady=30, relief="flat", 
                         highlightbackground="#dadce0", highlightthickness=1)
    form_frame.pack(pady=20)

    form_title = tk.Label(form_frame, text="Sign In", font=("Segoe UI", 24, "bold"), bg="white", fg="#202124")
    form_title.pack(pady=(0, 20))

    # Username field
    username_frame = tk.Frame(form_frame, bg="white")
    username_frame.pack(fill="x", pady=(0, 15))
    tk.Label(username_frame, text="Username", font=("Segoe UI", 12), bg="white", fg="#5f6368").pack(anchor="w")
    username_entry = ttk.Entry(username_frame, font=("Segoe UI", 12), width=30)
    username_entry.pack(fill="x", pady=(5, 0))

    # Password field with toggle
    password_frame = tk.Frame(form_frame, bg="white")
    password_frame.pack(fill="x", pady=(0, 25))
    tk.Label(password_frame, text="Password", font=("Segoe UI", 12), bg="white", fg="#5f6368").pack(anchor="w")
    
    password_container = tk.Frame(password_frame, bg="white")
    password_container.pack(fill="x", pady=(5, 0))
    
    password_entry = ttk.Entry(password_container, font=("Segoe UI", 12), show="•", width=30)
    password_entry.pack(side="left", fill="x", expand=True)
    
    toggle_btn = tk.Button(password_container, text="👁", command=toggle_password, 
                          font=("Segoe UI", 10), bg="white", fg="#5f6368", 
                          relief="flat", cursor="hand2", padx=5)
    toggle_btn.pack(side="left", padx=(5, 0))

    # Buttons
    button_frame = tk.Frame(form_frame, bg="white")
    button_frame.pack(fill="x", pady=(0, 20))

    login_btn = tk.Button(button_frame, text="Login", command=handle_login, 
                         font=("Segoe UI", 11, "bold"), width=20, height=2, 
                         bg="#1a73e8", fg="white", cursor="hand2", relief="flat")
    login_btn.pack(side="left", padx=(0, 10))
    login_btn.bind("<Enter>", lambda e: login_btn.configure(bg="#1557b0"))
    login_btn.bind("<Leave>", lambda e: login_btn.configure(bg="#1a73e8"))

    register_btn = tk.Button(button_frame, text="Register", command=handle_register, 
                            font=("Segoe UI", 11, "bold"), width=20, height=2, 
                            bg="#34a853", fg="white", cursor="hand2", relief="flat")
    register_btn.pack(side="left", padx=10)
    register_btn.bind("<Enter>", lambda e: register_btn.configure(bg="#2d9249"))
    register_btn.bind("<Leave>", lambda e: register_btn.configure(bg="#34a853"))

    exit_btn = tk.Button(button_frame, text="Exit", command=on_exit, 
                        font=("Segoe UI", 11, "bold"), width=20, height=2, 
                        bg="#ea4335", fg="white", cursor="hand2", relief="flat")
    exit_btn.pack(side="left", padx=10)
    exit_btn.bind("<Enter>", lambda e: exit_btn.configure(bg="#d33426"))
    exit_btn.bind("<Leave>", lambda e: exit_btn.configure(bg="#ea4335"))

    # Status label
    status_label = tk.Label(main_container, text="", font=("Segoe UI", 12), bg="#f0f2f5", pady=10)
    status_label.pack()

    # Help text
    help_label = tk.Label(main_container, text="Press ESC to exit fullscreen | Enter to login", 
                         font=("Segoe UI", 10), bg="#f0f2f5", fg="#9aa0a6")
    help_label.pack(pady=(10, 0))

    # Configure ttk style
    style = ttk.Style()
    style.configure("TEntry", padding=10, relief="flat", borderwidth=1)

    # Keyboard shortcuts
    root.bind('<Return>', lambda e: handle_login())
    root.bind('<Escape>', lambda e: on_exit())
    
    # Focus on username entry
    username_entry.focus()

    root.mainloop()

if __name__ == "__main__":
    init_db()
    launch_login_gui(lambda username, is_admin: print(f"Logged in as {username}, Admin: {is_admin}"))