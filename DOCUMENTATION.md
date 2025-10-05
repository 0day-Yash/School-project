A&Y Library System (Class 12 Practical)

Authors: Yash and Aryan

Project overview
----------------
A&Y Library System is a desktop Python application (Tkinter GUI) that manages a small library for a school. It supports user registration and login, browsing and searching books, borrowing and returning, borrowing history, fines, an admin panel for full management, and a basic recommendation system based on collaborative filtering using SVD. The project is implemented using standard Python libraries and lightweight data/science libraries for recommendations.

Purpose (Practical Exam context)
- Demonstrate understanding of file and database operations, GUI development, hashing for passwords, relational data design, basic algorithms (recommendation, fines calculation), and software organization.
- Provide a functional library management system suitable for a school lab practical.

Contents of the repository
--------------------------
- `main.py` - Entry point and main menu/dashboard classes. Initializes database and starts the app.
- `db_init.py` - Database schema initialization and DB constants.
- `login.py` - Login and registration GUI and authentication helpers.
- `book_management.py` - Book CRUD operations and optional GUI for direct management.
- `borrow_return.py` - Core borrowing/returning logic, fines calculation, recommendations, and related GUIs (Borrow, Return, History, Recommendations).
- `admin.py` - AdminPanel GUI used by admins to manage books, users, and view reports.
- `admin_new.py` - Another admin implementation/variant; project contains both (possibly iterative versions).
- `Populate.py` - Script to bulk-populate the database with sample books for testing.
- `One_Time.py` - One-time helpers and sample scripts (e.g., create admin user).
- `libtest.py` - Misc test / helper scripts used during development.
- `database.db` - SQLite database file (if present). Database contents may vary.
- `db_init.py` - Already listed; ensures schema and migration (adds fine column if missing).

How components connect (high-level flow)
---------------------------------------
1. Application start (`main.py`):
   - Calls `init_db()` from `db_init.py` to ensure the SQLite database and tables exist.
   - Launches `MainMenu` GUI (full-screen Tkinter). The Main menu allows Login, Admin Panel (login first), or Exit.

2. Authentication (`login.py`):
   - Users can register (username + password) or login.
   - Passwords are hashed with `bcrypt` and stored in `users.password_hash`.
   - `login_user` returns (success, is_admin) which drives whether the Dashboard or AdminPanel opens.

3. Dashboard (`main.py` -> `Dashboard`):
   - Shows statistics (total books, copies, users, borrowings, active borrowings, popular genre, user fines).
   - Offers quick actions: Borrow Book, Return Book, View History, Recommendations, and Admin Panel (if user is admin).

4. Book CRUD (`book_management.py` and Admin GUI in `admin.py`):
   - Admins can Add/Edit/Delete books. Each book row stores quantity and available counts.
   - Quantity updates attempt to keep `available` consistent with active borrowings (no negative availability).

5. Borrowing and Returns (`borrow_return.py`):
   - Borrowing: reduces `books.available` by 1, creates a `borrowings` record with borrow_date and due_date (14 days).
   - Returning: sets `return_date`, computes fine using `calculate_fine`, updates `books.available`.
   - Fines: default policy is no fine for first 14 days late; after that Rs.10 per day.
   - `update_fines` and `view_fines` update and show fines. Borrowing history queries join `borrowings` and `books`.

6. Recommendations (basic collaborative filtering):
   - The `get_recommended_books` function builds a user-book interaction matrix from `borrowings` (1 if borrowed), runs SVD (scipy.sparse.linalg.svds), and predicts scores.
   - Returns top-N book details for the current user, avoiding books already borrowed.
   - If not enough interaction data exists, falls back to most-borrowed/popular books.

Database schema (fields of importance)
-------------------------------------
- users
  - id INTEGER PRIMARY KEY
  - username TEXT UNIQUE
  - password_hash TEXT
  - is_admin INTEGER (0 or 1)

- books
  - id INTEGER PRIMARY KEY
  - title TEXT
  - author TEXT
  - isbn TEXT UNIQUE
  - genre TEXT
  - publication_year INTEGER
  - quantity INTEGER (total copies)
  - available INTEGER (currently available copies)
  - date_added TEXT

- borrowings
  - id INTEGER PRIMARY KEY
  - book_id INTEGER (FK -> books.id)
  - username TEXT (FK -> users.username)
  - borrow_date TEXT
  - due_date TEXT
  - return_date TEXT (nullable)
  - fine INTEGER DEFAULT 0

Key files explained (detailed)
-----------------------------
- `main.py`
  - MainMenu: initial full-screen window with Login / Admin Panel options.
  - Dashboard: after login, shows statistics and quick action buttons. Calls functions from borrow_return and admin modules.
  - Launch flow: if run directly, calls `init_db()` and starts the main menu.

- `db_init.py`
  - Defines `DB_NAME = "database.db"` and `init_db()` which creates tables if missing and migrates by adding `fine` column if absent.
  - This ensures the DB can be reused across runs and older schemas are upgraded safely.

- `login.py`
  - `register_user(username, password, is_admin=0)`: Hashes password with bcrypt and inserts into `users`.
  - `login_user(username, password)`: Fetches stored hash and compares using `bcrypt.checkpw`.
  - `launch_login_gui(on_success)`: Presents a sign-in/register UI; on success calls the provided callback with (username, is_admin).

- `book_management.py`
  - BookManagement: data-layer class with methods: add_sample_books, add_book, get_all_books, search_books, update_book, delete_book.
  - BookManagementGUI: optional GUI to manage books directly (lists books in a Treeview, add/edit/delete with dialogs).

