import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db_init import DB_NAME

class BookManagement:
    def __init__(self):
        self.db_name = DB_NAME
        self.add_sample_books()

    def add_sample_books(self):
        sample_books = [
            ("To Kill a Mockingbird", "Harper Lee", "9780446310789", "Fiction", 1960, 5),
            ("1984", "George Orwell", "9780451524935", "Dystopian", 1949, 3),
            ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Fiction", 1925, 4),
            ("Pride and Prejudice", "Jane Austen", "9780141439518", "Romance", 1813, 2),
            ("The Hobbit", "J.R.R. Tolkien", "9780547928227", "Fantasy", 1937, 6),
            # Add more sample books as needed
        ]
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                for book in sample_books:
                    try:
                        c.execute("""
                        INSERT INTO books 
                        (title, author, isbn, genre, publication_year, quantity)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, book)
                    except sqlite3.IntegrityError:
                        continue
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding sample books: {e}")

    def add_book(self, title, author, isbn, genre, publication_year, quantity):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                INSERT INTO books (title, author, isbn, genre, publication_year, quantity, available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, author, isbn, genre, publication_year, quantity, quantity))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def get_all_books(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM books ORDER BY title")
                return c.fetchall()
        except sqlite3.Error:
            return []

    def search_books(self, query):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                SELECT * FROM books 
                WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR genre LIKE ?
                ORDER BY title
                """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
                return c.fetchall()
        except sqlite3.Error:
            return []

    def update_book(self, book_id, title, author, isbn, genre, publication_year, quantity):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("""
                UPDATE books 
                SET title=?, author=?, isbn=?, genre=?, publication_year=?, quantity=?, available=?
                WHERE id=?
                """, (title, author, isbn, genre, publication_year, quantity, quantity, book_id))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def delete_book(self, book_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM books WHERE id=?", (book_id,))
                conn.commit()
                return c.rowcount > 0
        except sqlite3.Error:
            return False

class BookManagementGUI:
    def __init__(self, root):
        self.root = root
        self.book_manager = BookManagement()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Book Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f2f5")

        main_container = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_container.pack(expand=True, fill="both")

        title = tk.Label(main_container, text="Book Management System", font=("Segoe UI", 24, "bold"), bg="#f0f2f5", fg="#1a73e8")
        title.pack(pady=(0, 20))

        search_frame = tk.Frame(main_container, bg="#f0f2f5")
        search_frame.pack(fill="x", pady=(0, 20))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 12), width=40)
        search_entry.pack(side="left", padx=(0, 10))

        self.tree = ttk.Treeview(main_container, columns=("ID", "Title", "Author", "ISBN", "Genre", "Year", "Quantity", "Available"), show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("ISBN", text="ISBN")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Available", text="Available")
        self.tree.column("ID", width=50)
        self.tree.column("Title", width=300)
        self.tree.column("Author", width=200)
        self.tree.column("ISBN", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Year", width=80)
        self.tree.column("Quantity", width=80)
        self.tree.column("Available", width=80)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(main_container, bg="#f0f2f5")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Add Book", command=self.show_add_book_dialog, font=("Segoe UI", 12, "bold"), bg="#34a853", fg="white", relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(button_frame, text="Edit Book", command=self.show_edit_book_dialog, font=("Segoe UI", 12, "bold"), bg="#1a73e8", fg="white", relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Book", command=self.delete_selected_book, font=("Segoe UI", 12, "bold"), bg="#ea4335", fg="white", relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(button_frame, text="Back", command=self.root.destroy, font=("Segoe UI", 12, "bold"), bg="#6c757d", fg="white", relief="flat", cursor="hand2").pack(side="left", padx=5)

        self.load_books()

    def load_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        books = self.book_manager.get_all_books()
        for book in books:
            self.tree.insert("", "end", values=book)

    def on_search_change(self, *args):
        query = self.search_var.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        books = self.book_manager.search_books(query)
        for book in books:
            self.tree.insert("", "end", values=book)

    def show_add_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("400x500")
        dialog.configure(bg="#f0f2f5")

        fields = [("Title:", "title"), ("Author:", "author"), ("ISBN:", "isbn"), ("Genre:", "genre"), ("Publication Year:", "year"), ("Quantity:", "quantity")]
        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(dialog, text=label, font=("Segoe UI", 10), bg="#f0f2f5").pack(pady=(20 if i == 0 else 10, 5))
            entry = ttk.Entry(dialog, width=40)
            entry.pack()
            entries[field] = entry

        def save_book():
            try:
                if self.book_manager.add_book(
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["isbn"].get(),
                    entries["genre"].get(),
                    int(entries["year"].get()),
                    int(entries["quantity"].get())
                ):
                    self.load_books()
                    dialog.destroy()
                    messagebox.showinfo("Success", "Book added successfully!")
                else:
                    messagebox.showerror("Error", "Failed to add book")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for year and quantity")

        tk.Button(dialog, text="Save", command=save_book, font=("Segoe UI", 12, "bold"), bg="#34a853", fg="white", relief="flat").pack(pady=20)

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

        fields = [("Title:", "title"), ("Author:", "author"), ("ISBN:", "isbn"), ("Genre:", "genre"), ("Publication Year:", "year"), ("Quantity:", "quantity")]
        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(dialog, text=label, font=("Segoe UI", 10), bg="#f0f2f5").pack(pady=(20 if i == 0 else 10, 5))
            entry = ttk.Entry(dialog, width=40)
            entry.pack()
            entries[field] = entry

        current_values = self.tree.item(selected[0])["values"]
        entries["title"].insert(0, current_values[1])
        entries["author"].insert(0, current_values[2])
        entries["isbn"].insert(0, current_values[3])
        entries["genre"].insert(0, current_values[4])
        entries["year"].insert(0, current_values[5])
        entries["quantity"].insert(0, current_values[6])

        def save_changes():
            try:
                if self.book_manager.update_book(
                    book_id,
                    entries["title"].get(),
                    entries["author"].get(),
                    entries["isbn"].get(),
                    entries["genre"].get(),
                    int(entries["year"].get()),
                    int(entries["quantity"].get())
                ):
                    self.load_books()
                    dialog.destroy()
                    messagebox.showinfo("Success", "Book updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update book")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for year and quantity")

        tk.Button(dialog, text="Save Changes", command=save_changes, font=("Segoe UI", 12, "bold"), bg="#1a73e8", fg="white", relief="flat").pack(pady=20)

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
