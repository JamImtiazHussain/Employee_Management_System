import tkinter as tk
from tkinter import messagebox, ttk
from db import get_connection

def open_departments(content):
    # Title
    tk.Label(content, text="🏢 Department Management", font=("Arial", 16, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=15)

    # Button Frame
    btn_frame = tk.Frame(content, bg="#1a1a2e")
    btn_frame.pack(fill="x", padx=20)

    tk.Button(btn_frame, text="+ Add Department", font=("Arial", 10, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: add_department_window(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🗑 Delete", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: delete_department(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: load_departments(tree)).pack(side="left", padx=5)

    # Table Frame
    table_frame = tk.Frame(content, bg="#1a1a2e")
    table_frame.pack(fill="both", expand=True, padx=20, pady=15)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    # Treeview Table
    columns = ("ID", "Department Name", "Total Employees")
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
    widths = [80, 300, 200]
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")

    tree.pack(fill="both", expand=True)
    scrollbar.config(command=tree.yview)

    load_departments(tree)

def load_departments(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.dept_id, d.dept_name, COUNT(e.emp_id) as total
            FROM departments d
            LEFT JOIN employees e ON d.dept_id = e.dept_id
            GROUP BY d.dept_id, d.dept_name
            ORDER BY d.dept_id ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

def add_department_window(tree):
    win = tk.Toplevel()
    win.title("Add Department")
    win.geometry("350x250")
    win.configure(bg="#1a1a2e")
    win.resizable(False, False)

    tk.Label(win, text="Add New Department", font=("Arial", 14, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=20)

    tk.Label(win, text="Department Name", font=("Arial", 11),
             bg="#1a1a2e", fg="white").pack(pady=(10, 5))

    name_entry = tk.Entry(win, font=("Arial", 12), width=28,
                          bg="#16213e", fg="white", insertbackground="white",
                          relief="flat", bd=5)
    name_entry.pack(pady=5)

    def save():
        name = name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a department name!", parent=win)
            return

        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO departments (dept_name) VALUES (%s)", (name,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Department added successfully!", parent=win)
                win.destroy()
                load_departments(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add department!\n{e}", parent=win)

    tk.Button(win, text="Save Department", font=("Arial", 11, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=20, pady=8, command=save).pack(pady=25)

def delete_department(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a department to delete!")
        return

    dept_id = tree.item(selected[0])["values"][0]
    dept_name = tree.item(selected[0])["values"][1]
    total_emp = tree.item(selected[0])["values"][2]

    if total_emp > 0:
        messagebox.showerror("Error", f"Cannot delete '{dept_name}'!\nIt has {total_emp} employee(s) assigned to it.")
        return

    if messagebox.askyesno("Confirm", f"Delete department '{dept_name}'?"):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM departments WHERE dept_id=%s", (dept_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Department deleted successfully!")
                load_departments(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete!\n{e}")
