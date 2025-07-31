import tkinter as tk
from tkinter import ttk, messagebox
from login import launch_login_gui
from borrow_return import BorrowGUI, ReturnGUI, HistoryGUI
from admin import AdminPanel
import sqlite3
from db_init import DB_NAME

class Dashboard:
    def __init__(self, root, username, is_admin):
        self.root = root
        self.username = username
        self.is_admin = is_admin
        self.setup_styles()
        self.setup_gui()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
        self.style.configure("TLabel", font=("Segoe UI", 12), background="#ffffff")
        self.style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#20c997", foreground="white")

    def get_statistics(self):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM books")
                total_books = c.fetchone()[0]
                c.execute("SELECT SUM(quantity) FROM books")
                total_copies = c.fetchone()[0] or 0
                c.execute("SELECT COUNT(*) FROM users")
                total_users = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM borrowings")
                total_borrowings = c.fetchone()[0] or 0
                c.execute("SELECT COUNT(*) FROM borrowings WHERE return_date IS NULL")
                active_borrowings = c.fetchone()[0] or 0
                c.execute("SELECT genre, COUNT(*) as count FROM books GROUP BY genre ORDER BY count DESC LIMIT 1")
                popular_genre = c.fetchone()
                c.execute("SELECT SUM(fine) FROM borrowings WHERE username = ?", (self.username,))
                total_fines = c.fetchone()[0] or 0
                stats = {
                    "total_books": total_books,
                    "total_copies": total_copies,
                    "total_users": total_users,
                    "total_borrowings": total_borrowings,
                    "active_borrowings": active_borrowings,
                    "popular_genre": popular_genre[0] if popular_genre else "N/A",
                    "total_fines": total_fines
                }
                print("Dashboard statistics:", stats)
                return stats
        except sqlite3.Error as e:
            print(f"Error querying statistics: {e}")
            return {
                "total_books": 0,
                "total_copies": 0,
                "total_users": 0,
                "total_borrowings": 0,
                "active_borrowings": 0,
                "popular_genre": "N/A",
                "total_fines": 0
            }

    def setup_gui(self):
        self.root.title("Library Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#e9ecef")

        # Side Panels
        left_panel = tk.Frame(self.root, bg="#e9ecef", width=200, relief="flat", highlightbackground="#ced4da", highlightthickness=1)
        left_panel.pack(side="left", fill="y")
        right_panel = tk.Frame(self.root, bg="#e9ecef", width=200, relief="flat", highlightbackground="#ced4da", highlightthickness=1)
        right_panel.pack(side="right", fill="y")

        # Main Container
        main_container = tk.Frame(self.root, bg="#e9ecef", padx=40, pady=40)
        main_container.pack(expand=True, fill="both")

        # Header
        header_frame = tk.Frame(main_container, bg="#007bff")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text=f"Welcome, {self.username}!", font=("Segoe UI", 24, "bold"), bg="#007bff", fg="white").pack(side="left", padx=20, pady=15)
        tk.Label(header_frame, text="A&Y Library System", font=("Segoe UI", 14), bg="#007bff", fg="#e9ecef").pack(side="right", padx=20)

        # Stats
        self.stats_frame = tk.Frame(main_container, bg="#e9ecef")
        self.stats_frame.pack(fill="x", pady=15)
        self.update_stats()

        # Actions
        actions_frame = tk.Frame(main_container, bg="#e9ecef")
        actions_frame.pack(fill="x", pady=15)
        tk.Label(actions_frame, text="Quick Actions", font=("Segoe UI", 18, "bold"), bg="#e9ecef", fg="#007bff").pack(anchor="center", pady=10)

        actions = [
            ("Borrow Book", self.open_borrow, "#20c997"),
            ("Return Book", self.open_return, "#dc3545"),
            ("View History", self.open_history, "#007bff")
        ]
        if self.is_admin:
            actions.append(("Admin Panel", self.open_admin_panel, "#6c757d"))

        button_frame = tk.Frame(actions_frame, bg="#e9ecef")
        button_frame.pack(anchor="center")
        for title, command, color in actions:
            btn = tk.Button(button_frame, text=title, command=command, font=("Segoe UI", 12, "bold"), bg=color, fg="white", relief="flat", padx=20, pady=10, cursor="hand2")
            btn.pack(side="left", padx=15)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=f'#{int(c[1:3], 16)-25:02x}{int(c[3:5], 16)-25:02x}{int(c[5:7], 16)-25:02x}', font=("Segoe UI", 13, "bold")))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c, font=("Segoe UI", 12, "bold")))

        # Footer
        footer_frame = tk.Frame(main_container, bg="#e9ecef")
        footer_frame.pack(fill="x", pady=15)
        tk.Button(footer_frame, text="Refresh Stats", command=self.update_stats, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right", padx=15)
        tk.Button(footer_frame, text="Logout", command=self.logout, font=("Segoe UI", 12, "bold"), bg="#dc3545", fg="white", relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right")

    def update_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        stats = self.get_statistics()
        stat_cards = [
            ("Total Books", f"{stats['total_books']}", "#20c997"),
            ("Total Copies", f"{stats['total_copies']}", "#007bff"),
            ("Total Users", f"{stats['total_users']}", "#6c757d"),
            ("Active Borrowings", f"{stats['active_borrowings']}", "#dc3545"),
            ("Total Borrowings", f"{stats['total_borrowings']}", "#ffc107"),
            ("Popular Genre", stats['popular_genre'], "#17a2b8"),
            ("Your Fines", f"Rs. {stats['total_fines']}", "#e83e8c")
        ]
        for i, (title, value, color) in enumerate(stat_cards):
            card = tk.Frame(self.stats_frame, bg="white", padx=20, pady=15, relief="flat", highlightbackground="#20c997", highlightthickness=2)
            card.grid(row=i//3, column=i%3, padx=15, pady=10, sticky="nsew")
            tk.Label(card, text=title, font=("Segoe UI", 12), bg="white", fg="#6c757d").pack()
            tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg=color).pack(pady=5)
        self.stats_frame.grid_columnconfigure(tuple(range(3)), weight=1)
        self.stats_frame.pack(anchor="center")

    def open_borrow(self):
        borrow_window = tk.Toplevel(self.root)
        BorrowGUI(borrow_window, self.username)
        borrow_window.protocol("WM_DELETE_WINDOW", lambda: [borrow_window.destroy(), self.update_stats()])

    def open_return(self):
        return_window = tk.Toplevel(self.root)
        ReturnGUI(return_window, self.username)
        return_window.protocol("WM_DELETE_WINDOW", lambda: [return_window.destroy(), self.update_stats()])

    def open_history(self):
        history_window = tk.Toplevel(self.root)
        HistoryGUI(history_window, self.username)
        history_window.protocol("WM_DELETE_WINDOW", lambda: [history_window.destroy(), self.update_stats()])

    def open_admin_panel(self):
        if self.is_admin:
            admin_window = tk.Toplevel(self.root)
            AdminPanel(admin_window, self.username, lambda: [admin_window.destroy(), self.update_stats()])
            admin_window.protocol("WM_DELETE_WINDOW", lambda: [admin_window.destroy(), self.update_stats()])
        else:
            messagebox.showerror("Access Denied", "Only admins can access the admin panel.")

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
        self.root.configure(bg="#e9ecef")
        self.setup_gui()

    def setup_gui(self):
        # Side Panels
        left_panel = tk.Frame(self.root, bg="#e9ecef", width=200, relief="flat", highlightbackground="#ced4da", highlightthickness=1)
        left_panel.pack(side="left", fill="y")
        right_panel = tk.Frame(self.root, bg="#e9ecef", width=200, relief="flat", highlightbackground="#ced4da", highlightthickness=1)
        right_panel.pack(side="right", fill="y")

        # Main Container
        main_container = tk.Frame(self.root, bg="#e9ecef", padx=40, pady=40)
        main_container.pack(expand=True, fill="both")

        # Title Card
        title_frame = tk.Frame(main_container, bg="white", padx=30, pady=20, relief="flat", highlightbackground="#20c997", highlightthickness=2)
        title_frame.pack(pady=30, anchor="center")
        tk.Label(title_frame, text="A&Y Library", font=("Segoe UI", 36, "bold"), bg="white", fg="#007bff").pack()
        tk.Label(title_frame, text="Your Gateway to Knowledge", font=("Segoe UI", 18), bg="white", fg="#6c757d").pack(pady=10)

        # Menu
        menu_frame = tk.Frame(main_container, bg="white", padx=30, pady=30, relief="flat", highlightbackground="#20c997", highlightthickness=2)
        menu_frame.pack(pady=20, anchor="center")

        tk.Label(menu_frame, text="Select an Option", font=("Segoe UI", 20, "bold"), bg="white", fg="#343a40").pack(pady=15)

        button_frame = tk.Frame(menu_frame, bg="white")
        button_frame.pack(pady=15)

        buttons = [
            ("Login to Library", self.open_login, "#007bff"),
            ("Admin Panel", self.open_admin_panel, "#20c997"),
            ("Exit", self.root.destroy, "#dc3545")
        ]
        for title, command, color in buttons:
            btn = tk.Button(button_frame, text=title, command=command, font=("Segoe UI", 12, "bold"), bg=color, fg="white", relief="flat", padx=20, pady=12, width=20, cursor="hand2")
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=f'#{int(c[1:3], 16)-25:02x}{int(c[3:5], 16)-25:02x}{int(c[5:7], 16)-25:02x}', font=("Segoe UI", 13, "bold")))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c, font=("Segoe UI", 12, "bold")))

    def open_login(self):
        self.root.withdraw()
        launch_login_gui(self.on_login_success)

    def on_login_success(self, username, is_admin):
        self.root.deiconify()
        dashboard_window = tk.Toplevel(self.root)
        dashboard = Dashboard(dashboard_window, username, is_admin)
        dashboard_window.protocol("WM_DELETE_WINDOW", lambda: [dashboard_window.destroy(), self.root.deiconify()])
        self.root.withdraw()

    def open_admin_panel(self):
        self.root.withdraw()
        def on_admin_login_success(username, is_admin):
            if is_admin:
                admin_window = tk.Toplevel(self.root)
                AdminPanel(admin_window, username, lambda: [admin_window.destroy(), self.root.deiconify()])
                admin_window.protocol("WM_DELETE_WINDOW", lambda: [admin_window.destroy(), self.root.deiconify()])
            else:
                messagebox.showerror("Access Denied", "Only admins can access the admin panel.")
                self.root.deiconify()
        launch_login_gui(on_admin_login_success)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    from db_init import init_db
    init_db()
    app = MainMenu()
    app.run()
