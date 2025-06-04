import tkinter as tk
from tkinter import ttk, messagebox
from login import launch_login_gui
from book_management import BookManagementGUI
from borrow_return import BorrowGUI, ReturnGUI, HistoryGUI
import sqlite3

class Dashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.setup_gui()

    def get_statistics(self):
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            
            # Get total books
            c.execute("SELECT COUNT(*) FROM books")
            total_books = c.fetchone()[0]
            
            # Get total available books
            c.execute("SELECT SUM(quantity) FROM books")
            total_copies = c.fetchone()[0] or 0
            
            # Get total users
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            
            # Get total borrowings
            c.execute("SELECT COUNT(*) FROM borrowings")
            total_borrowings = c.fetchone()[0] or 0
            
            # Get active borrowings
            c.execute("SELECT COUNT(*) FROM borrowings WHERE return_date IS NULL")
            active_borrowings = c.fetchone()[0] or 0
            
            # Get most popular genre
            c.execute("""
                SELECT genre, COUNT(*) as count 
                FROM books 
                GROUP BY genre 
                ORDER BY count DESC 
                LIMIT 1
            """)
            popular_genre = c.fetchone()
            popular_genre = popular_genre[0] if popular_genre else "N/A"
            
            return {
                "total_books": total_books,
                "total_copies": total_copies,
                "total_users": total_users,
                "total_borrowings": total_borrowings,
                "active_borrowings": active_borrowings,
                "popular_genre": popular_genre
            }

    def setup_gui(self):
        self.root.title("Library Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a1a")

        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a1a", padx=40, pady=40)
        main_container.pack(expand=True, fill="both")

        # Header with welcome message and credits
        header_frame = tk.Frame(main_container, bg="#1a1a1a")
        header_frame.pack(fill="x", pady=(0, 30))

        welcome_label = tk.Label(
            header_frame,
            text=f"Welcome back, {self.username}!",
            font=("Segoe UI", 24, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"
        )
        welcome_label.pack(side="left")

        credits_label = tk.Label(
            header_frame,
            text="Made by Yash and Aryan\nDatabase hosted on Purplerain servers",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#888888",
            justify="right"
        )
        credits_label.pack(side="right")

        # Statistics section
        stats_frame = tk.Frame(main_container, bg="#1a1a1a")
        stats_frame.pack(fill="x", pady=(0, 30))

        stats = self.get_statistics()
        
        # Create stat cards
        stat_cards = [
            ("Total Books", f"{stats['total_books']}", "#2ecc71"),
            ("Total Copies", f"{stats['total_copies']}", "#3498db"),
            ("Total Users", f"{stats['total_users']}", "#9b59b6"),
            ("Active Borrowings", f"{stats['active_borrowings']}", "#e74c3c"),
            ("Total Borrowings", f"{stats['total_borrowings']}", "#f1c40f"),
            ("Popular Genre", stats['popular_genre'], "#1abc9c")
        ]

        for i, (title, value, color) in enumerate(stat_cards):
            card = tk.Frame(
                stats_frame,
                bg="#2d2d2d",
                padx=20,
                pady=15,
                relief="flat",
                highlightbackground=color,
                highlightthickness=1
            )
            card.grid(row=0, column=i, padx=10, sticky="nsew")

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 12),
                bg="#2d2d2d",
                fg="#888888"
            ).pack()

            tk.Label(
                card,
                text=value,
                font=("Segoe UI", 20, "bold"),
                bg="#2d2d2d",
                fg=color
            ).pack(pady=(5, 0))

        # Configure grid weights
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        stats_frame.grid_columnconfigure(4, weight=1)
        stats_frame.grid_columnconfigure(5, weight=1)

        # Quick actions section
        actions_frame = tk.Frame(main_container, bg="#1a1a1a")
        actions_frame.pack(fill="x", pady=(0, 30))

        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=("Segoe UI", 18, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"
        ).pack(anchor="w", pady=(0, 20))

        # Action buttons
        actions = [
            ("Borrow Book", self.open_borrow, "#2ecc71"),
            ("Return Book", self.open_return, "#e74c3c"),
            ("View History", self.open_history, "#3498db"),
            ("Manage Books", self.open_book_management, "#9b59b6")
        ]

        for title, command, color in actions:
            btn = tk.Button(
                actions_frame,
                text=title,
                command=command,
                font=("Segoe UI", 12, "bold"),
                bg=color,
                fg="white",
                relief="flat",
                padx=20,
                pady=10,
                cursor="hand2"
            )
            btn.pack(side="left", padx=10)

        # Logout button
        logout_btn = tk.Button(
            main_container,
            text="Logout",
            command=self.logout,
            font=("Segoe UI", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        logout_btn.pack(side="right", pady=20)

    def open_borrow(self):
        borrow_window = tk.Toplevel(self.root)
        BorrowGUI(borrow_window, self.username)

    def open_return(self):
        return_window = tk.Toplevel(self.root)
        ReturnGUI(return_window, self.username)

    def open_history(self):
        history_window = tk.Toplevel(self.root)
        HistoryGUI(history_window, self.username)

    def open_book_management(self):
        book_window = tk.Toplevel(self.root)
        BookManagementGUI(book_window)

    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        app = MainMenu(root)
        root.mainloop()

class MainMenu:
    def __init__(self, root=None):
        self.root = root if root else tk.Tk()
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