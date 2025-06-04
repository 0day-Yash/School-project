import tkinter as tk
from tkinter import ttk, messagebox
from login import launch_login_gui
from book_management import BookManagementGUI
from borrow_return import BorrowGUI, ReturnGUI, HistoryGUI

class Dashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.setup_gui()

    def setup_gui(self):
        self.root.title(f"Welcome, {self.username} - A&Y Library Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f2f5")

        # Main container
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=40, pady=40)
        main_container.pack(expand=True, fill="both")

        # Welcome message
        welcome_frame = tk.Frame(main_container, bg="#f0f2f5")
        welcome_frame.pack(fill="x", pady=(0, 30))

        welcome_label = tk.Label(
            welcome_frame,
            text=f"Welcome back, {self.username}!",
            font=("Segoe UI", 24, "bold"),
            bg="#f0f2f5",
            fg="#1a73e8"
        )
        welcome_label.pack()

        # Quick stats frame
        stats_frame = tk.Frame(main_container, bg="white", padx=20, pady=20)
        stats_frame.pack(fill="x", pady=(0, 30))

        # Stats title
        stats_title = tk.Label(
            stats_frame,
            text="Library Overview",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#202124"
        )
        stats_title.pack(anchor="w", pady=(0, 20))

        # Stats grid
        stats_grid = tk.Frame(stats_frame, bg="white")
        stats_grid.pack(fill="x")

        # Sample stats (you can replace these with actual data)
        stats = [
            ("Total Books", "1,234"),
            ("Available Books", "1,000"),
            ("Borrowed Books", "234"),
            ("Active Members", "150")
        ]

        for i, (label, value) in enumerate(stats):
            stat_frame = tk.Frame(stats_grid, bg="white")
            stat_frame.grid(row=0, column=i, padx=20, sticky="ew")
            stats_grid.columnconfigure(i, weight=1)

            value_label = tk.Label(
                stat_frame,
                text=value,
                font=("Segoe UI", 24, "bold"),
                bg="white",
                fg="#1a73e8"
            )
            value_label.pack()

            label_label = tk.Label(
                stat_frame,
                text=label,
                font=("Segoe UI", 12),
                bg="white",
                fg="#5f6368"
            )
            label_label.pack()

        # Quick actions frame
        actions_frame = tk.Frame(main_container, bg="white", padx=20, pady=20)
        actions_frame.pack(fill="x")

        # Actions title
        actions_title = tk.Label(
            actions_frame,
            text="Quick Actions",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#202124"
        )
        actions_title.pack(anchor="w", pady=(0, 20))

        # Action buttons
        buttons_frame = tk.Frame(actions_frame, bg="white")
        buttons_frame.pack(fill="x")

        # Define actions
        actions = [
            ("Manage Books", self.open_book_management, "#4a9eff"),
            ("Borrow Book", self.open_borrow, "#34a853"),
            ("Return Book", self.open_return, "#fbbc05"),
            ("View History", self.open_history, "#ea4335")
        ]

        for i, (text, command, color) in enumerate(actions):
            btn_frame = tk.Frame(buttons_frame, bg="white")
            btn_frame.grid(row=0, column=i, padx=10, sticky="ew")
            buttons_frame.columnconfigure(i, weight=1)

            btn = tk.Button(
                btn_frame,
                text=text,
                command=command,
                font=("Segoe UI", 12, "bold"),
                bg=color,
                fg="white",
                relief="flat",
                cursor="hand2",
                padx=20,
                pady=10
            )
            btn.pack(fill="x")

            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_enter(e, b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_leave(e, b, c))

    def on_enter(self, event, button, color):
        # Darken the color on hover
        r, g, b = self.root.winfo_rgb(color)
        r, g, b = r//256, g//256, b//256
        darker = f'#{max(0, r-30):02x}{max(0, g-30):02x}{max(0, b-30):02x}'
        button.configure(bg=darker)

    def on_leave(self, event, button, color):
        button.configure(bg=color)

    def open_book_management(self):
        book_window = tk.Toplevel(self.root)
        app = BookManagementGUI(book_window)

    def open_borrow(self):
        borrow_window = tk.Toplevel(self.root)
        app = BorrowGUI(borrow_window, self.username)

    def open_return(self):
        return_window = tk.Toplevel(self.root)
        app = ReturnGUI(return_window, self.username)

    def open_history(self):
        history_window = tk.Toplevel(self.root)
        app = HistoryGUI(history_window, self.username)

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("A&Y Library System")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f2f5")
        self.setup_gui()

    def setup_gui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=40, pady=40)
        main_container.pack(expand=True, fill="both")

        # Title section
        title_frame = tk.Frame(main_container, bg="#f0f2f5")
        title_frame.pack(pady=(0, 40))

        title = tk.Label(
            title_frame,
            text="A&Y Library",
            font=("Segoe UI", 48, "bold"),
            bg="#f0f2f5",
            fg="#1a73e8"
        )
        title.pack()

        subtitle = tk.Label(
            title_frame,
            text="Your Gateway to Knowledge",
            font=("Segoe UI", 18),
            bg="#f0f2f5",
            fg="#5f6368"
        )
        subtitle.pack(pady=(10, 0))

        # Menu container
        menu_frame = tk.Frame(
            main_container,
            bg="white",
            padx=40,
            pady=30,
            relief="flat",
            highlightbackground="#dadce0",
            highlightthickness=1
        )
        menu_frame.pack(pady=40)

        # Menu title
        menu_title = tk.Label(
            menu_frame,
            text="Select an Option",
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg="#202124"
        )
        menu_title.pack(pady=(0, 30))

        # Button container
        button_frame = tk.Frame(menu_frame, bg="white")
        button_frame.pack(pady=20)

        # Login button
        login_btn = tk.Button(
            button_frame,
            text="Login to Library",
            command=self.open_login,
            font=("Segoe UI", 12, "bold"),
            bg="#1a73e8",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            width=20
        )
        login_btn.pack(pady=10)

        # Book Management button
        book_mgmt_btn = tk.Button(
            button_frame,
            text="Manage Books",
            command=self.open_book_management,
            font=("Segoe UI", 12, "bold"),
            bg="#34a853",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            width=20
        )
        book_mgmt_btn.pack(pady=10)

        # Exit button
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.destroy,
            font=("Segoe UI", 12, "bold"),
            bg="#ea4335",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            width=20
        )
        exit_btn.pack(pady=10)

        # Add hover effects
        for btn in [login_btn, book_mgmt_btn, exit_btn]:
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(e, b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))

    def on_enter(self, event, button):
        # Darken the color on hover
        color = button.cget("bg")
        r, g, b = self.root.winfo_rgb(color)
        r, g, b = r//256, g//256, b//256
        darker = f'#{max(0, r-30):02x}{max(0, g-30):02x}{max(0, b-30):02x}'
        button.configure(bg=darker)

    def on_leave(self, event, button):
        # Restore original color
        if button.cget("text") == "Login to Library":
            button.configure(bg="#1a73e8")
        elif button.cget("text") == "Manage Books":
            button.configure(bg="#34a853")
        else:
            button.configure(bg="#ea4335")

    def open_login(self):
        self.root.withdraw()
        launch_login_gui(self.on_login_success)

    def on_login_success(self, username):
        self.root.deiconify()
        # Create and show dashboard
        dashboard_window = tk.Toplevel(self.root)
        dashboard = Dashboard(dashboard_window, username)
        
        def on_dashboard_close():
            dashboard_window.destroy()
            self.root.deiconify()
        
        dashboard_window.protocol("WM_DELETE_WINDOW", on_dashboard_close)
        self.root.withdraw()

    def open_book_management(self):
        self.root.withdraw()
        book_window = tk.Toplevel()
        app = BookManagementGUI(book_window)
        
        def on_book_window_close():
            book_window.destroy()
            self.root.deiconify()
        
        book_window.protocol("WM_DELETE_WINDOW", on_book_window_close)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainMenu()
    app.run() 