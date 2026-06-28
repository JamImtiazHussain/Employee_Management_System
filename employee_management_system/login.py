import tkinter as tk
from tkinter import messagebox
from db import get_connection

def open_login():
    window = tk.Tk()
    window.title("Employee Management System")
    window.geometry("400x500")
    window.resizable(True, True)
    window.state('zoomed')
    window.configure(bg="#1a1a2e")

    # Title
    tk.Label(window, text="Employee Management", font=("Arial", 18, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=30)
    tk.Label(window, text="System", font=("Arial", 18, "bold"),
             bg="#1a1a2e", fg="#e94560").pack()
    tk.Label(window, text="Admin Login", font=("Arial", 12),
             bg="#1a1a2e", fg="white").pack(pady=10)

    # Username
    tk.Label(window, text="Username", font=("Arial", 11),
             bg="#1a1a2e", fg="white").pack(pady=(20, 5))
    username_entry = tk.Entry(window, font=("Arial", 12), width=25,
                               bg="#16213e", fg="white", insertbackground="white",
                               relief="flat", bd=5)
    username_entry.pack(pady=5)

    # Password
    tk.Label(window, text="Password", font=("Arial", 11),
             bg="#1a1a2e", fg="white").pack(pady=(15, 5))
    password_entry = tk.Entry(window, font=("Arial", 12), width=25,
                               bg="#16213e", fg="white", insertbackground="white",
                               relief="flat", bd=5, show="*")
    password_entry.pack(pady=5)

    # Login Function
    def login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password!")
            return

        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                           (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                window.destroy()
                open_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password!")

    # Login Button
    tk.Button(window, text="Login", font=("Arial", 12, "bold"),
              bg="#e94560", fg="white", width=20, relief="flat",
              cursor="hand2", command=login).pack(pady=30)

    tk.Label(window, text="Default: admin / admin123", font=("Arial", 9),
             bg="#1a1a2e", fg="gray").pack()

    window.mainloop()

def open_dashboard():
    from dashboard import open_dashboard
    open_dashboard()

open_login()