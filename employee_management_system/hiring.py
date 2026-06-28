import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from db import get_connection
from groq import Groq

# ⚠️ Replace with your Groq API key
GROQ_API_KEY = "GROQ API KEY"
client = Groq(api_key=GROQ_API_KEY)

def open_hiring(content):
    tk.Label(content, text="📄 Hiring & AI Resume Screening", font=("Arial", 16, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=10)

    notebook = ttk.Notebook(content)
    notebook.pack(fill="both", expand=True, padx=20, pady=5)

    style = ttk.Style()
    style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
    style.configure("TNotebook.Tab", background="#16213e", foreground="white",
                    font=("Arial", 10, "bold"), padding=[15, 8])
    style.map("TNotebook.Tab", background=[("selected", "#e94560")])

    tab1 = tk.Frame(notebook, bg="#1a1a2e")
    notebook.add(tab1, text="📋 Applications")

    tab2 = tk.Frame(notebook, bg="#1a1a2e")
    notebook.add(tab2, text="🤖 AI Resume Screener")

    build_applications_tab(tab1)
    build_ai_screener_tab(tab2)

def build_applications_tab(tab):
    btn_frame = tk.Frame(tab, bg="#1a1a2e")
    btn_frame.pack(fill="x", padx=10, pady=10)

    tree_ref = [None]

    tk.Button(btn_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: load_applications(tree_ref[0])).pack(side="left", padx=5)

    tk.Button(btn_frame, text="✅ Accept", font=("Arial", 10, "bold"),
              bg="#00aa44", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: update_status(tree_ref[0], "Accepted")).pack(side="left", padx=5)

    tk.Button(btn_frame, text="❌ Reject", font=("Arial", 10, "bold"),
              bg="#aa0000", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: update_status(tree_ref[0], "Rejected")).pack(side="left", padx=5)

    tk.Button(btn_frame, text="🗑 Delete", font=("Arial", 10, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=15, pady=8, command=lambda: delete_application(tree_ref[0])).pack(side="left", padx=5)

    table_frame = tk.Frame(tab, bg="#1a1a2e")
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)

    scrollbar = ttk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    columns = ("ID", "Name", "Email", "Position", "AI Score", "Status", "Date")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                        yscrollcommand=scrollbar.set, height=12)

    style = ttk.Style()
    style.configure("Treeview", background="#16213e", foreground="white",
                    fieldbackground="#16213e", font=("Arial", 10), rowheight=30)
    style.configure("Treeview.Heading", background="#e94560", foreground="white",
                    font=("Arial", 10, "bold"))

    widths = [50, 130, 160, 130, 80, 100, 100]
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")

    tree.pack(fill="both", expand=True)
    scrollbar.config(command=tree.yview)
    tree_ref[0] = tree
    load_applications(tree)

