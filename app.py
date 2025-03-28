import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px


# --- Set Google Drive synced folder path ---
# Replace this with the correct path where your Google Drive is synced
DRIVE_PATH = "G:/My Drive/JobTracker"  # Modify this to match your actual path
CSV_FILE = os.path.join(DRIVE_PATH, "applications.csv")
RESUME_FOLDER = os.path.join(DRIVE_PATH, "resumes")

# Create folder if not exists
os.makedirs(RESUME_FOLDER, exist_ok=True)

# Load existing data or initialize DataFrame
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Company", "Job Description", "Date Applied", "Time Applied", "Resume File"])

# --- Streamlit UI ---
st.set_page_config(page_title="Job Application Tracker", layout="centered")
st.title("🗂️ Job Application Tracker")

st.header("➕ Add New Job Application")

with st.form("job_form"):
    company = st.text_input("🏢 Company Name")
    jd = st.text_area("📝 Job Description")
    uploaded_resume = st.file_uploader("📎 Upload Resume", type=["pdf", "docx"])
    submitted = st.form_submit_button("Save Application")

    if submitted:
        if not company or not jd or not uploaded_resume:
            st.error("❗ Please complete all fields including uploading a resume.")
        else:
            now = datetime.now()
            date_applied = now.strftime("%Y-%m-%d")
            time_applied = now.strftime("%H:%M:%S")

            # Save resume
            resume_filename = f"Ankit Kumar - {company} - CV.pdf"
            resume_path = os.path.join(RESUME_FOLDER, resume_filename)
            with open(resume_path, "wb") as f:
                f.write(uploaded_resume.getbuffer())

            # Add to DataFrame
            new_entry = {
                "Company": company,
                "Job Description": jd,
                "Date Applied": date_applied,
                "Time Applied": time_applied,
                "Resume File": resume_filename
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)

            st.success("✅ Application saved!")

st.subheader("🗂️ Applications by Date")

if not df.empty:
    df["Date Group"] = pd.to_datetime(df["Date Applied"]).dt.date
    grouped = df.groupby("Date Group")

    # Helper function to get the date in "28th March 2025" format
    def format_fancy_date(d):
        day = d.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{day}{suffix} {d.strftime('%B %Y')}"

    # Group and display applications by date
    for date, group in grouped:
        formatted_date = format_fancy_date(date)
        with st.expander(f"📅 {formatted_date} ({len(group)} application(s))", expanded=False):
            for _, row in group.iterrows():
                st.markdown(f"**🏢 Company:** {row['Company']}")
                st.markdown(f"**🕒 Applied At:** {row['Date Applied']}")
                st.markdown(f"**📎 Resume File:** `{row['Resume File']}`")
                st.markdown("**📄 Job Description:**")
                st.markdown(f"`{row['Job Description']}`")
                st.markdown("---")
else:
    st.info("No applications available.")

# --- View Existing Applications ---
st.subheader("📊 Application Trend")

# Convert 'Date Applied' to datetime and extract date only
df["Date Applied"] = pd.to_datetime(df["Date Applied"])
df["Date"] = df["Date Applied"].dt.date

# Group and count applications per date
daily_counts = df.groupby("Date").size().reset_index(name="Applications")

# Line chart
fig = px.line(
    daily_counts,
    x="Date",
    y="Applications",
    title="Jobs Applied Over Time",
    markers=True,
    labels={"Date": "Date", "Applications": "Number of Applications"},
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

