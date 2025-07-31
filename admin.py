import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from db_init import DB_NAME

class AdminPanel:
    def __init__(self, root, username, return_to_dashboard):
        self.root = root
        self.username = username
        self.return_to_dashboard = return_to_dashboard
        self.db_name = DB_NAME
        self.setup_styles()
        self.setup_gui()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
        self.style.configure("TLabel", font=("Segoe UI", 12), background="#ffffff")
        self.style.configure("Treeview", font=("Segoe UI", 12), rowheight=30)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#20c997", foreground="white")

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

    def refresh_book_list(self, search_term=""):
        for widget in self.book_list_frame.winfo_children():
            widget.destroy()
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                if search_term:
                    query = f"%{search_term.lower()}%"
                    c.execute("""
                    SELECT id, title, author, genre, isbn, publication_year, quantity, available 
                    FROM books 
                    WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(genre) LIKE ? OR LOWER(isbn) LIKE ?
                    """, (query, query, query, query))
                else:
                    c.execute("SELECT id, title, author, genre, isbn, publication_year, quantity, available FROM books")
                books = c.fetchall()
            for book in books:
                book_id, title, author, genre, isbn, pub_year, quantity, available = book
                row = tk.Frame(self.book_list_frame, bg="white", relief="flat", highlightbackground="#20c997", highlightthickness=2)
                row.pack(fill="x", pady=8, padx=10)
                tk.Label(row, text=f"{title} by {author} ({genre}, ISBN: {isbn})", bg="white", font=("Segoe UI", 12)).pack(side="left", padx=15)
                tk.Label(row, text=f"Qty: {quantity}, Avail: {available}", bg="white", font=("Segoe UI", 12)).pack(side="left", padx=15)
                tk.Button(row, text="Edit", command=lambda b=book_id: self.edit_book(b), bg="#007bff", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=6, cursor="hand2").pack(side="right", padx=5)
                tk.Button(row, text="Delete", command=lambda b=book_id: self.delete_book(b), bg="#dc3545", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=6, cursor="hand2").pack(side="right", padx=5)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load books: {e}")

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        isbn = self.isbn_entry.get()
        genre = self.genre_entry.get()
        pub_year = self.pub_year_entry.get()
        quantity = self.quantity_entry.get()
        if not (title and author and isbn and quantity):
            messagebox.showwarning("Warning", "Please fill in all required fields (Title, Author, ISBN, Quantity)")
            return
        try:
            quantity = int(quantity)
            pub_year = int(pub_year) if pub_year else None
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                INSERT INTO books (title, author, isbn, genre, publication_year, quantity, available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, author, isbn, genre, pub_year, quantity, quantity))
                conn.commit()
            messagebox.showinfo("Success", "Book added successfully")
            self.title_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.isbn_entry.delete(0, tk.END)
            self.genre_entry.delete(0, tk.END)
            self.pub_year_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.refresh_book_list(self.search_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity and Publication Year must be valid numbers")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ISBN already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_book(self, book_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            try:
                with sqlite3.connect(self.db_name) as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
                    conn.commit()
                messagebox.showinfo("Success", "Book deleted successfully")
                self.refresh_book_list(self.search_var.get())
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete book: {e}")

    def edit_book(self, book_id):
        def save_changes():
            new_title = title_entry.get()
            new_author = author_entry.get()
            new_isbn = isbn_entry.get()
            new_genre = genre_entry.get()
            new_pub_year = pub_year_entry.get()
            new_quantity = quantity_entry.get()
            if not (new_title and new_author and new_isbn and new_quantity):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
            try:
                new_quantity = int(new_quantity)
                new_pub_year = int(new_pub_year) if new_pub_year else None
                with sqlite3.connect(self.db_name) as conn:
                    c = conn.cursor()
                    c.execute("SELECT available FROM books WHERE id = ?", (book_id,))
                    current_available = c.fetchone()[0]
                    active_borrowings = c.execute("SELECT COUNT(*) FROM borrowings WHERE book_id = ? AND return_date IS NULL", (book_id,)).fetchone()[0]
                    new_available = min(new_quantity, current_available + active_borrowings)
                    c.execute("""
                    UPDATE books SET title = ?, author = ?, isbn = ?, genre = ?, publication_year = ?, quantity = ?, available = ?
                    WHERE id = ?
                    """, (new_title, new_author, new_isbn, new_genre, new_pub_year, new_quantity, new_available, book_id))
                    conn.commit()
                messagebox.showinfo("Success", "Book updated successfully")
                edit_win.destroy()
                self.refresh_book_list(self.search_var.get())
            except ValueError:
                messagebox.showerror("Error", "Quantity and Publication Year must be valid numbers")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "ISBN already exists")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT title, author, isbn, genre, publication_year, quantity FROM books WHERE id = ?", (book_id,))
                book = c.fetchone()
            if not book:
                messagebox.showerror("Error", "Book not found")
                return

            edit_win = tk.Toplevel(self.root)
            edit_win.title("Edit Book")
            edit_win.geometry("400x350")
            edit_win.configure(bg="#e9ecef")

            tk.Label(edit_win, text="Title:", font=("Segoe UI", 12), bg="#e9ecef").grid(row=0, column=0, padx=15, pady=10, sticky="e")
            title_entry = tk.Entry(edit_win, font=("Segoe UI", 12), width=25)
            title_entry.insert(0, book[0])
            title_entry.grid(row=0, column=1, pady=10)

            tk.Label(edit_win, text="Author:", font=("Segoe UI", 12), bg="#e9ecef").grid(row=1, column=0, padx=15, pady=10, sticky="e")
            author_entry = tk.Entry(edit_win, font=("Segoe UI", 12), width=25)
            author_entry.insert(0, book[1])
            author_entry.grid(row=1, column=1, pady=10)

            tk.Label(edit_win, text="ISBN:", font=("Segoe UI", 12), bg="#e9ecef").grid(row=2, column=0, padx=15, pady=10, sticky="e")
            isbn_entry = tk.Entry(edit_win, font=("Segoe UI", 12), width=25)
            isbn_entry.insert(0, book[2])
            isbn_entry.grid(row=2, column=1, pady=10)

            tk.Label(edit_win, text="Genre:", font=("Segoe UI", 12), bg="#e9ecef").grid(row=3, column=0, padx=15, pady=10, sticky="e")
            genre_entry = tk.Entry(edit_win, font=("Segoe UI", 12), width=25)
            genre_entry.insert(0, book[3])
            genre_entry.grid(row=3, column=1, pady=10)

            tk.Label(edit_win, text="Publication Year:", font=("Segoe UI", 12), bg="#e9ecef").grid(row=4, column=0, padx=15, pady=10, sticky="e")
            pub_year_entry = tk.Entry(edit_win, font=("Segoe UI", 12), width=25)
            pub_year_entry.insert(0, book[4] if book[4] else "")
            pub_year_entry.grid(row=4, column=1, pady=10)

            tk.Label(edit_win, text="Quantity:", font=("Segoe UI", 12), bg="#e9ecef").grid(row=5, column=0, padx=15, pady=10, sticky="e")
            quantity_entry = tk.Entry(edit_win, font=("Segoe UI", 12), width=25)
            quantity_entry.insert(0, book[5])
            quantity_entry.grid(row=5, column=1, pady=10)

            tk.Button(edit_win, text="Save Changes", font=("Segoe UI", 12, "bold"), bg="#20c997", fg="white", relief="flat", padx=20, pady=10, cursor="hand2", command=save_changes).grid(row=6, column=1, pady=15)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load book: {e}")

    def view_fines(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                SELECT b.id, b.username, bk.title, b.due_date, b.return_date, b.fine
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.id
                WHERE b.fine > 0
                ORDER BY b.username, b.due_date
                """)
                fines = c.fetchall()
            fine_win = tk.Toplevel(self.root)
            fine_win.title("Fines Report")
            fine_win.geometry("800x400")
            fine_win.configure(bg="#e9ecef")

            tree = ttk.Treeview(fine_win, columns=("ID", "Username", "Book", "Due Date", "Return Date", "Fine"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("Username", text="Username")
            tree.heading("Book", text="Book Title")
            tree.heading("Due Date", text="Due Date")
            tree.heading("Return Date", text="Return Date")
            tree.heading("Fine", text="Fine (Rs.)")
            tree.column("ID", width=50)
            tree.column("Username", width=100)
            tree.column("Book", width=200)
            tree.column("Due Date", width=150)
            tree.column("Return Date", width=150)
            tree.column("Fine", width=100)
            tree.pack(fill="both", expand=True, padx=15, pady=15)

            scrollbar = ttk.Scrollbar(fine_win, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)

            for fine in fines:
                tree.insert("", "end", values=fine)

            total_fine = sum(f[5] for f in fines)
            tk.Label(fine_win, text=f"Total Fines Outstanding: Rs. {total_fine}", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#007bff").pack(pady=10)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load fines: {e}")

    def view_users(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT username, is_admin FROM users ORDER BY username")
                users = c.fetchall()
                c.execute("""
                SELECT b.id, b.username, bk.title, b.borrow_date, b.due_date, b.return_date, b.fine
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.id
                ORDER BY b.username, b.borrow_date DESC
                """)
                borrowings = c.fetchall()
            user_win = tk.Toplevel(self.root)
            user_win.title("User Information")
            user_win.geometry("900x600")
            user_win.configure(bg="#e9ecef")

            tk.Label(user_win, text="All Users", font=("Segoe UI", 16, "bold"), bg="#e9ecef", fg="#007bff").pack(anchor="w", padx=15, pady=10)
            user_tree = ttk.Treeview(user_win, columns=("Username", "Is Admin"), show="headings")
            user_tree.heading("Username", text="Username")
            user_tree.heading("Is Admin", text="Is Admin")
            user_tree.column("Username", width=200)
            user_tree.column("Is Admin", width=100)
            user_tree.pack(fill="x", padx=15, pady=10)

            user_scrollbar = ttk.Scrollbar(user_win, orient="vertical", command=user_tree.yview)
            user_scrollbar.pack(side="right", fill="y")
            user_tree.configure(yscrollcommand=user_scrollbar.set)

            for user in users:
                user_tree.insert("", "end", values=(user[0], "Yes" if user[1] else "No"))

            tk.Label(user_win, text="Borrowing History", font=("Segoe UI", 16, "bold"), bg="#e9ecef", fg="#007bff").pack(anchor="w", padx=15, pady=10)
            borrow_tree = ttk.Treeview(user_win, columns=("ID", "Username", "Book", "Borrow Date", "Due Date", "Return Date", "Fine"), show="headings")
            borrow_tree.heading("ID", text="ID")
            borrow_tree.heading("Username", text="Username")
            borrow_tree.heading("Book", text="Book Title")
            borrow_tree.heading("Borrow Date", text="Borrow Date")
            borrow_tree.heading("Due Date", text="Due Date")
            borrow_tree.heading("Return Date", text="Return Date")
            borrow_tree.heading("Fine", text="Fine (Rs.)")
            borrow_tree.column("ID", width=50)
            borrow_tree.column("Username", width=100)
            borrow_tree.column("Book", width=200)
            borrow_tree.column("Borrow Date", width=150)
            borrow_tree.column("Due Date", width=150)
            borrow_tree.column("Return Date", width=150)
            borrow_tree.column("Fine", width=100)
            borrow_tree.pack(fill="both", expand=True, padx=15, pady=10)

            borrow_scrollbar = ttk.Scrollbar(user_win, orient="vertical", command=borrow_tree.yview)
            borrow_scrollbar.pack(side="right", fill="y")
            borrow_tree.configure(yscrollcommand=borrow_scrollbar.set)

            for borrowing in borrowings:
                return_date = borrowing[5] if borrowing[5] else "Not Returned"
                borrow_tree.insert("", "end", values=(borrowing[0], borrowing[1], borrowing[2], borrowing[3], borrowing[4], return_date, borrowing[6]))

            total_fine = sum(b[6] for b in borrowings if b[6])
            tk.Label(user_win, text=f"Total Fines Across All Users: Rs. {total_fine}", font=("Segoe UI", 12, "bold"), bg="#e9ecef", fg="#007bff").pack(pady=10)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load user information: {e}")

    def setup_gui(self):
        self.root.title("Admin Panel - A&Y Library")
        self.root.geometry("900x700")
        self.root.configure(bg="#e9ecef")

        # Header
        header_frame = tk.Frame(self.root, bg="#007bff")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Admin Panel", font=("Segoe UI", 24, "bold"), bg="#007bff", fg="white").pack(side="left", padx=20, pady=15)
        tk.Button(header_frame, text="Back to Dashboard", command=self.return_to_dashboard, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right", padx=10)
        tk.Button(header_frame, text="View Users", command=self.view_users, font=("Segoe UI", 12, "bold"), bg="#17a2b8", fg="white", relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right", padx=10)
        tk.Button(header_frame, text="View Fines", command=self.view_fines, font=("Segoe UI", 12, "bold"), bg="#ffc107", fg="white", relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right", padx=10)

        # Search Bar
        search_frame = tk.Frame(self.root, bg="#e9ecef")
        search_frame.pack(fill="x", pady=15)
        tk.Label(search_frame, text="Search Books:", font=("Segoe UI", 12, "bold"), bg="#e9ecef").pack(side="left", padx=15)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_book_list(self.search_var.get()))
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 12), width=30)
        search_entry.pack(side="left", padx=15)

        # Add Book Form
        form_frame = tk.Frame(self.root, bg="white", padx=25, pady=20, relief="flat", highlightbackground="#20c997", highlightthickness=2)
        form_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(form_frame, text="Title:", font=("Segoe UI", 12), bg="white").grid(row=0, column=0, padx=15, pady=8, sticky="e")
        self.title_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=25)
        self.title_entry.grid(row=0, column=1, pady=8)
        tk.Label(form_frame, text="Author:", font=("Segoe UI", 12), bg="white").grid(row=0, column=2, padx=15, pady=8, sticky="e")
        self.author_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=25)
        self.author_entry.grid(row=0, column=3, pady=8)
        tk.Label(form_frame, text="ISBN:", font=("Segoe UI", 12), bg="white").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.isbn_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=25)
        self.isbn_entry.grid(row=1, column=1, pady=8)
        tk.Label(form_frame, text="Genre:", font=("Segoe UI", 12), bg="white").grid(row=1, column=2, padx=15, pady=8, sticky="e")
        self.genre_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=25)
        self.genre_entry.grid(row=1, column=3, pady=8)
        tk.Label(form_frame, text="Pub Year:", font=("Segoe UI", 12), bg="white").grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.pub_year_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=25)
        self.pub_year_entry.grid(row=2, column=1, pady=8)
        tk.Label(form_frame, text="Quantity:", font=("Segoe UI", 12), bg="white").grid(row=2, column=2, padx=15, pady=8, sticky="e")
        self.quantity_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=25)
        self.quantity_entry.grid(row=2, column=3, pady=8)
        tk.Button(form_frame, text="Add Book", command=self.add_book, font=("Segoe UI", 12, "bold"), bg="#20c997", fg="white", relief="flat", padx=20, pady=10, cursor="hand2").grid(row=3, column=3, pady=15, sticky="e")

        # Book List
        canvas_frame = tk.Frame(self.root, bg="#e9ecef")
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=15)
        canvas = tk.Canvas(canvas_frame, bg="#e9ecef", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.book_list_frame = tk.Frame(canvas, bg="#e9ecef")
        self.book_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.book_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_book_list()