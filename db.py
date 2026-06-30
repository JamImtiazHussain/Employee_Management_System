import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "employee_management.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            position TEXT NOT NULL,
            dept_id INTEGER,
            joining_date TEXT,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salaries (
            salary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            basic_salary REAL NOT NULL,
            bonus REAL DEFAULT 0,
            deductions REAL DEFAULT 0,
            net_salary REAL NOT NULL,
            pay_date TEXT NOT NULL,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            app_id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT NOT NULL,
            email TEXT,
            position_applied TEXT NOT NULL,
            resume_text TEXT,
            ai_score INTEGER DEFAULT 0,
            ai_feedback TEXT,
            status TEXT DEFAULT 'New',
            applied_date TEXT DEFAULT (date('now'))
        )
    """)

    # Seed default admin user if none exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123"),
        )

    conn.commit()
    conn.close()
