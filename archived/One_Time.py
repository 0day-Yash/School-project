import sqlite3
import bcrypt
from db_init import DB_NAME
with sqlite3.connect(DB_NAME) as conn:
    c = conn.cursor()
    hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
    c.execute("INSERT OR IGNORE INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)", ("admin", hashed, 1))
    conn.commit()