- `borrow_return.py`
  - BorrowReturnSystem: encapsulates borrow/return logic, fine calculation, queries for user borrowings, available books, and the recommendation engine.
  - BorrowGUI/ReturnGUI/HistoryGUI/RecommendationsGUI: Tkinter windows for borrowing, returning, viewing history, and showing recommendations.
  - Recommendation algorithm details: constructs a sparse user-book matrix, runs SVD, computes predicted scores and selects top items. Uses numpy/pandas/scipy.

- `admin.py` and `admin_new.py`
  - Both provide AdminPanel GUIs (iterative implementations). They allow searching books, adding/editing/deleting, viewing users and fines, and showing summary statistics.
  - `admin.py` is used by `main.py` (AdminPanel class imported); `admin_new.py` contains an extended variant with full-screen layout and additional reports.

- `Populate.py` and `One_Time.py`
  - Helper scripts to populate the database with many sample books and to create a default admin user (username: `admin`, password: `admin123`) respectively.

Design notes and algorithms
---------------------------
- Password security: Uses `bcrypt` to hash passwords before storing. Good for the practical; note that `bcrypt` must be installed as a dependency.
- Loans & fines: A simple policy is implemented (14-day grace, then Rs.10/day). Fine is computed and stored on return or via `update_fines`.
- Availability invariants: `books.available` is decremented on borrow and incremented on return. When editing quantities, the admin UI calculates a new `available` that accounts for active borrowings.
- Recommendations: Lightweight collaborative filtering using SVD. Advantages: simple, educational. Limitations: SVD on small/very sparse matrix may crash or return poor results. The code contains safeguards and a fallback to popular books.

Usage and setup (how to run)
----------------------------
1. Create a virtual environment (recommended) and activate it.

Windows PowerShell example:

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
```

2. Install dependencies (see `requirements.txt`).

```powershell
pip install -r requirements.txt
```

3. Initialize the database and create a default admin (one-time):

```powershell
python db_init.py
python One_Time.py
```

Alternatively running `main.py` will call `init_db()` automatically.

4. Run the application:

```powershell
python main.py
```

5. Login with the created admin (`admin` / `admin123`) or register a new user via the GUI.

Teacher-friendly demonstration flow
----------------------------------
- Start `main.py`.
- Show the Main Menu and explain the UI layout.
- Click Login, demonstrate registering a new student, then login.
- From Dashboard show Borrow -> select a book -> Borrow. Show `books.available` decrement.
- Show Return -> select the borrowed book -> Return. Demonstrate fine calculation by altering system date or using the `borrowings` table and setting past due_date.
- Login as Admin and show: adding a new book, editing metadata, deleting a user (with checks for active borrowings), viewing fines report.
- Demonstrate recommendations by borrowing multiple books for different users and showing Recommendations for a target user.

Edge cases and how the app handles them
--------------------------------------
- Borrowing when no copies available: blocked; returns an error message.
- Returning a book that's already returned: blocked; returns informative message.
- Deleting a user with active borrowings: blocked until returns.
- Duplicate ISBNs when adding books: database constraint catches duplicates; GUI shows error.
- Small datasets for recommendations: falls back to most-borrowed books.
- Date parsing errors for fines: caught and default to 0 fine.

Testing
-------
- Unit tests are not included but can be added. Suggested tests:
  - DB initialization: `init_db()` creates tables.
  - Auth: `register_user` then `login_user` returns success.
  - Borrow-return flow: borrow a known book, check `available` decremented and borrowing record created; return and check `available` incremented and fine calculated.
  - Recommendation fallback: ensure that with no borrowings, `get_recommended_books` returns popular books.

Dependencies
------------
- Python 3.10+ recommended
- Libraries (development):
  - bcrypt
  - pandas
  - numpy
  - scipy

(Full list in `requirements.txt` generated alongside this doc.)

Code quality notes and small improvements
----------------------------------------
- There are two admin implementations (`admin.py` and `admin_new.py`). Consider consolidating to a single module to avoid confusion and duplicated maintenance.
- Some scripts in the repository duplicate functionality (e.g., `libtest.py` and bits inside `One_Time.py`). Keep only the final/used scripts.
- Add unit tests using `pytest` and small fixtures that create temporary SQLite databases (use `:memory:`) to run isolated tests quickly.
- Consider switching to a minimal ORM (like SQLAlchemy) if the project grows.

Files to show teacher during viva (recommended)
---------------------------------------------
- `main.py`, `login.py`, `borrow_return.py`, `admin.py`, `db_init.py` — these show the main features and code structure.
- `Populate.py` — to show how you populated the database for demonstrations.

Maintenance and future enhancements
----------------------------------
- Add email notifications or reminders for due books.
- Add user roles beyond admin/student (librarian, guest).
- Replace SVD-based recommendations with content-based or hybrid methods for better small-sample performance.
- Add export (CSV/PDF) for reports like fines and borrowing history.
- Add proper logging using Python's logging module for audit and debugging.

Appendix: Quick reference commands
---------------------------------
Run app:

```powershell
python main.py
```

Init DB only:

```powershell
python db_init.py
```

Populate sample books:

```powershell
python Populate.py
```

Create default admin:

```powershell
python One_Time.py
```

Contact / Credits
-----------------
Project made by Yash and Aryan for Class 12 Computer Science practical. If you need edits to the documentation or more teacher-friendly slides or a short demo script, tell me what you'd like next.