def load_applications(tree):
    for row in tree.get_children():
        tree.delete(row)
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT app_id, applicant_name, email, position_applied,
                   ai_score, status, applied_date
            FROM job_applications ORDER BY app_id ASC
        """)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

def update_status(tree, status):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an application!")
        return
    app_id = tree.item(selected[0])["values"][0]
    name = tree.item(selected[0])["values"][1]
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE job_applications SET status=%s WHERE app_id=%s", (status, app_id))

            # If accepted, automatically add to employees table
            if status == "Accepted":
                cursor.execute("""
                    SELECT applicant_name, email, position_applied
                    FROM job_applications WHERE app_id=%s
                """, (app_id,))
                applicant = cursor.fetchone()

                if applicant:
                    app_name, app_email, app_position = applicant

                    # Check if already exists in employees
                    cursor.execute("SELECT emp_id FROM employees WHERE email=%s", (app_email,))
                    existing = cursor.fetchone()

                    if not existing:
                        cursor.execute("""
                            INSERT INTO employees (name, email, position, joining_date, status)
                            VALUES (%s, %s, %s, CURDATE(), 'Active')
                        """, (app_name, app_email, app_position))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success",
                            f"'{name}' accepted and added to Employees! ✅")
                    else:
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Info",
                            f"'{name}' accepted but already exists in Employees!")
            else:
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"'{name}' marked as {status}!")

            load_applications(tree)
    except Exception as e:
        messagebox.showerror("Error", f"Failed!\n{e}")

def delete_application(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an application!")
        return
    app_id = tree.item(selected[0])["values"][0]
    name = tree.item(selected[0])["values"][1]
    if messagebox.askyesno("Confirm", f"Delete application for '{name}'?"):
        try:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM job_applications WHERE app_id=%s", (app_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Application deleted!")
                load_applications(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed!\n{e}")

def build_ai_screener_tab(tab):
    canvas = tk.Canvas(tab, bg="#1a1a2e", highlightthickness=0)
    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    inner = tk.Frame(canvas, bg="#1a1a2e")
    canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

    def on_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", on_resize)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner.bind("<Configure>", on_frame_configure)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    tk.Label(inner, text="Applicant Details", font=("Arial", 12, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(anchor="w", padx=20, pady=(15, 5))

    fields = {}

    def make_field(label):
        tk.Label(inner, text=label, font=("Arial", 10),
                 bg="#1a1a2e", fg="white").pack(anchor="w", padx=20)
        entry = tk.Entry(inner, font=("Arial", 11), width=50, bg="#16213e",
                         fg="white", insertbackground="white", relief="flat", bd=5)
        entry.pack(anchor="w", padx=20, pady=(2, 8))
        fields[label] = entry

    make_field("Applicant Name")
    make_field("Email")
    make_field("Position Applied For")

    # File upload buttons
    file_frame = tk.Frame(inner, bg="#1a1a2e")
    file_frame.pack(anchor="w", padx=20, pady=(5, 0))

    tk.Label(file_frame, text="Upload Resume File:", font=("Arial", 10),
             bg="#1a1a2e", fg="white").pack(side="left", padx=(0, 10))

    tk.Button(file_frame, text="📄 Upload PDF", font=("Arial", 9, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=10, pady=5, command=lambda: upload_file("pdf")).pack(side="left", padx=5)

    tk.Button(file_frame, text="📝 Upload Word", font=("Arial", 9, "bold"),
              bg="#16213e", fg="white", relief="flat", cursor="hand2",
              padx=10, pady=5, command=lambda: upload_file("docx")).pack(side="left", padx=5)

    file_label = tk.Label(inner, text="No file selected", font=("Arial", 9),
                          bg="#1a1a2e", fg="gray")
    file_label.pack(anchor="w", padx=20, pady=(3, 5))

    tk.Label(inner, text="Or Paste Resume Text Below", font=("Arial", 10),
             bg="#1a1a2e", fg="white").pack(anchor="w", padx=20)

    resume_text = tk.Text(inner, font=("Arial", 10), width=55, height=6,
                          bg="#16213e", fg="white", insertbackground="white",
                          relief="flat", bd=5)
    resume_text.pack(anchor="w", padx=20, pady=(2, 10))

    def upload_file(file_type):
        if file_type == "pdf":
            filepath = filedialog.askopenfilename(
                title="Select PDF Resume",
                filetypes=[("PDF files", "*.pdf")]
            )
            if filepath:
                try:
                    import PyPDF2
                    with open(filepath, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                    resume_text.delete("1.0", tk.END)
                    resume_text.insert("1.0", text)
                    file_label.config(text=f"✅ Loaded: {filepath.split('/')[-1]}", fg="#00ff88")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read PDF!\n{e}")

        elif file_type == "docx":
            filepath = filedialog.askopenfilename(
                title="Select Word Resume",
                filetypes=[("Word files", "*.docx")]
            )
            if filepath:
                try:
                    import docx
                    doc = docx.Document(filepath)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    resume_text.delete("1.0", tk.END)
                    resume_text.insert("1.0", text)
                    file_label.config(text=f"✅ Loaded: {filepath.split('/')[-1]}", fg="#00ff88")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read Word file!\n{e}")

    status_label = tk.Label(inner, text="", font=("Arial", 10),
                            bg="#1a1a2e", fg="#00ff88")
    status_label.pack(padx=20)

    tk.Button(inner, text="🤖 Screen Resume with AI", font=("Arial", 11, "bold"),
              bg="#e94560", fg="white", relief="flat", cursor="hand2",
              padx=20, pady=10, command=lambda: screen_resume()).pack(pady=15)

    tk.Label(inner, text="🤖 AI Analysis Result", font=("Arial", 12, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(anchor="w", padx=20, pady=(15, 5))

    score_label = tk.Label(inner, text="Score: --", font=("Arial", 20, "bold"),
                           bg="#1a1a2e", fg="#00ff88")
    score_label.pack(padx=20)

    feedback_frame = tk.Frame(inner, bg="#1a1a2e")
    feedback_frame.pack(fill="x", padx=20, pady=10)

    feedback_scroll = ttk.Scrollbar(feedback_frame)
    feedback_scroll.pack(side="right", fill="y")

    feedback_text = tk.Text(feedback_frame, font=("Arial", 10), width=55, height=20,
                            bg="#16213e", fg="white", relief="flat", bd=5,
                            wrap="word", state="disabled",
                            yscrollcommand=feedback_scroll.set)
    feedback_text.pack(side="left", fill="both", expand=True)
    feedback_scroll.config(command=feedback_text.yview)
    def screen_resume():
        name = fields["Applicant Name"].get()
        email = fields["Email"].get()
        position = fields["Position Applied For"].get()
        resume = resume_text.get("1.0", tk.END).strip()

        if not name or not position or not resume:
            messagebox.showwarning("Warning", "Name, Position and Resume text are required!")
            return

        status_label.config(text="⏳ AI is analyzing resume...", fg="#ffaa00")
        inner.update()

        try:
            prompt = f"""
You are an expert HR recruiter. Analyze the following resume for the position of '{position}'.

Resume:
{resume}

Provide:
1. A score out of 100
2. Key strengths (2-3 points)
3. Areas of concern (2-3 points)
4. Overall recommendation (Hire / Maybe / Reject)

Format:
SCORE: [number]
STRENGTHS:
- [point 1]
- [point 2]
CONCERNS:
- [point 1]
- [point 2]
RECOMMENDATION: [Hire/Maybe/Reject]
SUMMARY: [2-3 sentences]
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )

            ai_response = response.choices[0].message.content
            score = 0
            for line in ai_response.split("\n"):
                if line.startswith("SCORE:"):
                    try:
                        score = int(line.replace("SCORE:", "").strip())
                    except:
                        score = 0
                    break

            score_color = "#00ff88" if score >= 70 else "#ffaa00" if score >= 50 else "#ff4444"
            score_label.config(text=f"Score: {score}/100", fg=score_color)

            feedback_text.config(state="normal")
            feedback_text.delete("1.0", tk.END)
            feedback_text.insert("1.0", ai_response)
            feedback_text.config(state="disabled")

            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO job_applications
                    (applicant_name, email, position_applied, resume_text, ai_score, ai_feedback, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Reviewed')
                """, (name, email, position, resume, score, ai_response))
                conn.commit()
                conn.close()

            status_label.config(text="✅ Analysis complete & saved!", fg="#00ff88")

        except Exception as e:
            status_label.config(text=f"❌ Error: {e}", fg="#ff4444")
