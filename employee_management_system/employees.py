import tkinter as tk
from tkinter import messagebox, ttk
from db import get_connection

def open_employees(content):
    # Title
    tk.Label(content, text="👥 Employee Management", font=("Arial", 16, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=15)

    # Top Button Frame
    btn_frame = tk.Frame(content, bg="#1a1a2e")
    btn_frame.pack(fill="x", padx=20)

    tk.Button(btn_frame, text="+ Add Employee", font=("Arial", 10, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: add_employee_window(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="✏ Edit", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: edit_employee_window(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🗑 Delete", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: delete_employee(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: load_employees(tree)).pack(side="left", padx=5)

    # Table Frame
    table_frame = tk.Frame(content, bg="#1a1a2e")
    table_frame.pack(fill="both", expand=True, padx=20, pady=15)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    # Treeview Table
    columns = ("ID", "Name", "Email", "Phone", "Position", "Department", "Joining Date", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                        yscrollcommand=scrollbar.set, height=15)

    # Style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#16213e", foreground="white",
                    fieldbackground="#16213e", font=("Arial", 10), rowheight=30)
    style.configure("Treeview.Heading", background="#e94560", foreground="white",
                    font=("Arial", 10, "bold"))

    # Column widths
    widths = [50, 120, 150, 100, 120, 120, 100, 80]
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")

    tree.pack(fill="both", expand=True)
    scrollbar.config(command=tree.yview)

    load_employees(tree)

def load_employees(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.emp_id, e.name, e.email, e.phone, e.position,
                   IFNULL(d.dept_name, 'N/A'), e.joining_date, e.status
            FROM employees e
            LEFT JOIN departments d ON e.dept_id = d.dept_id
            ORDER BY e.emp_id ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

def add_employee_window(tree):
    win = tk.Toplevel()
    win.title("Add New Employee")
    win.geometry("400x550")
    win.configure(bg="#1a1a2e")
    win.resizable(False, False)

    tk.Label(win, text="Add New Employee", font=("Arial", 14, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=15)

    fields = {}

    def make_field(label):
        tk.Label(win, text=label, font=("Arial", 10), bg="#1a1a2e", fg="white").pack(pady=(8,2))
        entry = tk.Entry(win, font=("Arial", 11), width=30, bg="#16213e",
                         fg="white", insertbackground="white", relief="flat", bd=5)
        entry.pack()
        fields[label] = entry

    make_field("Full Name")
    make_field("Email")
    make_field("Phone")
    make_field("Position")
    make_field("Joining Date (YYYY-MM-DD)")

    # Department Dropdown
    tk.Label(win, text="Department", font=("Arial", 10), bg="#1a1a2e", fg="white").pack(pady=(8,2))
    dept_var = tk.StringVar()
    dept_dropdown = ttk.Combobox(win, textvariable=dept_var, font=("Arial", 11),
                                  width=28, state="readonly")

    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id, dept_name FROM departments")
        depts = cursor.fetchall()
        conn.close()
        dept_dropdown["values"] = [f"{d[0]} - {d[1]}" for d in depts]
    dept_dropdown.pack()

    def save():
        name = fields["Full Name"].get()
        email = fields["Email"].get()
        phone = fields["Phone"].get()
        position = fields["Position"].get()
        joining = fields["Joining Date (YYYY-MM-DD)"].get()
        dept = dept_var.get()

        if not name or not position:
            messagebox.showwarning("Warning", "Name and Position are required!", parent=win)
            return

        # Validate date format
        import re
        if joining and not re.match(r"^\d{4}-\d{2}-\d{2}$", joining):
            messagebox.showwarning("Warning", "Date must be in YYYY-MM-DD format!\nExample: 2024-01-15", parent=win)
            return

        dept_id = int(dept.split(" - ")[0]) if dept else None

        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO employees (name, email, phone, position, dept_id, joining_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, email, phone, position, dept_id, joining or None))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Employee added successfully!", parent=win)
                win.destroy()
                load_employees(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add employee!\n{e}", parent=win)

    tk.Button(win, text="Save Employee", font=("Arial", 11, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=20, pady=8, command=save).pack(pady=20)

def delete_employee(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee to delete!")
        return

    emp_id = tree.item(selected[0])["values"][0]
    name = tree.item(selected[0])["values"][1]

    if messagebox.askyesno("Confirm", f"Delete employee '{name}'?"):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                # First delete related salary records
                cursor.execute("DELETE FROM salaries WHERE emp_id=%s", (emp_id,))
                # Then delete the employee
                cursor.execute("DELETE FROM employees WHERE emp_id=%s", (emp_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Employee deleted successfully!")
                load_employees(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete!\n{e}")
def edit_employee_window(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee to edit!")
        return

    values = tree.item(selected[0])["values"]
    emp_id = values[0]

    win = tk.Toplevel()
    win.title("Edit Employee")
    win.geometry("400x580")
    win.configure(bg="#1a1a2e")
    win.resizable(False, False)

    tk.Label(win, text="Edit Employee", font=("Arial", 14, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=15)

    fields = {}

    def make_field(label, default):
        tk.Label(win, text=label, font=("Arial", 10), bg="#1a1a2e", fg="white").pack(pady=(8,2))
        entry = tk.Entry(win, font=("Arial", 11), width=30, bg="#16213e",
                         fg="white", insertbackground="white", relief="flat", bd=5)
        entry.insert(0, default)
        entry.pack()
        fields[label] = entry

    make_field("Full Name", values[1])
    make_field("Email", values[2])
    make_field("Phone", values[3])
    make_field("Position", values[4])

    # Department Dropdown
    tk.Label(win, text="Department", font=("Arial", 10),
             bg="#1a1a2e", fg="white").pack(pady=(8, 2))
    dept_var = tk.StringVar()
    dept_dropdown = ttk.Combobox(win, textvariable=dept_var, font=("Arial", 11),
                                  width=28, state="readonly")

    # Load departments
    dept_list = []
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id, dept_name FROM departments")
        dept_list = cursor.fetchall()

        # Get current department of employee
        cursor.execute("SELECT dept_id FROM employees WHERE emp_id=%s", (emp_id,))
        current_dept = cursor.fetchone()
        conn.close()

        dept_dropdown["values"] = [f"{d[0]} - {d[1]}" for d in dept_list]

        # Pre-select current department
        if current_dept and current_dept[0]:
            for d in dept_list:
                if d[0] == current_dept[0]:
                    dept_var.set(f"{d[0]} - {d[1]}")
                    break
        else:
            # Set current department name from table if available
            current_dept_name = values[5]
            for d in dept_list:
                if d[1] == current_dept_name:
                    dept_var.set(f"{d[0]} - {d[1]}")
                    break

    dept_dropdown.pack()

    def update():
        name = fields["Full Name"].get()
        email = fields["Email"].get()
        phone = fields["Phone"].get()
        position = fields["Position"].get()
        dept = dept_var.get()

        if not name or not position:
            messagebox.showwarning("Warning", "Name and Position are required!", parent=win)
            return

        dept_id = int(dept.split(" - ")[0]) if dept else None

        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE employees SET name=%s, email=%s, phone=%s, position=%s, dept_id=%s
                    WHERE emp_id=%s
                """, (name, email, phone, position, dept_id, emp_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Employee updated successfully!", parent=win)
                win.destroy()
                load_employees(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update!\n{e}", parent=win)

    tk.Button(win, text="Update Employee", font=("Arial", 11, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=20, pady=8, command=update).pack(pady=20)