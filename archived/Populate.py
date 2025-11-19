import sqlite3
import random
from datetime import datetime
from db_init import DB_NAME

def generate_isbn(index):
    """Generate a unique 13-digit ISBN-like string."""
    base = f"978{index:010d}"
    return base

def populate_books():
    genres = [
        "Fiction", "Fantasy", "Romance", "Thriller", "Science Fiction",
        "Historical Fiction", "Young Adult", "Non-Fiction", "Mystery", "Biography"
    ]
    titles = [
        "Whispers of", "Shadows of", "Echoes of", "The Last", "Journey to",
        "Secrets of", "Tales of", "The Forgotten", "Dreams of", "Path to",
        "Light of", "Darkness in", "Rise of", "Fall of", "Heart of"
    ]
    nouns = [
        "Time", "Destiny", "Love", "Fate", "Hope", "Truth", "Courage",
        "Dreams", "Stars", "Empire", "Kingdom", "Night", "Dawn", "Horizon"
    ]
    authors = [
        "Emma Stone", "Liam Carter", "Olivia Grant", "Noah Blake", "Ava Reed",
        "Ethan Moore", "Sophia Clark", "James Hill", "Isabella Ward", "Lucas Gray",
        "Mia Evans", "Alexander Lee", "Charlotte King", "Daniel Wright", "Amelia Scott"
    ]

    books = []
    for i in range(200):
        title = f"{random.choice(titles)} {random.choice(nouns)}"
        author = random.choice(authors)
        isbn = generate_isbn(i)
        genre = random.choice(genres)
        publication_year = random.randint(1800, 2025)
        quantity = random.randint(1, 10)
        books.append((title, author, isbn, genre, publication_year, quantity))

    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            inserted = 0
            for book in books:
                try:
                    c.execute("""
                    INSERT INTO books 
                    (title, author, isbn, genre, publication_year, quantity, available)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (*book, book[5]))  # available = quantity
                    inserted += 1
                except sqlite3.IntegrityError:
                    continue  # Skip duplicates (ISBN conflict)
            conn.commit()
            print(f"Successfully inserted {inserted} books into the database.")
    except sqlite3.Error as e:
        print(f"Error populating books: {e}")

if __name__ == "__main__":
    populate_books()
