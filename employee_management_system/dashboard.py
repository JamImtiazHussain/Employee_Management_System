import tkinter as tk
from tkinter import messagebox

def open_dashboard():
    window = tk.Tk()
    window.title("Employee Management System - Dashboard")
    window.geometry("900x600")
    window.resizable(True, True)
    window.state('zoomed')
    window.configure(bg="#1a1a2e")

    # Top Header
    header = tk.Frame(window, bg="#e94560", height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="🏢 Employee Management System",
             font=("Arial", 18, "bold"), bg="#e94560", fg="white").pack(side="left", padx=20, pady=15)

    tk.Button(header, text="Logout", font=("Arial", 10, "bold"),
              bg="#1a1a2e", fg="white", relief="flat", cursor="hand2",
              command=lambda: logout(window)).pack(side="right", padx=20, pady=15)

    # Left Sidebar
    sidebar = tk.Frame(window, bg="#16213e", width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="Navigation", font=("Arial", 12, "bold"),
             bg="#16213e", fg="#e94560").pack(pady=20)

    # Main Content Area
    content = tk.Frame(window, bg="#1a1a2e")
    content.pack(side="right", fill="both", expand=True)

    # Welcome Message in content
    tk.Label(content, text="👋 Welcome, Admin!",
             font=("Arial", 22, "bold"), bg="#1a1a2e", fg="white").pack(pady=40)
    tk.Label(content, text="Select a module from the sidebar to get started.",
             font=("Arial", 12), bg="#1a1a2e", fg="gray").pack()

    # Sidebar Buttons
    buttons = [
        ("👥  Employees", lambda: open_module("employees", content)),
        ("🏢  Departments", lambda: open_module("departments", content)),
        ("💰  Salary", lambda: open_module("salary", content)),
        ("📄  Hiring & AI", lambda: open_module("hiring", content)),
    ]

    for text, cmd in buttons:
        tk.Button(sidebar, text=text, font=("Arial", 11), bg="#16213e", fg="white",
                  relief="flat", cursor="hand2", width=20, anchor="w",
                  padx=10, pady=12, activebackground="#e94560",
                  activeforeground="white", command=cmd).pack(fill="x", pady=2)

    window.mainloop()

def open_module(module_name, content):
    # Clear content area
    for widget in content.winfo_children():
        widget.destroy()

    if module_name == "employees":
        from employees import open_employees
        open_employees(content)
    elif module_name == "departments":
        from departments import open_departments
        open_departments(content)
    elif module_name == "salary":
        from salary import open_salary
        open_salary(content)
    elif module_name == "hiring":
        from hiring import open_hiring
        open_hiring(content)

def logout(window):
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        window.destroy()
        from login import open_login
        open_login()