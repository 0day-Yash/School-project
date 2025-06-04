import tkinter as tk
from tkinter import ttk, messagebox
from login import launch_login_gui
from book_management import BookManagementGUI

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("A&Y Library System")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f2f5")
        self.setup_gui()

    def setup_gui(self):
        # Main container
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=40, pady=40)
        main_container.pack(expand=True, fill="both")

        # Title
        title = tk.Label(
            main_container,
            text="A&Y Library System",
            font=("Segoe UI", 48, "bold"),
            bg="#f0f2f5",
            fg="#1a73e8"
        )
        title.pack(pady=(0, 40))

        subtitle = tk.Label(
            main_container,
            text="Welcome to the Library Management System",
            font=("Segoe UI", 18),
            bg="#f0f2f5",
            fg="#5f6368"
        )
        subtitle.pack(pady=(0, 60))

        # Menu container with card-like appearance
        menu_frame = tk.Frame(
            main_container,
            bg="white",
            padx=40,
            pady=30,
            relief="flat",
            highlightbackground="#dadce0",
            highlightthickness=1
        )
        menu_frame.pack(pady=20)

        # Menu title
        menu_title = tk.Label(
            menu_frame,
            text="Select an Option",
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg="#202124"
        )
        menu_title.pack(pady=(0, 30))

        # Custom button style
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

        # Button container
        button_frame = tk.Frame(menu_frame, bg="white")
        button_frame.pack(pady=20)

        # Login button
        login_btn = RoundedButton(
            button_frame,
            text="Login to Library",
            command=self.open_login,
            font=("Segoe UI", 14, "bold"),
            width=25,
            height=2,
            bg="#1a73e8",
            fg="white",
            cursor="hand2"
        )
        login_btn.normal_color = "#1a73e8"
        login_btn.hover_color = "#1557b0"
        login_btn.pack(pady=10)

        # Book Management button
        book_mgmt_btn = RoundedButton(
            button_frame,
            text="Manage Books",
            command=self.open_book_management,
            font=("Segoe UI", 14, "bold"),
            width=25,
            height=2,
            bg="#34a853",
            fg="white",
            cursor="hand2"
        )
        book_mgmt_btn.normal_color = "#34a853"
        book_mgmt_btn.hover_color = "#2d9249"
        book_mgmt_btn.pack(pady=10)

        # Exit button
        exit_btn = RoundedButton(
            button_frame,
            text="Exit",
            command=self.root.destroy,
            font=("Segoe UI", 14, "bold"),
            width=25,
            height=2,
            bg="#ea4335",
            fg="white",
            cursor="hand2"
        )
        exit_btn.normal_color = "#ea4335"
        exit_btn.hover_color = "#d33426"
        exit_btn.pack(pady=10)

    def open_login(self):
        self.root.withdraw()  # Hide the main window
        launch_login_gui(self.on_login_success)

    def on_login_success(self, username):
        self.root.deiconify()  # Show the main window again
        messagebox.showinfo("Welcome", f"Welcome back, {username}!")

    def open_book_management(self):
        self.root.withdraw()  # Hide the main window
        book_window = tk.Toplevel()
        app = BookManagementGUI(book_window)
        
        def on_book_window_close():
            book_window.destroy()
            self.root.deiconify()  # Show the main window again
        
        book_window.protocol("WM_DELETE_WINDOW", on_book_window_close)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainMenu()
    app.run() 