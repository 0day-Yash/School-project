from login import launch_login_gui
DB_NAME = "database.db"

def on_login_success(username):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
        row = c.fetchone()

    if row and row[0] == 1:
        print("Logged in as Admin")
        launch_admin_panel()
    else:
        print(f"{username} has logged in.")
        launch_main_dashboard(username)

def logout():
    root.destroy()
    launch_login_gui(on_login_success)  # on_login_success should be imported from main.py


import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
import os
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Always create tables if missing
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            tags TEXT,
            available INTEGER DEFAULT 1
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            book_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
        """)

        conn.commit()

#########################################################
def populate_sample_books():
    books = [
        ("The Great Gatsby", "F. Scott Fitzgerald", "Classic", "romance,american,dream"),
        ("1984", "George Orwell", "Dystopian", "future,totalitarian,freedom"),
        ("To Kill a Mockingbird", "Harper Lee", "Classic", "justice,america,civil-rights"),
        ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "adventure,dragons,magic"),
        ("Pride and Prejudice", "Jane Austen", "Romance", "love,society,marriage"),
        ("The Alchemist", "Paulo Coelho", "Philosophical", "destiny,journey,self-discovery"),
        ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy", "magic,school,adventure"),
        ("The Catcher in the Rye", "J.D. Salinger", "Coming-of-age", "teenage,rebel,identity")
    ]

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        for title, author, genre, tags in books:
            c.execute("SELECT * FROM books WHERE title = ? AND author = ?", (title, author))
            if not c.fetchone():  # avoid duplicates
                c.execute("INSERT INTO books (title, author, genre, tags, available) VALUES (?, ?, ?, ?, 1)",
                          (title, author, genre, tags))
        conn.commit()

############################################################
DB_NAME = "database.db"

def launch_admin_panel():
    def refresh_book_list():
        for widget in book_list_frame.winfo_children():
            widget.destroy()

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, title, author, genre FROM books")
            books = c.fetchall()

        for book_id, title, author, genre in books:
            row = tk.Frame(book_list_frame, bg="#fff")
            row.pack(fill="x", pady=2, padx=5)

            tk.Label(row, text=f"{title} by {author} ({genre})", bg="#fff", font=("Segoe UI", 12)).pack(side="left", padx=5)
            tk.Button(row, text="Edit", command=lambda b=book_id: edit_book(b), bg="#007bff", fg="white", width=8).pack(side="right", padx=5)
            tk.Button(row, text="Delete", command=lambda b=book_id: delete_book(b), bg="#dc3545", fg="white", width=8).pack(side="right")

    def add_book():
        title = title_entry.get()
        author = author_entry.get()
        genre = genre_entry.get()
        tags = tags_entry.get()
        if title and author:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO books (title, author, genre, tags, available) VALUES (?, ?, ?, ?, 1)",
                          (title, author, genre, tags))
                conn.commit()
            refresh_book_list()

    def delete_book(book_id):
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
        refresh_book_list()

    def edit_book(book_id):
        def save_changes():
            new_title = title_entry.get()
            new_author = author_entry.get()
            new_genre = genre_entry.get()
            new_tags = tags_entry.get()

            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("""
                    UPDATE books SET title = ?, author = ?, genre = ?, tags = ?
                    WHERE id = ?
                """, (new_title, new_author, new_genre, new_tags, book_id))
                conn.commit()

            edit_win.destroy()
            refresh_book_list()

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT title, author, genre, tags FROM books WHERE id = ?", (book_id,))
            book = c.fetchone()

        if not book:
            return

        edit_win = tk.Toplevel(root)
        edit_win.title("Edit Book")
        edit_win.geometry("400x250")
        edit_win.configure(bg="#f0f0f0")

        tk.Label(edit_win, text="Title:", bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        title_entry = tk.Entry(edit_win, width=30)
        title_entry.insert(0, book[0])
        title_entry.grid(row=0, column=1, pady=5)

        tk.Label(edit_win, text="Author:", bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        author_entry = tk.Entry(edit_win, width=30)
        author_entry.insert(0, book[1])
        author_entry.grid(row=1, column=1, pady=5)

        tk.Label(edit_win, text="Genre:", bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        genre_entry = tk.Entry(edit_win, width=30)
        genre_entry.insert(0, book[2])
        genre_entry.grid(row=2, column=1, pady=5)

        tk.Label(edit_win, text="Tags:", bg="#f0f0f0").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        tags_entry = tk.Entry(edit_win, width=30)
        tags_entry.insert(0, book[3])
        tags_entry.grid(row=3, column=1, pady=5)

        tk.Button(edit_win, text="Save Changes", bg="#4CAF50", fg="white", command=save_changes).grid(row=4, column=1, pady=15)

    global root
    root = tk.Tk()
    root.title("Admin Panel - Smart Library")
    root.geometry("1000x600")
    root.configure(bg="#f0f4f7")
    tk.Button(root, text="Logout", bg="#dc3545", fg="white", command=logout).pack(anchor="ne", padx=20, pady=10)


    tk.Label(root, text="Admin Panel - Manage Books", font=("Segoe UI", 20, "bold"), bg="#f0f4f7").pack(pady=20)

    # Add Book Form
    form_frame = tk.Frame(root, bg="#f0f4f7")
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Title:", bg="#f0f4f7").grid(row=0, column=0)
    title_entry = tk.Entry(form_frame, width=30)
    title_entry.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Author:", bg="#f0f4f7").grid(row=0, column=2)
    author_entry = tk.Entry(form_frame, width=30)
    author_entry.grid(row=0, column=3, padx=5)

    tk.Label(form_frame, text="Genre:", bg="#f0f4f7").grid(row=1, column=0)
    genre_entry = tk.Entry(form_frame, width=30)
    genre_entry.grid(row=1, column=1, padx=5)

    tk.Label(form_frame, text="Tags:", bg="#f0f4f7").grid(row=1, column=2)
    tags_entry = tk.Entry(form_frame, width=30)
    tags_entry.grid(row=1, column=3, padx=5)

    tk.Button(root, text="Add Book", command=add_book, bg="#4CAF50", fg="white", font=("Segoe UI", 12)).pack(pady=10)

    # Book List
    # Create a scrollable canvas inside a frame
    canvas_frame = tk.Frame(root, bg="#f0f4f7")
    canvas_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    canvas = tk.Canvas(canvas_frame, bg="#f0f4f7", highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f4f7")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    book_list_frame = scrollable_frame  # all book rows will be added to this frame

    refresh_book_list()
    root.mainloop()


#*****************************************************************


import tkinter as tk
import sqlite3
from datetime import datetime

def launch_main_dashboard(username):
    def logout():
        root.destroy()
        launch_login_gui(on_login_success)

    def fetch_books(search_term=""):
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            if search_term:
                query = f"%{search_term.lower()}%"
                c.execute("SELECT id, title, author, genre FROM books WHERE available = 1 AND (LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(genre) LIKE ?)",
                          (query, query, query))
            else:
                c.execute("SELECT id, title, author, genre FROM books WHERE available = 1")
            return c.fetchall()

    def fetch_recommendations():
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT b.title, b.author FROM books b
                JOIN transactions t ON b.id = t.book_id
                WHERE t.username = ? ORDER BY t.issue_date DESC LIMIT 1
            """, (username,))
            row = c.fetchone()
            if row:
                c.execute("SELECT genre FROM books WHERE title = ?", (row[0],))
                genre = c.fetchone()
                if genre:
                    c.execute("SELECT title, author FROM books WHERE genre = ? AND available = 1 LIMIT 3", (genre[0],))
                    return c.fetchall()
        return []

    def fetch_user_books():
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT b.id, b.title, b.author, b.genre FROM books b
                JOIN transactions t ON b.id = t.book_id
                WHERE t.username = ? AND t.return_date IS NULL
            """, (username,))
            return c.fetchall()

    def borrow_book(book_id):
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
            c.execute("INSERT INTO transactions (username, book_id, issue_date) VALUES (?, ?, ?)",
                      (username, book_id, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
        refresh_dashboard()

    def return_book(book_id):
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
            c.execute("UPDATE transactions SET return_date = ? WHERE book_id = ? AND username = ? AND return_date IS NULL",
                      (datetime.now().strftime("%Y-%m-%d"), book_id, username))
            conn.commit()
        refresh_dashboard()

    def refresh_dashboard():
        search_term = search_var.get()

        # Available Books
        for widget in books_frame.winfo_children():
            widget.destroy()

        tk.Label(books_frame, text="📚 Available Books", font=("Segoe UI", 18, "bold"), bg="#fdf6e3", fg="#222").pack(anchor="w", padx=10, pady=10)
        for book_id, title, author, genre in fetch_books(search_term):
            card = tk.Frame(books_frame, bg="white", relief="groove", bd=2)
            card.pack(fill="x", padx=20, pady=5)
            tk.Label(card, text=title, font=("Segoe UI", 15, "bold"), bg="white").pack(anchor="w", padx=10)
            tk.Label(card, text=f"by {author} | Genre: {genre}", font=("Segoe UI", 11), bg="white", fg="#555").pack(anchor="w", padx=10)
            tk.Button(card, text="Borrow", font=("Segoe UI", 10), bg="#4CAF50", fg="white",
                      command=lambda b=book_id: borrow_book(b)).pack(padx=10, pady=5, anchor="e")

        # Recommendations
        for widget in recommendations_frame.winfo_children():
            widget.destroy()

        tk.Label(recommendations_frame, text="✨ Recommendations", font=("Segoe UI", 16, "bold"), bg="#eee8d5").pack(anchor="w", padx=10, pady=10)
        recs = fetch_recommendations()
        if recs:
            for title, author in recs:
                tk.Label(recommendations_frame, text=f"{title} by {author}", font=("Segoe UI", 12),
                         bg="#eee8d5", fg="#444").pack(anchor="w", padx=20, pady=2)
        else:
            tk.Label(recommendations_frame, text="No recommendations yet.", font=("Segoe UI", 12),
                     bg="#eee8d5", fg="#999").pack(anchor="w", padx=20)

        # My Books
        for widget in my_books_frame.winfo_children():
            widget.destroy()

        tk.Label(my_books_frame, text="📖 My Books", font=("Segoe UI", 16, "bold"), bg="#fdf6e3").pack(anchor="w", padx=10, pady=10)
        user_books = fetch_user_books()
        if user_books:
            for book_id, title, author, genre in user_books:
                frame = tk.Frame(my_books_frame, bg="white", relief="ridge", bd=2)
                frame.pack(fill="x", padx=20, pady=5)
                tk.Label(frame, text=title, font=("Segoe UI", 14, "bold"), bg="white").pack(anchor="w", padx=10)
                tk.Label(frame, text=f"by {author} | {genre}", font=("Segoe UI", 11), bg="white", fg="#555").pack(anchor="w", padx=10)
                tk.Button(frame, text="Return", font=("Segoe UI", 10), bg="#2196F3", fg="white",
                          command=lambda b=book_id: return_book(b)).pack(padx=10, pady=5, anchor="e")
        else:
            tk.Label(my_books_frame, text="You haven't borrowed anything yet.", font=("Segoe UI", 12),
                     bg="#fdf6e3", fg="#666").pack(padx=20)

    # ==== Main Window ====
    root = tk.Tk()
    root.title("Smart Library")
    root.attributes('-fullscreen', True)
    root.configure(bg="#fdf6e3")

    # Top bar with Welcome + Logout
    top_frame = tk.Frame(root, bg="#fdf6e3")
    top_frame.pack(fill="x", pady=(20, 0), padx=20)

    tk.Label(top_frame, text=f"Welcome, {username}!", font=("Segoe UI", 28, "bold"), bg="#fdf6e3", fg="#2e2e2e").pack(side="left")
    tk.Button(top_frame, text="Logout", font=("Segoe UI", 12), bg="#dc3545", fg="white",
          command=logout).pack(side="right", padx=10)

    # Search bar right below it
    search_var = tk.StringVar()
    search_entry = tk.Entry(root, textvariable=search_var, font=("Segoe UI", 14), width=40)
    search_entry.pack(pady=10)
    search_var.trace_add("write", lambda *args: refresh_dashboard())


    # Main content frames
    content = tk.Frame(root, bg="#fdf6e3")
    content.pack(fill="both", expand=True, padx=20)

    books_canvas_frame = tk.Frame(content, bg="#fdf6e3")
    books_canvas_frame.pack(side="left", fill="both", expand=True)

    books_canvas = tk.Canvas(books_canvas_frame, bg="#fdf6e3", highlightthickness=0)
    books_scrollbar = tk.Scrollbar(books_canvas_frame, orient="vertical", command=books_canvas.yview)
    books_scrollable_frame = tk.Frame(books_canvas, bg="#fdf6e3")

    books_scrollable_frame.bind(
    "<Configure>",
    lambda e: books_canvas.configure(
        scrollregion=books_canvas.bbox("all")
    )
)

    books_canvas.create_window((0, 0), window=books_scrollable_frame, anchor="nw")
    books_canvas.configure(yscrollcommand=books_scrollbar.set)

    books_canvas.pack(side="left", fill="both", expand=True)
    books_scrollbar.pack(side="right", fill="y")

    books_frame = books_scrollable_frame  # redirect your book list to this
 

    my_books_frame = tk.Frame(content, bg="#fdf6e3")
    my_books_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))

    recommendations_frame = tk.Frame(content, bg="#eee8d5", width=300)
    recommendations_frame.pack(side="right", fill="y", padx=(20, 0))

    
    refresh_dashboard()
    root.mainloop()















if __name__ == "__main__":
    init_db()
    populate_sample_books()
    launch_login_gui(on_login_success)

