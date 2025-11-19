import logging
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from db_init import DB_NAME
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

# Simple logging for debugging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

# Configure Treeview heading style so column headers are visible (white on black)
try:
    _style = ttk.Style()
    # Use default theme for predictable styling
    try:
        _style.theme_use('default')
    except Exception:
        pass
    _style.configure("Treeview.Heading", background="#000000", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
    _style.configure("Treeview", font=("Segoe UI", 10), foreground="#111111")
    # Ensure heading maps are set for active/pressed states
    _style.map("Treeview.Heading",
               background=[('active', '#000000'), ('pressed', '#111111')],
               foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
except Exception:
    logger.exception("Failed to configure Treeview heading style")

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
        logger.debug("borrow_book called with book_id=%s username=%s", book_id, username)
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                logger.debug("Executing SELECT available FROM books WHERE id = %s", book_id)
                c.execute("SELECT available FROM books WHERE id = ?", (book_id,))
                result = c.fetchone()
                logger.debug("Availability result: %s", result)
                if not result or result[0] <= 0:
                    logger.info("Book %s not available to borrow", book_id)
                    return False, "Book is not available for borrowing"
                due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                logger.debug("Inserting borrowing record for user %s book %s", username, book_id)
                c.execute("""
                INSERT INTO borrowings (book_id, username, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
                """, (book_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), due_date))
                logger.debug("Decrementing available count for book %s", book_id)
                c.execute("UPDATE books SET available = available - 1 WHERE id = ?", (book_id,))
                conn.commit()
                logger.info("Borrowed book ID %s for user %s", book_id, username)
                return True, "Book borrowed successfully"
        except sqlite3.Error as e:
            logger.exception("Error borrowing book: %s", e)
            return False, f"Database error: {e}"

    def return_book(self, borrowing_id):
        logger.debug("return_book called with borrowing_id=%s", borrowing_id)
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                logger.debug("Selecting borrowing row for id %s", borrowing_id)
                c.execute("SELECT book_id, return_date, due_date FROM borrowings WHERE id = ?", (borrowing_id,))
                result = c.fetchone()
                logger.debug("Borrowing row: %s", result)
                if not result:
                    logger.info("Borrowing ID %s not found", borrowing_id)
                    return False, "Borrowing record not found"
                if result[1] is not None:
                    logger.info("Borrowing ID %s already returned", borrowing_id)
                    return False, "Book already returned"
                book_id, _, due_date = result
                return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fine = self.calculate_fine(due_date, return_date)
                logger.debug("Updating borrowings return_date and fine for id %s", borrowing_id)
                c.execute("UPDATE borrowings SET return_date = ?, fine = ? WHERE id = ?", (return_date, fine, borrowing_id))
                logger.debug("Incrementing available for book %s", book_id)
                c.execute("UPDATE books SET available = available + 1 WHERE id = ?", (book_id,))
                conn.commit()
                logger.info("Returned book ID %s for borrowing ID %s with fine Rs. %s", book_id, borrowing_id, fine)
                return True, f"Book returned successfully{f'. Fine: Rs. {fine}' if fine > 0 else ''}"
        except sqlite3.Error as e:
            logger.exception("Error returning book: %s", e)
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
                rows = c.fetchall()
                logger.debug("get_user_borrowings for %s returned %d rows", username, len(rows))
                return rows
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
                rows = c.fetchall()
                logger.debug("get_unreturned_borrowings for %s returned %d rows", username, len(rows))
                return rows
        except sqlite3.Error as e:
            print(f"Error fetching unreturned borrowings: {e}")
            return []

    def get_available_books(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT id, title, author, available FROM books WHERE available > 0 ORDER BY title")
                rows = c.fetchall()
                logger.debug("get_available_books returned %d books", len(rows))
                return rows
        except sqlite3.Error as e:
            print(f"Error fetching available books: {e}")
            return []

    def get_recommended_books(self, username, top_n=5):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # Get all unique users and books
                c.execute("SELECT DISTINCT username FROM users")
                users = [row[0] for row in c.fetchall()]
                c.execute("SELECT DISTINCT id FROM books")
                books = [row[0] for row in c.fetchall()]
                if not users or not books:
                    return []
                user_map = {u: i for i, u in enumerate(users)}
                book_map = {b: i for i, b in enumerate(books)}
                # Get interactions (binary: 1 if borrowed)
                c.execute("SELECT DISTINCT username, book_id, 1 as interaction FROM borrowings")
                data = c.fetchall()
                if not data:
                    # Fallback to popular books
                    c.execute("""
                    SELECT book_id, COUNT(*) as borrows
                    FROM borrowings
                    GROUP BY book_id
                    ORDER BY borrows DESC
                    LIMIT ?
                    """, (top_n,))
                    pop = c.fetchall()
                    recs = [row[0] for row in pop]
                    if recs:
                        c.execute("SELECT id, title, author FROM books WHERE id IN ({})".format(','.join('?' for _ in recs)), recs)
                        return c.fetchall()
                    else:
                        return []
                # Build sparse matrix (FIX: Use float64 dtype for SVD compatibility)
                rows = []
                cols = []
                vals = []
                for u, b, inter in data:
                    if u in user_map and b in book_map:
                        rows.append(user_map[u])
                        cols.append(book_map[b])
                        vals.append(inter)
                matrix = csr_matrix((vals, (rows, cols)), shape=(len(users), len(books)), dtype=np.float64)
                # SVD decomposition
                k = min(50, min(matrix.shape[0], matrix.shape[1]) - 1)
                U, sigma, Vt = svds(matrix, k=k)
                sigma_diag = np.diag(sigma)
                predicted = np.dot(np.dot(U, sigma_diag), Vt)
                user_idx = user_map.get(username)
                if user_idx is None:
                    return []
                user_preds = predicted[user_idx, :]
                # Get books already borrowed
                c.execute("SELECT DISTINCT book_id FROM borrowings WHERE username = ?", (username,))
                borrowed = set(row[0] for row in c.fetchall())
                # Get top recommendations
                rec_indices = np.argsort(user_preds)[::-1]
                rec_books = []
                for idx in rec_indices:
                    book_id = books[idx]
                    if book_id not in borrowed:
                        rec_books.append(book_id)
                    if len(rec_books) == top_n:
                        break
                # Get book details
                if rec_books:
                    placeholders = ','.join('?' for _ in rec_books)
                    c.execute(f"SELECT id, title, author FROM books WHERE id IN ({placeholders})", rec_books)
                    return c.fetchall()
                else:
                    return []
        except Exception as e:
            print(f"Error in recommendations: {e}")
            return []

class BorrowGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.borrow_system = BorrowReturnSystem()
        self.setup_gui()

    def setup_gui(self):
        logger.debug("Opening BorrowGUI for user %s", self.username)
        self.root.title("Borrow Books")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")

        # Create main container but defer packing until control bar is created
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)

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
        # Tree view placed above a bottom control bar so action buttons remain visible
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        # Bindings for selection and double-click to borrow
        self.tree.bind("<Double-1>", lambda e: self.borrow_selected_book())
        self.tree.bind("<<TreeviewSelect>>", lambda e: logger.debug("Tree selection changed: %s", self.tree.selection()))

        # Bottom control bar: pack BEFORE the main_container so it reserves space at bottom
        control_bar = tk.Frame(self.root, bg="#f0f2f5", padx=10, pady=8)
        control_bar.pack(side="bottom", fill="x")
        control_bar.configure(relief="raised", bd=1)
        control_bar.lift()

        help_lbl = tk.Label(control_bar, text="Select a row and click 'Borrow Selected Book' (or press Enter)", font=("Segoe UI", 10), bg="#f0f2f5", fg="#495057")
        help_lbl.pack(side="left")

        borrow_btn = tk.Button(control_bar, text="Borrow Selected Book", command=self.borrow_selected_book, font=("Segoe UI", 12, "bold"), bg="#4a9eff", fg="white", relief="flat", cursor="hand2", padx=16, pady=8)
        borrow_btn.pack(side="right", padx=6)
        back_btn = tk.Button(control_bar, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2", padx=16, pady=8)
        back_btn.pack(side="right", padx=6)

        # Now pack the main content area so it fills remaining space above control_bar
        main_container.pack(expand=True, fill="both")

        # Keyboard binding: Enter to borrow
        self.root.bind('<Return>', lambda e: self.borrow_selected_book())

        # Diagnostic: force geometry calculation and log widget visibility/positions
        try:
            self.root.update_idletasks()
            logger.debug("BorrowGUI geometry=%s", self.root.geometry())
            logger.debug("control_bar mapped=%s rooty=%s", control_bar.winfo_ismapped(), control_bar.winfo_rooty())
            logger.debug("tree height=%s reqheight=%s", self.tree.winfo_height(), self.tree.winfo_reqheight())
            children = self.tree.get_children()
            first_bbox = None
            if children:
                try:
                    first_bbox = self.tree.bbox(children[0])
                except Exception:
                    first_bbox = None
            logger.debug("tree first row bbox=%s", first_bbox)
        except Exception as e:
            logger.exception("Error during BorrowGUI diagnostics: %s", e)

        self.load_available_books()

    def load_available_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        books = self.borrow_system.get_available_books()
        logger.debug("load_available_books: %d books to show", len(books))
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
        logger.debug("borrow_selected_book selection: %s", selected)
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to borrow")
            return
        book_id = self.tree.item(selected[0])["values"][0]
        logger.debug("User %s attempting to borrow book id %s", self.username, book_id)
        success, message = self.borrow_system.borrow_book(book_id, self.username)
        logger.debug("borrow_book result: success=%s message=%s", success, message)
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
        logger.debug("Opening ReturnGUI for user %s", self.username)
        self.root.title("Return Books")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")
        # Create main container but defer packing until control bar is created
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)

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

        # Bottom control bar for return: pack BEFORE the main_container so it reserves bottom space
        control_bar = tk.Frame(self.root, bg="#f0f2f5", padx=10, pady=8)
        control_bar.pack(side="bottom", fill="x")
        control_bar.configure(relief="raised", bd=1)
        control_bar.lift()

        help_lbl = tk.Label(control_bar, text="Select a borrowed row and click 'Return Selected Book'", font=("Segoe UI", 10), bg="#f0f2f5", fg="#495057")
        help_lbl.pack(side="left")

        return_btn = tk.Button(control_bar, text="Return Selected Book", command=self.return_selected_book, font=("Segoe UI", 12, "bold"), bg="#34a853", fg="white", relief="flat", cursor="hand2", padx=16, pady=8)
        return_btn.pack(side="right", padx=6)
        back_btn = tk.Button(control_bar, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2", padx=16, pady=8)
        back_btn.pack(side="right", padx=6)

        # Now pack the main content area so it fills remaining space above control_bar
        main_container.pack(expand=True, fill="both")

        # Keyboard binding: Enter to return
        self.root.bind('<Return>', lambda e: self.return_selected_book())

        self.load_borrowed_books()

    def load_borrowed_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        borrowings = self.borrow_system.get_unreturned_borrowings(self.username)
        logger.debug("load_borrowed_books: %d borrowings to show for user %s", len(borrowings), self.username)
        for b in borrowings:
            self.tree.insert("", "end", values=b)

    def return_selected_book(self):
        selected = self.tree.selection()
        logger.debug("return_selected_book selection: %s", selected)
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to return")
            return
        borrowing_id = self.tree.item(selected[0])["values"][0]
        logger.debug("User %s attempting to return borrowing id %s", self.username, borrowing_id)
        # Pre-check: fetch due_date and calculate potential fine to confirm with user
        fine = 0
        try:
            with sqlite3.connect(self.borrow_system.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT due_date FROM borrowings WHERE id = ?", (borrowing_id,))
                row = c.fetchone()
                if row and row[0]:
                    due_date = row[0]
                    fine = self.borrow_system.calculate_fine(due_date)
                else:
                    fine = 0
        except sqlite3.Error as e:
            logger.exception("Error fetching due_date for borrowing id %s: %s", borrowing_id, e)
            messagebox.showerror("Error", "Unable to verify due date. Please try again.")
            return

        if fine > 0:
            proceed = messagebox.askyesno("Fine Payment Required", f"This book is overdue. A fine of Rs. {fine} is due. Do you want to proceed with the return and pay the fine?")
            if not proceed:
                messagebox.showinfo("Return Cancelled", "Return cancelled. Please clear the fine before returning the book.")
                return

        success, message = self.borrow_system.return_book(borrowing_id)
        logger.debug("return_book result: success=%s message=%s", success, message)
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

class RecommendationsGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.borrow_system = BorrowReturnSystem()
        self.setup_gui()

    def setup_gui(self):
        logger.debug("Opening RecommendationsGUI for user %s", self.username)
        self.root.title("Book Recommendations")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)

        title = tk.Label(main_container, text="Recommended Books for You", font=("Segoe UI", 24, "bold"), bg="#f0f2f5", fg="#1a73e8")
        title.pack(pady=(0, 20))

        self.tree = ttk.Treeview(main_container, columns=("ID", "Title", "Author"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=400)
        self.tree.column("Author", width=200)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bottom control bar for recommendations: pack BEFORE the main_container so it reserves bottom space
        control_bar = tk.Frame(self.root, bg="#f0f2f5", padx=10, pady=8)
        control_bar.pack(side="bottom", fill="x")

        help_lbl = tk.Label(control_bar, text="Select a recommended book and click 'Borrow Selected'", font=("Segoe UI", 10), bg="#f0f2f5", fg="#495057")
        help_lbl.pack(side="left")

        borrow_btn = tk.Button(control_bar, text="Borrow Selected", command=self.borrow_selected, font=("Segoe UI", 12, "bold"), bg="#4a9eff", fg="white", relief="flat", cursor="hand2", padx=16, pady=8)
        borrow_btn.pack(side="right", padx=6)
        back_btn = tk.Button(control_bar, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2", padx=16, pady=8)
        back_btn.pack(side="right", padx=6)

        # Now pack the main content area so it fills remaining space above control_bar
        main_container.pack(expand=True, fill="both")

        # Keyboard binding: Enter to borrow from recommendations
        self.root.bind('<Return>', lambda e: self.borrow_selected())

        self.load_recommendations()

    def load_recommendations(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        recs = self.borrow_system.get_recommended_books(self.username)
        logger.debug("load_recommendations returned %d recommendations for %s", len(recs), self.username)
        for rec in recs:
            self.tree.insert("", "end", values=rec)
        if not recs:
            messagebox.showinfo("Info", "No recommendations available yet. Borrow some books to get personalized suggestions!")

    def borrow_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to borrow")
            return
        book_id = self.tree.item(selected[0])["values"][0]
        logger.debug("Recommendations borrow_selected chosen book_id=%s for user=%s", book_id, self.username)
        # Check availability
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT available FROM books WHERE id = ?", (book_id,))
            result = c.fetchone()
            if not result or result[0] <= 0:
                messagebox.showerror("Error", "Book not available")
                return
        success, message = self.borrow_system.borrow_book(book_id, self.username)
        if success:
            messagebox.showinfo("Success", message)
            self.load_recommendations()
        else:
            messagebox.showerror("Error", message)
