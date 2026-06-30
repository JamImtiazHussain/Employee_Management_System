# Employee Management System

A web-based employee management system with login, employee/department/salary
CRUD, and AI-powered resume screening (via Groq).

Originally a Tkinter desktop app backed by MySQL; rebuilt here as a Streamlit
web app backed by SQLite for free, simple deployment on Streamlit Community
Cloud.

## Setup

1. Add your Groq API key to Streamlit secrets as `GROQ_API_KEY` (required
   only for the AI Resume Screener tab).
2. Default login: `admin` / `admin123`

## Notes

- Data is stored in a local SQLite file. On Streamlit Community Cloud's free
  tier, this file does **not** persist across redeploys or container
  restarts — this is expected for a portfolio/demo deployment.
