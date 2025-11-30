import tkinter as tk
from tkinter import ttk, messagebox
from login import launch_login_gui
from borrow_return import BorrowGUI, ReturnGUI, HistoryGUI, RecommendationsGUI
from admin import AdminPanel
import sqlite3
from db_init import DB_NAME
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

class Dashboard:
    def __init__(self, root, username, is_admin):
        self.root = root
        self.username = username
        self.is_admin = is_admin
        logger.debug("Initializing Dashboard for user=%s is_admin=%s", username, is_admin)
        self.setup_styles()
        self.setup_gui()
        self.update_clock()

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
                c.execute("SELECT COUNT(*) FROM borrowings WHERE username = ? AND return_date IS NULL", (self.username,))
                my_active = c.fetchone()[0] or 0
                stats = {
                    "total_books": total_books,
                    "total_copies": total_copies,
                    "total_users": total_users,
                    "total_borrowings": total_borrowings,
                    "active_borrowings": active_borrowings,
                    "popular_genre": popular_genre[0] if popular_genre else "N/A",
                    "total_fines": total_fines,
                    "my_active": my_active
                }
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
                "total_fines": 0,
                "my_active": 0
            }

    def update_clock(self):
        """Update the clock display"""
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%B %d, %Y")
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.root.after(1000, self.update_clock)

    def setup_gui(self):
        self.root.title("Library Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f5f7fa")

        # Top bar with exit button
        top_bar = tk.Frame(self.root, bg="#ffffff", height=60, relief="flat")
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        # Library branding on left
        tk.Label(top_bar, text="📚 A&Y Library", font=("Segoe UI", 16, "bold"), 
                bg="#ffffff", fg="#007bff").pack(side="left", padx=20)

        # Clock and date in center
        clock_frame = tk.Frame(top_bar, bg="#ffffff")
        clock_frame.pack(side="left", expand=True)
        self.time_label = tk.Label(clock_frame, text="", font=("Segoe UI", 14, "bold"), 
                                   bg="#ffffff", fg="#495057")
        self.time_label.pack()
        self.date_label = tk.Label(clock_frame, text="", font=("Segoe UI", 10), 
                                   bg="#ffffff", fg="#6c757d")
        self.date_label.pack()

        # Logout button
        logout_btn = tk.Button(top_bar, text="🚪 Logout", command=self.logout, 
                              font=("Segoe UI", 12), bg="#ffffff", fg="#6c757d", 
                              relief="flat", cursor="hand2", padx=15, pady=5)
        logout_btn.pack(side="right", padx=5)
        logout_btn.bind("<Enter>", lambda e: logout_btn.configure(bg="#e2e6ea", fg="#343a40"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.configure(bg="#ffffff", fg="#6c757d"))

        # Exit button on right
        exit_btn = tk.Button(top_bar, text="✕ Exit", command=self.confirm_exit, 
                            font=("Segoe UI", 12), bg="#ffffff", fg="#dc3545", 
                            relief="flat", cursor="hand2", padx=15, pady=5)
        exit_btn.pack(side="right", padx=20)
        exit_btn.bind("<Enter>", lambda e: exit_btn.configure(bg="#f8d7da", fg="#721c24"))
        exit_btn.bind("<Leave>", lambda e: exit_btn.configure(bg="#ffffff", fg="#dc3545"))

        # Main Container with scrollable canvas
        main_container = tk.Frame(self.root, bg="#f5f7fa")
        main_container.pack(expand=True, fill="both", padx=30, pady=20)

        # Welcome Header
        header_frame = tk.Frame(main_container, bg="#007bff", relief="flat")
        header_frame.pack(fill="x", pady=(0, 20))
        
        welcome_text = f"Welcome back, {self.username}!"
        if self.is_admin:
            welcome_text += " (Admin)"
        
        tk.Label(header_frame, text=welcome_text, font=("Segoe UI", 26, "bold"), 
                bg="#007bff", fg="white").pack(side="left", padx=30, pady=20)
        
        # Quick stats in header
        quick_stats = tk.Frame(header_frame, bg="#007bff")
        quick_stats.pack(side="right", padx=30)
        
        stats = self.get_statistics()
        tk.Label(quick_stats, text=f"My Active: {stats['my_active']}", 
                font=("Segoe UI", 11), bg="#007bff", fg="white").pack(anchor="e")
        tk.Label(quick_stats, text=f"My Fines: Rs.{stats['total_fines']}", 
                font=("Segoe UI", 11), bg="#007bff", fg="#ffc107").pack(anchor="e")

        # Stats Cards Section
        stats_section = tk.Frame(main_container, bg="#f5f7fa")
        stats_section.pack(fill="x", pady=(0, 20))
        
        tk.Label(stats_section, text="Library Overview", font=("Segoe UI", 18, "bold"), 
                bg="#f5f7fa", fg="#212529").pack(anchor="w", pady=(0, 15))
        
        self.stats_frame = tk.Frame(stats_section, bg="#f5f7fa")
        self.stats_frame.pack(fill="x")
        self.update_stats()

        # Quick Actions Section
        actions_section = tk.Frame(main_container, bg="#f5f7fa")
        actions_section.pack(fill="x", pady=(0, 20))
        
        tk.Label(actions_section, text="Quick Actions", font=("Segoe UI", 18, "bold"), 
                bg="#f5f7fa", fg="#212529").pack(anchor="w", pady=(0, 15))

        actions_container = tk.Frame(actions_section, bg="#f5f7fa")
        actions_container.pack(fill="x")

        actions = [
            ("📖 Borrow Book", self.open_borrow, "#20c997", "Borrow books from library"),
            ("↩️ Return Book", self.open_return, "#dc3545", "Return borrowed books"),
            ("📜 View History", self.open_history, "#007bff", "See your borrowing history"),
            ("⭐ Recommendations", self.open_recommendations, "#ffc107", "Get personalized suggestions")
        ]
        
        if self.is_admin:
            actions.append(("⚙️ Admin Panel", self.open_admin_panel, "#6c757d", "Manage library system"))

        for i, (title, command, color, desc) in enumerate(actions):
            card = tk.Frame(actions_container, bg="white", relief="flat", 
                          highlightbackground="#dee2e6", highlightthickness=1, cursor="hand2")
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew", ipadx=15, ipady=15)
            
            tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), 
                    bg="white", fg=color).pack(pady=(5, 2))
            tk.Label(card, text=desc, font=("Segoe UI", 9), 
                    bg="white", fg="#6c757d").pack(pady=(0, 5))
            
            # Make entire card clickable
            card.bind("<Button-1>", lambda e, cmd=command: cmd())
            card.bind("<Enter>", lambda e, c=card, col=color: c.configure(
                highlightbackground=col, highlightthickness=2, bg="#f8f9fa"))
            card.bind("<Leave>", lambda e, c=card: c.configure(
                highlightbackground="#dee2e6", highlightthickness=1, bg="white"))
            
            # Make labels inside clickable too
            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda e, cmd=command: cmd())
                widget.bind("<Enter>", lambda e, c=card, col=color: [
                    c.configure(highlightbackground=col, highlightthickness=2, bg="#f8f9fa"),
                    widget.configure(bg="#f8f9fa")
                ])
                widget.bind("<Leave>", lambda e, c=card, w=widget: [
                    c.configure(highlightbackground="#dee2e6", highlightthickness=1, bg="white"),
                    w.configure(bg="white")
                ])

        for i in range(3):
            actions_container.grid_columnconfigure(i, weight=1, uniform="action")

        # Bottom action bar
        bottom_bar = tk.Frame(main_container, bg="#f5f7fa")
        bottom_bar.pack(fill="x", pady=(10, 0))
        
        refresh_btn = tk.Button(bottom_bar, text="🔄 Refresh Stats", command=self.update_stats, 
                               font=("Segoe UI", 11, "bold"), bg="#17a2b8", fg="white", 
                               relief="flat", padx=20, pady=10, cursor="hand2")
        refresh_btn.pack(side="right", padx=5)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.configure(bg="#138496"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.configure(bg="#17a2b8"))
        
        logout_btn = tk.Button(bottom_bar, text="🚪 Logout", command=self.logout, 
                              font=("Segoe UI", 11, "bold"), bg="#6c757d", fg="white", 
                              relief="flat", padx=20, pady=10, cursor="hand2")
        logout_btn.pack(side="right", padx=5)
        logout_btn.bind("<Enter>", lambda e: logout_btn.configure(bg="#5a6268"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.configure(bg="#6c757d"))

    def update_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
            
        stats = self.get_statistics()
        
        stat_cards = [
            ("📚 Total Books", f"{stats['total_books']}", "#20c997", "Unique titles"),
            ("📦 Total Copies", f"{stats['total_copies']}", "#007bff", "Books in stock"),
            ("👥 Total Users", f"{stats['total_users']}", "#6c757d", "Registered members"),
            ("🔄 Active Loans", f"{stats['active_borrowings']}", "#dc3545", "Currently borrowed"),
            ("📊 All Borrowings", f"{stats['total_borrowings']}", "#ffc107", "Total transactions"),
            ("🎭 Popular Genre", stats['popular_genre'], "#17a2b8", "Most borrowed")
        ]
        
        for i, (title, value, color, subtitle) in enumerate(stat_cards):
            card = tk.Frame(self.stats_frame, bg="white", relief="flat", 
                          highlightbackground="#dee2e6", highlightthickness=1)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew", ipadx=15, ipady=10)
            
            tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), 
                    bg="white", fg="#495057").pack(pady=(5, 0))
            tk.Label(card, text=value, font=("Segoe UI", 22, "bold"), 
                    bg="white", fg=color).pack(pady=5)
            tk.Label(card, text=subtitle, font=("Segoe UI", 9), 
                    bg="white", fg="#6c757d").pack(pady=(0, 5))
        
        for i in range(3):
            self.stats_frame.grid_columnconfigure(i, weight=1, uniform="stat")

    def confirm_exit(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def open_borrow(self):
        logger.debug("open_borrow called for user=%s", self.username)
        borrow_window = tk.Toplevel(self.root)
        BorrowGUI(borrow_window, self.username)
        borrow_window.protocol("WM_DELETE_WINDOW", lambda: [borrow_window.destroy(), self.update_stats()])

    def open_return(self):
        logger.debug("open_return called for user=%s", self.username)
        return_window = tk.Toplevel(self.root)
        ReturnGUI(return_window, self.username)
        return_window.protocol("WM_DELETE_WINDOW", lambda: [return_window.destroy(), self.update_stats()])

    def open_history(self):
        logger.debug("open_history called for user=%s", self.username)
        history_window = tk.Toplevel(self.root)
        HistoryGUI(history_window, self.username)

    def open_recommendations(self):
        logger.debug("open_recommendations called for user=%s", self.username)
        rec_window = tk.Toplevel(self.root)
        RecommendationsGUI(rec_window, self.username)

    def open_admin_panel(self):
        if self.is_admin:
            logger.debug("open_admin_panel called for admin user=%s", self.username)
            admin_window = tk.Toplevel(self.root)
            AdminPanel(admin_window, self.username, lambda: [admin_window.destroy(), self.update_stats()])
            admin_window.protocol("WM_DELETE_WINDOW", lambda: [admin_window.destroy(), self.update_stats()])
        else:
            messagebox.showerror("Access Denied", "Only admins can access the admin panel.")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            root = tk.Tk()
            app = MainMenu(root)
            root.mainloop()


class MainMenu:
    def __init__(self, root=None):
        self.root = root if root else tk.Tk()
        self.root.title("A&Y Library System")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f5f7fa")
        self.setup_gui()

    def setup_gui(self):
        # Top decorative bar
        top_bar = tk.Frame(self.root, bg="#007bff", height=5)
        top_bar.pack(fill="x", side="top")

        # Exit button in top-right
        exit_btn = tk.Button(self.root, text="✕", command=self.confirm_exit, 
                            font=("Segoe UI", 16), bg="#f5f7fa", fg="#6c757d", 
                            relief="flat", cursor="hand2", padx=15, pady=5)
        exit_btn.place(relx=1.0, rely=0, anchor="ne", x=-10, y=15)
        exit_btn.bind("<Enter>", lambda e: exit_btn.configure(fg="#dc3545"))
        exit_btn.bind("<Leave>", lambda e: exit_btn.configure(fg="#6c757d"))

        # Main Container
        main_container = tk.Frame(self.root, bg="#f5f7fa")
        main_container.pack(expand=True, fill="both", padx=50, pady=50)

        # Large Library Icon/Logo
        logo_frame = tk.Frame(main_container, bg="#f5f7fa")
        logo_frame.pack(pady=(0, 20))
        
        tk.Label(logo_frame, text="📚", font=("Segoe UI", 80), bg="#f5f7fa").pack()

        # Title Card
        title_frame = tk.Frame(main_container, bg="white", relief="flat", 
                             highlightbackground="#007bff", highlightthickness=3)
        title_frame.pack(pady=(0, 40))
        
        tk.Label(title_frame, text="A&Y Library", font=("Segoe UI", 42, "bold"), 
                bg="white", fg="#007bff").pack(padx=50, pady=(30, 10))
        tk.Label(title_frame, text="Your Gateway to Knowledge", font=("Segoe UI", 18), 
                bg="white", fg="#6c757d").pack(padx=50, pady=(0, 30))

        # Menu Card
        menu_frame = tk.Frame(main_container, bg="white", relief="flat", 
                            highlightbackground="#dee2e6", highlightthickness=1)
        menu_frame.pack()

        tk.Label(menu_frame, text="Welcome! Please Select an Option", 
                font=("Segoe UI", 18, "bold"), bg="white", fg="#343a40").pack(padx=50, pady=(30, 20))

        button_container = tk.Frame(menu_frame, bg="white")
        button_container.pack(padx=50, pady=(0, 30))

        buttons = [
            ("🔐 Login to Library", self.open_login, "#007bff", "Access your account"),
            ("⚙️ Admin Panel", self.open_admin_panel, "#20c997", "Administrative access"),
            ("❌ Exit Application", self.confirm_exit, "#dc3545", "Close the application")
        ]
        
        for title, command, color, desc in buttons:
            btn_frame = tk.Frame(button_container, bg="white", relief="flat", 
                               highlightbackground="#dee2e6", highlightthickness=1, cursor="hand2")
            btn_frame.pack(pady=8, fill="x")
            
            btn_content = tk.Frame(btn_frame, bg="white")
            btn_content.pack(fill="x", padx=20, pady=15)
            
            tk.Label(btn_content, text=title, font=("Segoe UI", 14, "bold"), 
                    bg="white", fg=color, anchor="w").pack(fill="x")
            tk.Label(btn_content, text=desc, font=("Segoe UI", 10), 
                    bg="white", fg="#6c757d", anchor="w").pack(fill="x")
            
            # Make entire frame clickable
            btn_frame.bind("<Button-1>", lambda e, cmd=command: cmd())
            btn_frame.bind("<Enter>", lambda e, f=btn_frame, col=color: f.configure(
                highlightbackground=col, highlightthickness=2, bg="#f8f9fa"))
            btn_frame.bind("<Leave>", lambda e, f=btn_frame: f.configure(
                highlightbackground="#dee2e6", highlightthickness=1, bg="white"))
            
            # Make inner widgets clickable
            for widget in [btn_content] + list(btn_content.winfo_children()):
                widget.bind("<Button-1>", lambda e, cmd=command: cmd())
                widget.bind("<Enter>", lambda e, f=btn_frame, col=color, w=widget: [
                    f.configure(highlightbackground=col, highlightthickness=2, bg="#f8f9fa"),
                    w.configure(bg="#f8f9fa")
                ])
                widget.bind("<Leave>", lambda e, f=btn_frame, w=widget: [
                    f.configure(highlightbackground="#dee2e6", highlightthickness=1, bg="white"),
                    w.configure(bg="white")
                ])

        # Footer
        footer = tk.Label(self.root, text="© 2025 A&Y Library System | Version 1.0", 
                         font=("Segoe UI", 10), bg="#f5f7fa", fg="#6c757d")
        footer.pack(side="bottom", pady=20)

    def confirm_exit(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the application?"):
            self.root.destroy()

    def open_login(self):
        self.root.withdraw()
        launch_login_gui(self.on_login_success)

    def on_login_success(self, username, is_admin):
        logger.debug("on_login_success called with username=%s is_admin=%s", username, is_admin)
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