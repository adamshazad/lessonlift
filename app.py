import streamlit as st
import os
import json
import re
import base64
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
import google.generativeai as genai

# ---------------------------
# Configuration
# ---------------------------
USER_FILE = "users.json"

# Ensure users.json exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# ---------------------------
# User Management
# ---------------------------
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, email, password):
    users = load_users()
    if username in users or any(u.get("email") == email for u in users.values()):
        return False, "Username or email already exists"
    users[username] = {"email": email, "password": password}
    save_users(users)
    return True, "Account created successfully!"

def login_user(username_or_email, password):
    users = load_users()
    for username, details in users.items():
        if username_or_email == username or username_or_email == details.get("email"):
            if details["password"] == password:
                return True, username
    return False, "Invalid username/email or password"

# ---------------------------
# PDF / DOCX Export
# ---------------------------
def export_to_pdf(text, title="Lesson Plan"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    flow = []

    for line in text.split("\n"):
        if line.strip():
            flow.append(Paragraph(line, styles["Normal"]))
            flow.append(Spacer(1, 12))
    doc.build(flow)

    buffer.seek(0)
    return buffer

def export_to_docx(text, title="Lesson Plan"):
    buffer = BytesIO()
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------------------
# Lesson Generator
# ---------------------------
def generate_and_display_plan(prompt, title="Generated"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text"):
            st.error("⚠️ No response from model.")
            return

        lesson_text = response.text.strip()
        st.subheader(f"📘 {title} Lesson Plan")
        st.text_area("Generated Lesson Plan", lesson_text, height=400)

        # Save to session history
        st.session_state.history.append(lesson_text)

        # Downloads
        pdf_buffer = export_to_pdf(lesson_text, title)
        docx_buffer = export_to_docx(lesson_text, title)

        pdf_buffer.seek(0)
        docx_buffer.seek(0)

        st.download_button(
            "⬇️ Download PDF",
            data=pdf_buffer,
            file_name="lesson_plan.pdf",
            mime="application/pdf"
        )
        st.download_button(
            "⬇️ Download DOCX",
            data=docx_buffer,
            file_name="lesson_plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.download_button(
            "⬇️ Download TXT",
            data=lesson_text,
            file_name="lesson_plan.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"⚠️ Something went wrong: {str(e)}")

# ---------------------------
# Pages
# ---------------------------
def login_page():
    st.image("logo.png", use_container_width=True)
    st.title("📚 LessonLift")
    st.write("Generate lessons in seconds 🚀")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab1:
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = login_user(username_or_email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = msg
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        new_username = st.text_input("Choose Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            success, msg = register_user(new_username, new_email, new_password)
            if success:
                st.success(msg)
            else:
                st.error(msg)

def lesson_generator_page():
    # Sidebar info
    st.sidebar.image("logo.png", use_container_width=True)
    st.sidebar.success(f"✅ Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # Main page
    st.title("📚 LessonLift")
    st.write("Generate lessons in seconds 🚀")

    subject = st.text_input("📘 Subject")
    topic = st.text_input("🎯 Topic")
    year_group = st.text_input("🏫 Year Group")
    ability_level = st.text_input("📊 Ability Level")
    duration = st.text_input("⏳ Lesson Duration (minutes)")

    if st.button("✨ Generate Lesson"):
        if not subject or not topic:
            st.error("⚠️ Please enter subject and topic.")
        else:
            prompt = (
                f"Create a detailed lesson plan.\n"
                f"Subject: {subject}\n"
                f"Topic: {topic}\n"
                f"Year Group: {year_group}\n"
                f"Ability Level: {ability_level}\n"
                f"Lesson Duration: {duration} minutes"
            )
            st.info("✨ Creating your lesson plan...")
            generate_and_display_plan(prompt, title=topic or "Lesson")

    # History
    if st.session_state.history:
        st.subheader("📜 Lesson History")
        for i, lesson in enumerate(st.session_state.history, 1):
            with st.expander(f"Lesson {i}"):
                st.text_area("Lesson", lesson, height=200)

# ---------------------------
# Main
# ---------------------------
def main():
    st.set_page_config(page_title="LessonLift", page_icon="📚")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.history = []

    if not st.session_state.logged_in:
        login_page()
    else:
        lesson_generator_page()

if __name__ == "__main__":
    main()