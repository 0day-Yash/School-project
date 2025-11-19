"""
Reset all user passwords to a single test password and write creds.txt.
Creates a backup of the database file before making changes: database.db.bak

USAGE: run from project root (the script expects db_init.DB_NAME)
"""
import shutil
import os
import sqlite3
import bcrypt
from db_init import DB_NAME

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, DB_NAME)
BACKUP_PATH = DB_PATH + '.bak'
CREDS_FILE = os.path.join(PROJECT_ROOT, 'creds.txt')
TEST_PASSWORD = 'password'

def backup_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")

def reset_passwords():
    hashed = bcrypt.hashpw(TEST_PASSWORD.encode('utf-8'), bcrypt.gensalt())
    updated = []
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute("SELECT username FROM users")
        rows = c.fetchall()
        usernames = [r[0] for r in rows]
        for u in usernames:
            c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed, u))
        conn.commit()
        updated = usernames
    finally:
        conn.close()
    return updated

def write_creds(usernames):
    with open(CREDS_FILE, 'w', encoding='utf-8') as f:
        for u in usernames:
            f.write(f"{u}:{TEST_PASSWORD}\n")
    print(f"Wrote creds for {len(usernames)} users to {CREDS_FILE}")

if __name__ == '__main__':
    print("Starting password reset operation — creating DB backup first.")
    backup_db()
    users = reset_passwords()
    write_creds(users)
    print("Done. If you need to restore the original DB, replace the current database with the .bak file.")
