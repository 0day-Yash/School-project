# A&Y Library Management System

A desktop library management system built with Python and Tkinter, featuring user authentication, book management, borrowing/returns, fines calculation, and personalized recommendations.

## 🌟 Features

- **Authentication**
  - User registration and login
  - Password hashing with bcrypt
  - Admin and regular user roles

- **Book Management**
  - Add, edit, and delete books
  - Track total and available copies
  - Search by title or author
  - ISBN uniqueness validation

- **Borrowing System**
  - Borrow and return books
  - 14-day loan period
  - Automatic fine calculation (Rs.10/day after grace period)
  - View borrowing history

- **Admin Features**
  - Manage books and users
  - View fines report
  - Monitor system statistics
  - Toggle user admin status

- **Smart Recommendations**
  - Collaborative filtering using SVD
  - Fallback to popularity-based suggestions
  - Personalized for each user

- **Modern UI**
  - Full-screen Tkinter interface
  - Beautiful login screen with library background
  - Dashboard with quick actions
  - Easy-to-use book lists

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/0day-yash/School-project.git
   cd School-project
   ```

2. Create and activate a virtual environment (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Initialize the database and create default admin:
   ```powershell
   python db_init.py
   python One_Time.py
   ```

5. Run the application:
   ```powershell
   python main.py
   ```

6. Login with default admin credentials:
   - Username: admin
   - Password: admin123

## 📁 Project Structure

- `main.py` - Entry point, dashboard, and main menu
- `login.py` - Authentication and login GUI
- `borrow_return.py` - Core borrowing system and related UIs
- `admin.py` - Admin panel and management features
- `book_management.py` - Book CRUD operations
- `db_init.py` - Database schema and initialization
- `requirements.txt` - Project dependencies

## 🔧 Configuration

The system uses SQLite (`database.db`) for data storage. Key settings:
- Loan period: 14 days
- Fine rate: Rs.10 per day after grace period
- Admin creation: Use One_Time.py or the admin panel

## 👥 User Types

1. **Regular Users**
   - Browse and search books
   - Borrow and return books
   - View personal history
   - Get personalized recommendations

2. **Administrators**
   - All regular user features
   - Manage books and users
   - View system reports
   - Monitor fines and statistics

## 🎯 Recent Updates

- Added background image to login screen
- Improved recommendation system reliability
- Enhanced admin user management
- Added double-click actions for faster borrowing
- Implemented fine calculation and tracking

## 🔜 Planned Features

1. **Enhanced User Experience**
   - Book cover image support
   - Dark/light theme toggle
   - Mobile-responsive design
   - Keyboard shortcuts

2. **Advanced Features**
   - Email notifications for due dates
   - QR code scanning for books
   - Export reports to PDF/Excel
   - Reading list creation

3. **Library Operations**
   - Book reservations
   - Inter-library loans
   - Book condition tracking
   - Digital content management

4. **Analytics**
   - Reading pattern analysis
   - Popular genre trends
   - Peak borrowing times
   - User engagement metrics

## 📝 Contributing

Want to contribute? Great! Here are some ways:
1. Fork the repo
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 🔒 Security

- Passwords are hashed using bcrypt
- SQLite database with proper constraints
- Input validation on all forms
- Role-based access control

## 📄 License

This project is part of a Class 12 Computer Science practical.

## 👥 Authors

Created by Yash and Aryan

## 🙏 Acknowledgments

- Thanks to our teachers for guidance
- Built using Python and Tkinter
- Uses collaborative filtering for recommendations