import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from db_init import DB_NAME

class BorrowReturnSystem:
    def __init__(self):
        self.db_name = DB_NAME

    def calculate_fine(self, due_date, return_date=None):
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(return_date, "%Y-%m-%d %H:%M:%S") if return_date else datetime.now()
            days_overdue = (end - due).days
            if days_overdue > 14:
                return (days_overdue - 14) * 10  # Rs. 10 per day after 14 days
            return 0
        except ValueError as e:
            print(f"Error parsing dates for fine calculation: {e}")
            return 0

    def update_fines(self, borrowing_id=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                if borrowing_id:
                    c.execute("SELECT due_date, return_date FROM borrowings WHERE id = ?", (borrowing_id,))
                    due_date, return_date = c.fetchone()
                    fine = self.calculate_fine(due_date, return_date)
                    c.execute("UPDATE borrowings SET fine = ? WHERE id = ?", (fine, borrowing_id))
                else:
                    c.execute("SELECT id, due_date, return_date FROM borrowings WHERE return_date IS NULL")
                    for borrowing_id, due_date, _ in c.fetchall():
                        fine = self.calculate_fine(due_date)
                        c.execute("UPDATE borrowings SET fine = ? WHERE id = ?", (fine, borrowing_id))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating fines: {e}")

    def borrow_book(self, book_id, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT available FROM books WHERE id = ?", (book_id,))
                result = c.fetchone()
                if not result or result[0] <= 0:
                    return False, "Book is not available for borrowing"
                due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                c.execute("""
                INSERT INTO borrowings (book_id, username, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
                """, (book_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), due_date))
                c.execute("UPDATE books SET available = available - 1 WHERE id = ?", (book_id,))
                conn.commit()
                print(f"Borrowed book ID {book_id} for user {username}")
                return True, "Book borrowed successfully"
        except sqlite3.Error as e:
            print(f"Error borrowing book: {e}")
            return False, f"Database error: {e}"

    def return_book(self, borrowing_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT book_id, return_date, due_date FROM borrowings WHERE id = ?", (borrowing_id,))
                result = c.fetchone()
                if not result:
                    print(f"Borrowing ID {borrowing_id} not found")
                    return False, "Borrowing record not found"
                if result[1] is not None:
                    print(f"Borrowing ID {borrowing_id} already returned")
                    return False, "Book already returned"
                book_id, _, due_date = result
                return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fine = self.calculate_fine(due_date, return_date)
                c.execute("UPDATE borrowings SET return_date = ?, fine = ? WHERE id = ?", (return_date, fine, borrowing_id))
                c.execute("UPDATE books SET available = available + 1 WHERE id = ?", (book_id,))
                conn.commit()
                print(f"Returned book ID {book_id} for borrowing ID {borrowing_id} with fine Rs. {fine}")
                return True, f"Book returned successfully{f'. Fine: Rs. {fine}' if fine > 0 else ''}"
        except sqlite3.Error as e:
            print(f"Error returning book: {e}")
            return False, f"Database error: {e}"

    def get_user_borrowings(self, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                SELECT b.id, bk.title, bk.author, b.borrow_date, b.due_date, b.return_date, b.fine
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.id
                WHERE b.username = ?
                ORDER BY b.borrow_date DESC
                """, (username,))
                return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching borrowings: {e}")
            return []

    def get_unreturned_borrowings(self, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                SELECT b.id, bk.title, bk.author, b.borrow_date, b.due_date
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.id
                WHERE b.username = ? AND b.return_date IS NULL
                ORDER BY b.borrow_date DESC
                """, (username,))
                return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching unreturned borrowings: {e}")
            return []

    def get_available_books(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT id, title, author, available FROM books WHERE available > 0 ORDER BY title")
                return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching available books: {e}")
            return []

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

        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        title = tk.Label(main_container, text="Available Books", font=("Segoe UI", 24, "bold"), bg="#f0f2f5", fg="#1a73e8")
        title.pack(pady=(0, 20))

        search_frame = tk.Frame(main_container, bg="#f0f2f5")
        search_frame.pack(fill="x", pady=(0, 20))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 12), width=40)
        search_entry.pack(side="left", padx=(0, 10))

        self.tree = ttk.Treeview(main_container, columns=("ID", "Title", "Author", "Available"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Available", text="Available")
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=400)
        self.tree.column("Author", width=200)
        self.tree.column("Available", width=100)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(main_container, text="Borrow Selected Book", command=self.borrow_selected_book, font=("Segoe UI", 12, "bold"), bg="#4a9eff", fg="white", relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)
        tk.Button(main_container, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)

        self.load_available_books()

    def load_available_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        books = self.borrow_system.get_available_books()
        for book in books:
            self.tree.insert("", "end", values=book)

    def on_search_change(self, *args):
        query = self.search_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
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

        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        title = tk.Label(main_container, text="Your Borrowed Books", font=("Segoe UI", 24, "bold"), bg="#f0f2f5", fg="#1a73e8")
        title.pack(pady=(0, 20))

        self.tree = ttk.Treeview(main_container, columns=("ID", "Title", "Author", "Borrow Date", "Due Date"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Borrow Date", text="Borrow Date")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=300)
        self.tree.column("Author", width=200)
        self.tree.column("Borrow Date", width=150)
        self.tree.column("Due Date", width=150)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(main_container, text="Return Selected Book", command=self.return_selected_book, font=("Segoe UI", 12, "bold"), bg="#34a853", fg="white", relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)
        tk.Button(main_container, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)

        self.load_borrowed_books()

    def load_borrowed_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        borrowings = self.borrow_system.get_unreturned_borrowings(self.username)
        for b in borrowings:
            self.tree.insert("", "end", values=b)

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

        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        title = tk.Label(main_container, text="Your Borrowing History", font=("Segoe UI", 24, "bold"), bg="#f0f2f5", fg="#1a73e8")
        title.pack(pady=(0, 20))

        self.tree = ttk.Treeview(main_container, columns=("Title", "Author", "Borrow Date", "Due Date", "Return Date", "Fine"), show="headings", height=20)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Borrow Date", text="Borrow Date")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Return Date", text="Return Date")
        self.tree.heading("Fine", text="Fine (Rs.)")
        self.tree.column("Title", width=300)
        self.tree.column("Author", width=200)
        self.tree.column("Borrow Date", width=150)
        self.tree.column("Due Date", width=150)
        self.tree.column("Return Date", width=150)
        self.tree.column("Fine", width=100)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(main_container, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2", padx=20, pady=10).pack(pady=10)

        self.load_history()

    def load_history(self):
        self.borrow_system.update_fines()  # Update fines before displaying
        for item in self.tree.get_children():
            self.tree.delete(item)
        borrowings = self.borrow_system.get_user_borrowings(self.username)
        for b in borrowings:
            return_date = b[5] if b[5] else "Not returned"
            fine = b[6]
            self.tree.insert("", "end", values=(b[1], b[2], b[3], b[4], return_date, fine))