import tkinter as tk
from tkinter import messagebox, ttk
from db import get_connection

def open_salary(content):
    # Title
    tk.Label(content, text="💰 Salary Management", font=("Arial", 16, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=15)

    # Button Frame
    btn_frame = tk.Frame(content, bg="#1a1a2e")
    btn_frame.pack(fill="x", padx=20)

    tk.Button(btn_frame, text="+ Process Salary", font=("Arial", 10, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: process_salary_window(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: load_salaries(tree)).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🗑 Delete", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: delete_salary(tree)).pack(side="left", padx=5)

    # Table Frame
    table_frame = tk.Frame(content, bg="#1a1a2e")
    table_frame.pack(fill="both", expand=True, padx=20, pady=15)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    # Treeview Table
    columns = ("Salary ID", "Employee", "Basic Salary", "Bonus", "Deductions", "Net Salary", "Pay Date")
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
    widths = [80, 150, 120, 100, 110, 120, 100]
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")

    tree.pack(fill="both", expand=True)
    scrollbar.config(command=tree.yview)

    load_salaries(tree)

def load_salaries(tree):
    for row in tree.get_children():
        tree.delete(row)

    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.salary_id, e.name, s.basic_salary, s.bonus,
                   s.deductions, s.net_salary, s.pay_date
            FROM salaries s
            JOIN employees e ON s.emp_id = e.emp_id
            ORDER BY s.salary_id ASC
        """)
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

def process_salary_window(tree):
    win = tk.Toplevel()
    win.title("Process Salary")
    win.geometry("400x480")
    win.configure(bg="#1a1a2e")
    win.resizable(False, False)

    tk.Label(win, text="💰 Process Salary", font=("Arial", 14, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=15)

    # Employee Dropdown
    tk.Label(win, text="Select Employee", font=("Arial", 10),
             bg="#1a1a2e", fg="white").pack(pady=(8, 2))
    emp_var = tk.StringVar()
    emp_dropdown = ttk.Combobox(win, textvariable=emp_var, font=("Arial", 11),
                                 width=28, state="readonly")

    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT emp_id, name FROM employees WHERE status='Active'")
        emps = cursor.fetchall()
        conn.close()
        emp_dropdown["values"] = [f"{e[0]} - {e[1]}" for e in emps]
    emp_dropdown.pack(pady=5)

    fields = {}

    def make_field(label):
        tk.Label(win, text=label, font=("Arial", 10), bg="#1a1a2e", fg="white").pack(pady=(8, 2))
        entry = tk.Entry(win, font=("Arial", 11), width=30, bg="#16213e",
                         fg="white", insertbackground="white", relief="flat", bd=5)
        entry.pack()
        fields[label] = entry

    make_field("Basic Salary")
    make_field("Bonus")
    make_field("Deductions")
    make_field("Pay Date (YYYY-MM-DD)")

    # Net Salary Display
    net_label = tk.Label(win, text="Net Salary: 0.00", font=("Arial", 12, "bold"),
                         bg="#1a1a2e", fg="#00ff88")
    net_label.pack(pady=10)

    def calculate_net(*args):
        try:
            basic = float(fields["Basic Salary"].get() or 0)
            bonus = float(fields["Bonus"].get() or 0)
            deductions = float(fields["Deductions"].get() or 0)
            net = basic + bonus - deductions
            net_label.config(text=f"Net Salary: {net:,.2f}")
        except:
            net_label.config(text="Net Salary: 0.00")

    for f in ["Basic Salary", "Bonus", "Deductions"]:
        fields[f].bind("<KeyRelease>", calculate_net)

    def save():
        emp = emp_var.get()
        basic = fields["Basic Salary"].get()
        bonus = fields["Bonus"].get() or "0"
        deductions = fields["Deductions"].get() or "0"
        pay_date = fields["Pay Date (YYYY-MM-DD)"].get()

        if not emp or not basic or not pay_date:
            messagebox.showwarning("Warning", "Employee, Basic Salary and Pay Date are required!", parent=win)
            return

        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", pay_date):
            messagebox.showwarning("Warning", "Date must be in YYYY-MM-DD format!", parent=win)
            return

        try:
            emp_id = int(emp.split(" - ")[0])
            basic = float(basic)
            bonus = float(bonus)
            deductions = float(deductions)
            net = basic + bonus - deductions

            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO salaries (emp_id, basic_salary, bonus, deductions, net_salary, pay_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (emp_id, basic, bonus, deductions, net, pay_date))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Salary processed!\nNet Salary: {net:,.2f}", parent=win)
                win.destroy()
                load_salaries(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process salary!\n{e}", parent=win)

    tk.Button(win, text="Process Salary", font=("Arial", 11, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=20, pady=8, command=save).pack(pady=15)

def delete_salary(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a salary record to delete!")
        return

    salary_id = tree.item(selected[0])["values"][0]
    emp_name = tree.item(selected[0])["values"][1]

    if messagebox.askyesno("Confirm", f"Delete salary record for '{emp_name}'?"):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM salaries WHERE salary_id=%s", (salary_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Salary record deleted!")
                load_salaries(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete!\n{e}")
