import sqlite3

DB_NAME = "database.db"

def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # Create users table
            c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
            """)
            # Create books table
            c.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                genre TEXT,
                publication_year INTEGER,
                quantity INTEGER NOT NULL,
                available INTEGER NOT NULL,
                date_added TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Create borrowings table with fine column
            c.execute("""
            CREATE TABLE IF NOT EXISTS borrowings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                username TEXT NOT NULL,
                borrow_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                fine INTEGER DEFAULT 0,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(username) REFERENCES users(username)
            )
            """)
            # Add fine column to existing borrowings table if it doesn't exist
            try:
                c.execute("ALTER TABLE borrowings ADD COLUMN fine INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Column already exists
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
