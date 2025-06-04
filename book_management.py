import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class BookManagement:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.init_book_table()
        self.add_sample_books()

    def init_book_table(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # Drop the existing table if it exists to recreate with correct structure
            c.execute("DROP TABLE IF EXISTS books")
            c.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                genre TEXT,
                publication_year INTEGER,
                quantity INTEGER DEFAULT 1,
                available INTEGER DEFAULT 1,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

    def add_sample_books(self):
        sample_books = [
            ("To Kill a Mockingbird", "Harper Lee", "9780446310789", "Fiction", 1960, 5),
            ("1984", "George Orwell", "9780451524935", "Dystopian", 1949, 3),
            ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Fiction", 1925, 4),
            ("Pride and Prejudice", "Jane Austen", "9780141439518", "Romance", 1813, 2),
            ("The Hobbit", "J.R.R. Tolkien", "9780547928227", "Fantasy", 1937, 6),
            ("The Catcher in the Rye", "J.D. Salinger", "9780316769488", "Fiction", 1951, 3),
            ("The Lord of the Rings", "J.R.R. Tolkien", "9780544003415", "Fantasy", 1954, 4),
            ("The Alchemist", "Paulo Coelho", "9780062315007", "Fiction", 1988, 5),
            ("The Little Prince", "Antoine de Saint-Exupéry", "9780156013987", "Fable", 1943, 3),
            ("The Da Vinci Code", "Dan Brown", "9780307474278", "Thriller", 2003, 4)
        ]

        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            for book in sample_books:
                try:
                    c.execute("""
                    INSERT INTO books 
                    (title, author, isbn, genre, publication_year, quantity)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, book)
                except sqlite3.Error as e:
                    print(f"Error adding book {book[0]}: {e}")
            conn.commit()

    def add_book(self, title, author, isbn, genre, publication_year, quantity):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                INSERT INTO books (title, author, isbn, genre, publication_year, quantity)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (title, author, isbn, genre, publication_year, quantity))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_all_books(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM books ORDER BY title")
            return c.fetchall()

    def search_books(self, query):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR genre LIKE ?
            ORDER BY title
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            return c.fetchall()

    def update_book(self, book_id, title, author, isbn, genre, publication_year, quantity):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                UPDATE books 
                SET title=?, author=?, isbn=?, genre=?, publication_year=?, quantity=?
                WHERE id=?
                """, (title, author, isbn, genre, publication_year, quantity, book_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_book(self, book_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM books WHERE id=?", (book_id,))
            conn.commit()
            return c.rowcount > 0

class BookManagementGUI:
    def __init__(self, root):
        self.root = root
        self.book_manager = BookManagement()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Book Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f2f5")

        # Create main container
        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        # Title
        title = tk.Label(
            main_container,
            text="Book Management System",
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

        # Treeview for books
        self.tree = ttk.Treeview(
            main_container,
            columns=("ID", "Title", "Author", "ISBN", "Genre", "Year", "Quantity", "Available"),
            show="headings",
            height=20
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("ISBN", text="ISBN")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Available", text="Available")

        # Set column widths
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=300)
        self.tree.column("Author", width=200)
        self.tree.column("ISBN", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Year", width=80)
        self.tree.column("Quantity", width=80)
        self.tree.column("Available", width=80)

        self.tree.pack(fill="both", expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Button frame
        button_frame = tk.Frame(main_container, bg="#f0f2f5")
        button_frame.pack(pady=20)

        # Add buttons
        ttk.Button(
            button_frame,
            text="Add Book",
            command=self.show_add_book_dialog
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Edit Book",
            command=self.show_edit_book_dialog
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Delete Book",
            command=self.delete_selected_book
        ).pack(side="left", padx=5)

        # Load initial data
        self.load_books()

    def load_books(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load books
        books = self.book_manager.get_all_books()
        for book in books:
            self.tree.insert("", "end", values=book)

    def on_search_change(self, *args):
        query = self.search_var.get()
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load filtered books
        books = self.book_manager.search_books(query)
        for book in books:
            self.tree.insert("", "end", values=book)

    def show_add_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("400x500")
        dialog.configure(bg="#f0f2f5")

        # Add input fields
        fields = [
            ("Title:", "title"),
            ("Author:", "author"),
            ("ISBN:", "isbn"),
            ("Genre:", "genre"),
            ("Publication Year:", "year"),
            ("Quantity:", "quantity")
        ]

        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(
                dialog,
                text=label,
                font=("Segoe UI", 10),
                bg="#f0f2f5"
            ).pack(pady=(20 if i == 0 else 10, 5))

            entry = ttk.Entry(dialog, width=40)
            entry.pack()
            entries[field] = entry

        def save_book():
            try:
                self.book_manager.add_book(
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["isbn"].get(),
                    entries["genre"].get(),
                    int(entries["year"].get()),
                    int(entries["quantity"].get())
                )
                self.load_books()
                dialog.destroy()
                messagebox.showinfo("Success", "Book added successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for year and quantity")

        ttk.Button(
            dialog,
            text="Save",
            command=save_book
        ).pack(pady=20)

    def show_edit_book_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return

        book_id = self.tree.item(selected[0])["values"][0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Book")
        dialog.geometry("400x500")
        dialog.configure(bg="#f0f2f5")

        # Add input fields
        fields = [
            ("Title:", "title"),
            ("Author:", "author"),
            ("ISBN:", "isbn"),
            ("Genre:", "genre"),
            ("Publication Year:", "year"),
            ("Quantity:", "quantity")
        ]

        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(
                dialog,
                text=label,
                font=("Segoe UI", 10),
                bg="#f0f2f5"
            ).pack(pady=(20 if i == 0 else 10, 5))

            entry = ttk.Entry(dialog, width=40)
            entry.pack()
            entries[field] = entry

        # Load current values
        current_values = self.tree.item(selected[0])["values"]
        entries["title"].insert(0, current_values[1])
        entries["author"].insert(0, current_values[2])
        entries["isbn"].insert(0, current_values[3])
        entries["genre"].insert(0, current_values[4])
        entries["year"].insert(0, current_values[5])
        entries["quantity"].insert(0, current_values[6])

        def save_changes():
            try:
                self.book_manager.update_book(
                    book_id,
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["isbn"].get(),
                    entries["genre"].get(),
                    int(entries["year"].get()),
                    int(entries["quantity"].get())
                )
                self.load_books()
                dialog.destroy()
                messagebox.showinfo("Success", "Book updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for year and quantity")

        ttk.Button(
            dialog,
            text="Save Changes",
            command=save_changes
        ).pack(pady=20)

    def delete_selected_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?"):
            book_id = self.tree.item(selected[0])["values"][0]
            if self.book_manager.delete_book(book_id):
                self.load_books()
                messagebox.showinfo("Success", "Book deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete book")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookManagementGUI(root)
    root.mainloop() 