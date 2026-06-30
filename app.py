import streamlit as st
import pandas as pd
from datetime import date

from db import get_connection, init_db

st.set_page_config(page_title="Employee Management System", page_icon="🏢", layout="wide")

init_db()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---------------- LOGIN ----------------
def login_page():
    st.title("🏢 Employee Management System")
    st.subheader("Admin Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.warning("Please enter both username and password!")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE username=? AND password=?",
                    (username, password),
                )
                user = cursor.fetchone()
                conn.close()

                if user:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid username or password!")

    st.caption("Default: admin / admin123")


# ---------------- EMPLOYEES ----------------
def employees_page():
    st.header("👥 Employee Management")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT dept_id, dept_name FROM departments")
    depts = cursor.fetchall()
    dept_options = {f"{d[0]} - {d[1]}": d[0] for d in depts}
    conn.close()

    with st.expander("+ Add New Employee"):
        with st.form("add_employee_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            position = st.text_input("Position")
            joining = st.date_input("Joining Date", value=date.today())
            dept_label = st.selectbox("Department", ["(None)"] + list(dept_options.keys()))
            add_submitted = st.form_submit_button("Save Employee")

            if add_submitted:
                if not name or not position:
                    st.warning("Name and Position are required!")
                else:
                    dept_id = dept_options.get(dept_label)
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT INTO employees (name, email, phone, position, dept_id, joining_date)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (name, email, phone, position, dept_id, str(joining)),
                    )
                    conn.commit()
                    conn.close()
                    st.success("Employee added successfully!")
                    st.rerun()

    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT e.emp_id AS ID, e.name AS Name, e.email AS Email, e.phone AS Phone,
                  e.position AS Position, IFNULL(d.dept_name, 'N/A') AS Department,
                  e.joining_date AS "Joining Date", e.status AS Status
           FROM employees e
           LEFT JOIN departments d ON e.dept_id = d.dept_id
           ORDER BY e.emp_id ASC""",
        conn,
    )
    conn.close()

    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.subheader("Edit or Delete Employee")
        selected_id = st.selectbox("Select Employee ID", df["ID"].tolist())
        selected_row = df[df["ID"] == selected_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            with st.form("edit_employee_form"):
                st.write("**Edit Employee**")
                e_name = st.text_input("Full Name", value=selected_row["Name"])
                e_email = st.text_input("Email", value=selected_row["Email"] or "")
                e_phone = st.text_input("Phone", value=selected_row["Phone"] or "")
                e_position = st.text_input("Position", value=selected_row["Position"])
                e_dept_label = st.selectbox(
                    "Department",
                    ["(None)"] + list(dept_options.keys()),
                    index=0,
                )
                edit_submitted = st.form_submit_button("Update Employee")

                if edit_submitted:
                    e_dept_id = dept_options.get(e_dept_label)
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE employees SET name=?, email=?, phone=?, position=?, dept_id=?
                           WHERE emp_id=?""",
                        (e_name, e_email, e_phone, e_position, e_dept_id, int(selected_id)),
                    )
                    conn.commit()
                    conn.close()
                    st.success("Employee updated successfully!")
                    st.rerun()

        with col2:
            st.write("**Delete Employee**")
            st.write(f"Selected: {selected_row['Name']}")
            if st.button("🗑 Delete Employee", type="primary"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM salaries WHERE emp_id=?", (int(selected_id),))
                cursor.execute("DELETE FROM employees WHERE emp_id=?", (int(selected_id),))
                conn.commit()
                conn.close()
                st.success("Employee deleted successfully!")
                st.rerun()


# ---------------- DEPARTMENTS ----------------
def departments_page():
    st.header("🏢 Department Management")

    with st.expander("+ Add New Department"):
        with st.form("add_dept_form", clear_on_submit=True):
            dept_name = st.text_input("Department Name")
            submitted = st.form_submit_button("Save Department")
            if submitted:
                if not dept_name.strip():
                    st.warning("Please enter a department name!")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO departments (dept_name) VALUES (?)", (dept_name.strip(),)
                        )
                        conn.commit()
                        conn.close()
                        st.success("Department added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add department! {e}")

    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT d.dept_id AS ID, d.dept_name AS "Department Name",
                  COUNT(e.emp_id) AS "Total Employees"
           FROM departments d
           LEFT JOIN employees e ON d.dept_id = e.dept_id
           GROUP BY d.dept_id, d.dept_name
           ORDER BY d.dept_id ASC""",
        conn,
    )
    conn.close()

    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.subheader("Delete Department")
        selected_id = st.selectbox("Select Department ID", df["ID"].tolist())
        selected_row = df[df["ID"] == selected_id].iloc[0]

        if selected_row["Total Employees"] > 0:
            st.warning(
                f"Cannot delete '{selected_row['Department Name']}'! "
                f"It has {selected_row['Total Employees']} employee(s) assigned to it."
            )
        else:
            if st.button("🗑 Delete Department", type="primary"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM departments WHERE dept_id=?", (int(selected_id),))
                conn.commit()
                conn.close()
                st.success("Department deleted successfully!")
                st.rerun()


# ---------------- SALARY ----------------
def salary_page():
    st.header("💰 Salary Management")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, name FROM employees WHERE status='Active'")
    emps = cursor.fetchall()
    emp_options = {f"{e[0]} - {e[1]}": e[0] for e in emps}
    conn.close()

    with st.expander("+ Process Salary"):
        with st.form("process_salary_form", clear_on_submit=True):
            emp_label = st.selectbox(
                "Select Employee",
                list(emp_options.keys()) if emp_options else ["(No active employees)"],
            )
            basic = st.number_input("Basic Salary", min_value=0.0, step=100.0)
            bonus = st.number_input("Bonus", min_value=0.0, step=50.0, value=0.0)
            deductions = st.number_input("Deductions", min_value=0.0, step=50.0, value=0.0)
            pay_date = st.date_input("Pay Date", value=date.today())
            net = basic + bonus - deductions
            st.write(f"**Net Salary: {net:,.2f}**")
            submitted = st.form_submit_button("Process Salary")

            if submitted:
                if not emp_options or not basic:
                    st.warning("Employee and Basic Salary are required!")
                else:
                    emp_id = emp_options[emp_label]
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT INTO salaries (emp_id, basic_salary, bonus, deductions, net_salary, pay_date)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (emp_id, basic, bonus, deductions, net, str(pay_date)),
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Salary processed! Net Salary: {net:,.2f}")
                    st.rerun()

    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT s.salary_id AS "Salary ID", e.name AS Employee, s.basic_salary AS "Basic Salary",
                  s.bonus AS Bonus, s.deductions AS Deductions, s.net_salary AS "Net Salary",
                  s.pay_date AS "Pay Date"
           FROM salaries s
           JOIN employees e ON s.emp_id = e.emp_id
           ORDER BY s.salary_id ASC""",
        conn,
    )
    conn.close()

    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.subheader("Delete Salary Record")
        selected_id = st.selectbox("Select Salary ID", df["Salary ID"].tolist())
        if st.button("🗑 Delete Salary Record", type="primary"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM salaries WHERE salary_id=?", (int(selected_id),))
            conn.commit()
            conn.close()
            st.success("Salary record deleted!")
            st.rerun()


# ---------------- HIRING & AI ----------------
def hiring_page():
    st.header("📄 Hiring & AI Resume Screening")

    tab1, tab2 = st.tabs(["📋 Applications", "🤖 AI Resume Screener"])

    with tab1:
        conn = get_connection()
        df = pd.read_sql_query(
            """SELECT app_id AS ID, applicant_name AS Name, email AS Email,
                      position_applied AS Position, ai_score AS "AI Score",
                      status AS Status, applied_date AS Date
               FROM job_applications ORDER BY app_id ASC""",
            conn,
        )
        conn.close()

        st.dataframe(df, use_container_width=True, hide_index=True)

        if not df.empty:
            selected_id = st.selectbox("Select Application ID", df["ID"].tolist())

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Accept"):
                    _update_application_status(int(selected_id), "Accepted")
                    st.rerun()
            with col2:
                if st.button("❌ Reject"):
                    _update_application_status(int(selected_id), "Rejected")
                    st.rerun()
            with col3:
                if st.button("🗑 Delete Application"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM job_applications WHERE app_id=?", (int(selected_id),))
                    conn.commit()
                    conn.close()
                    st.success("Application deleted!")
                    st.rerun()

    with tab2:
        st.subheader("Applicant Details")
        name = st.text_input("Applicant Name")
        email = st.text_input("Email", key="hiring_email")
        position = st.text_input("Position Applied For")

        st.write("Upload Resume File or paste text below")
        uploaded_file = st.file_uploader("Upload Resume (PDF or Word)", type=["pdf", "docx"])

        resume_text_default = ""
        if uploaded_file is not None:
            resume_text_default = _extract_resume_text(uploaded_file)

        resume_text = st.text_area("Resume Text", value=resume_text_default, height=200)

        if st.button("🤖 Screen Resume with AI"):
            if not name or not position or not resume_text.strip():
                st.warning("Name, Position and Resume text are required!")
            else:
                with st.spinner("AI is analyzing resume..."):
                    score, ai_response = _screen_resume(position, resume_text)

                if score is None:
                    st.error(ai_response)
                else:
                    score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                    st.write(f"{score_color} Score: {score}/100")
                    st.text_area("AI Analysis", value=ai_response, height=300, disabled=True)

                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT INTO job_applications
                           (applicant_name, email, position_applied, resume_text, ai_score, ai_feedback, status)
                           VALUES (?, ?, ?, ?, ?, ?, 'Reviewed')""",
                        (name, email, position, resume_text, score, ai_response),
                    )
                    conn.commit()
                    conn.close()
                    st.success("Analysis complete & saved!")


def _update_application_status(app_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE job_applications SET status=? WHERE app_id=?", (status, app_id))

    if status == "Accepted":
        cursor.execute(
            "SELECT applicant_name, email, position_applied FROM job_applications WHERE app_id=?",
            (app_id,),
        )
        applicant = cursor.fetchone()
        if applicant:
            app_name, app_email, app_position = applicant
            cursor.execute("SELECT emp_id FROM employees WHERE email=?", (app_email,))
            existing = cursor.fetchone()
            if not existing:
                cursor.execute(
                    """INSERT INTO employees (name, email, position, joining_date, status)
                       VALUES (?, ?, ?, date('now'), 'Active')""",
                    (app_name, app_email, app_position),
                )
                st.success(f"'{app_name}' accepted and added to Employees!")
            else:
                st.info(f"'{app_name}' accepted but already exists in Employees!")

    conn.commit()
    conn.close()


def _extract_resume_text(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            import PyPDF2

            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            import docx

            doc = docx.Document(uploaded_file)
            return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        st.error(f"Failed to read file! {e}")
        return ""


def _screen_resume(position, resume):
    try:
        from groq import Groq

        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            return None, "GROQ_API_KEY is not configured in Streamlit secrets."

        client = Groq(api_key=api_key)

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
            max_tokens=500,
        )

        ai_response = response.choices[0].message.content
        score = 0
        for line in ai_response.split("\n"):
            if line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip())
                except ValueError:
                    score = 0
                break

        return score, ai_response

    except Exception as e:
        return None, f"Error: {e}"


# ---------------- MAIN APP / NAVIGATION ----------------
def main_app():
    st.sidebar.title("🏢 Employee Management")
    st.sidebar.write("Welcome, Admin!")

    page = st.sidebar.radio(
        "Navigation",
        ["Employees", "Departments", "Salary", "Hiring & AI"],
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    if page == "Employees":
        employees_page()
    elif page == "Departments":
        departments_page()
    elif page == "Salary":
        salary_page()
    elif page == "Hiring & AI":
        hiring_page()


# ---------------- ENTRY POINT ----------------
if st.session_state.logged_in:
    main_app()
else:
    login_page()
