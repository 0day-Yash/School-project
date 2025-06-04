import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class BorrowReturnSystem:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.init_tables()

    def init_tables(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # Create borrowings table
            c.execute("""
            CREATE TABLE IF NOT EXISTS borrowings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                username TEXT,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                return_date TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
            """)
            conn.commit()

    def borrow_book(self, book_id, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # Check if book is available
                c.execute("SELECT available FROM books WHERE id = ?", (book_id,))
                available = c.fetchone()[0]
                if available <= 0:
                    return False, "Book is not available for borrowing"

                # Calculate due date (14 days from now)
                due_date = datetime.now() + timedelta(days=14)

                # Add borrowing record
                c.execute("""
                INSERT INTO borrowings (book_id, username, due_date)
                VALUES (?, ?, ?)
                """, (book_id, username, due_date))

                # Update book availability
                c.execute("""
                UPDATE books 
                SET available = available - 1 
                WHERE id = ?
                """, (book_id,))

                conn.commit()
                return True, "Book borrowed successfully"
        except Exception as e:
            return False, str(e)

    def return_book(self, borrowing_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # Get book_id from borrowing record
                c.execute("SELECT book_id FROM borrowings WHERE id = ?", (borrowing_id,))
                book_id = c.fetchone()[0]

                # Update borrowing record
                c.execute("""
                UPDATE borrowings 
                SET return_date = CURRENT_TIMESTAMP 
                WHERE id = ?
                """, (borrowing_id,))

                # Update book availability
                c.execute("""
                UPDATE books 
                SET available = available + 1 
                WHERE id = ?
                """, (book_id,))

                conn.commit()
                return True, "Book returned successfully"
        except Exception as e:
            return False, str(e)

    def get_user_borrowings(self, username):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
            SELECT b.id, bk.title, bk.author, b.borrow_date, b.due_date, b.return_date
            FROM borrowings b
            JOIN books bk ON b.book_id = bk.id
            WHERE b.username = ?
            ORDER BY b.borrow_date DESC
            """, (username,))
            return c.fetchall()

    def get_available_books(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
            SELECT id, title, author, available
            FROM books
            WHERE available > 0
            ORDER BY title
            """)
            return c.fetchall()

class BorrowGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.borrow_system = BorrowReturnSystem()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Borrow Books")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")

        # Main container
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        # Title
        title = tk.Label(
            main_container,
            text="Available Books",
            font=("Segoe UI", 24, "bold"),
            bg="#f0f2f5",
            fg="#1a73e8"
        )
        title.pack(pady=(0, 20))

        # Search frame
        search_frame = tk.Frame(main_container, bg="#f0f2f5")
        search_frame.pack(fill="x", pady=(0, 20))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            width=40
        )
        search_entry.pack(side="left", padx=(0, 10))

        # Treeview for available books
        self.tree = ttk.Treeview(
            main_container,
            columns=("ID", "Title", "Author", "Available"),
            show="headings",
            height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Available", text="Available")

        # Set column widths
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=400)
        self.tree.column("Author", width=200)
        self.tree.column("Available", width=100)

        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Borrow button
        borrow_btn = tk.Button(
            main_container,
            text="Borrow Selected Book",
            command=self.borrow_selected_book,
            font=("Segoe UI", 12, "bold"),
            bg="#4a9eff",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        borrow_btn.pack(pady=20)

        # Load initial data
        self.load_available_books()

    def load_available_books(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load available books
        books = self.borrow_system.get_available_books()
        for book in books:
            self.tree.insert("", "end", values=book)

    def on_search_change(self, *args):
        query = self.search_var.get().lower()
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load filtered books
        books = self.borrow_system.get_available_books()
        for book in books:
            if query in book[1].lower() or query in book[2].lower():
                self.tree.insert("", "end", values=book)

    def borrow_selected_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to borrow")
            return

        book_id = self.tree.item(selected[0])["values"][0]
        success, message = self.borrow_system.borrow_book(book_id, self.username)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_available_books()
        else:
            messagebox.showerror("Error", message)

class ReturnGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.borrow_system = BorrowReturnSystem()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Return Books")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")

        # Main container
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        # Title
        title = tk.Label(
            main_container,
            text="Your Borrowed Books",
            font=("Segoe UI", 24, "bold"),
            bg="#f0f2f5",
            fg="#1a73e8"
        )
        title.pack(pady=(0, 20))

        # Treeview for borrowed books
        self.tree = ttk.Treeview(
            main_container,
            columns=("ID", "Title", "Author", "Borrow Date", "Due Date", "Status"),
            show="headings",
            height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Borrow Date", text="Borrow Date")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")

        # Set column widths
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=300)
        self.tree.column("Author", width=200)
        self.tree.column("Borrow Date", width=150)
        self.tree.column("Due Date", width=150)
        self.tree.column("Status", width=100)

        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Return button
        return_btn = tk.Button(
            main_container,
            text="Return Selected Book",
            command=self.return_selected_book,
            font=("Segoe UI", 12, "bold"),
            bg="#34a853",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        return_btn.pack(pady=20)

        # Load initial data
        self.load_borrowed_books()

    def load_borrowed_books(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load borrowed books
        borrowings = self.borrow_system.get_user_borrowings(self.username)
        for b in borrowings:
            status = "Returned" if b[5] else "Borrowed"
            self.tree.insert("", "end", values=(
                b[0],  # borrowing id
                b[1],  # title
                b[2],  # author
                b[3],  # borrow date
                b[4],  # due date
                status
            ))

    def return_selected_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to return")
            return

        borrowing_id = self.tree.item(selected[0])["values"][0]
        success, message = self.borrow_system.return_book(borrowing_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_borrowed_books()
        else:
            messagebox.showerror("Error", message)

class HistoryGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.borrow_system = BorrowReturnSystem()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Borrowing History")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")

        # Main container
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        # Title
        title = tk.Label(
            main_container,
            text="Your Borrowing History",
            font=("Segoe UI", 24, "bold"),
            bg="#f0f2f5",
            fg="#1a73e8"
        )
        title.pack(pady=(0, 20))

        # Treeview for history
        self.tree = ttk.Treeview(
            main_container,
            columns=("Title", "Author", "Borrow Date", "Due Date", "Return Date", "Status"),
            show="headings",
            height=20
        )

        # Configure columns
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Borrow Date", text="Borrow Date")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Return Date", text="Return Date")
        self.tree.heading("Status", text="Status")

        # Set column widths
        self.tree.column("Title", width=300)
        self.tree.column("Author", width=200)
        self.tree.column("Borrow Date", width=150)
        self.tree.column("Due Date", width=150)
        self.tree.column("Return Date", width=150)
        self.tree.column("Status", width=100)

        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_history()

    def load_history(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load history
        borrowings = self.borrow_system.get_user_borrowings(self.username)
        for b in borrowings:
            status = "Returned" if b[5] else "Borrowed"
            return_date = b[5] if b[5] else "Not returned"
            self.tree.insert("", "end", values=(
                b[1],  # title
                b[2],  # author
                b[3],  # borrow date
                b[4],  # due date
                return_date,
                status
            )) 