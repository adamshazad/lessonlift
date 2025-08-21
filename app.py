import streamlit as st
import json
import os
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from docx import Document
import google.generativeai as genai

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift AI", page_icon="📘", layout="centered")

# -------------------------------
# CSS styling
# -------------------------------
st.markdown("""
<style>
body {background-color: white; color: black;}
.stTextInput>div>div>input, textarea, select {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
    padding: 8px !important;
    border-radius: 5px !important;
}
.stCard {
    background-color: #f9f9f9 !important;
    color: black !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.15) !important;
    line-height: 1.5em;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# User authentication
# -------------------------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, email, password):
    users = load_users()
    if username in users or email in [u["email"] for u in users.values()]:
        return False, "Username or email already exists."
    users[username] = {"email": email, "password": password}
    save_users(users)
    return True, "Registration successful!"

def login_user(username_or_email, password):
    users = load_users()
    for username, data in users.items():
        if (username == username_or_email or data["email"] == username_or_email) and data["password"] == password:
            return True, username
    return False, "Invalid username/email or password."

# -------------------------------
# Session state for login and page
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []

# -------------------------------
# Logo display
# -------------------------------
def show_logo(path, width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center; align-items:center; margin-bottom:10px;">
            <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png' in the app folder.")

# -------------------------------
# PDF generator
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=14, alignment=TA_LEFT)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceBefore=12, spaceAfter=6)
    story = []
    lines = text.splitlines()
    current_list = []
    sections_keywords = [
        "lesson title","learning outcomes","starter activity","main activity",
        "plenary activity","resources needed","differentiation ideas","assessment methods"
    ]

    for line in lines:
        line = line.strip()
        if not line:
            if current_list:
                story.append(ListFlowable([ListItem(Paragraph(item, normal_style)) for item in current_list], bulletType='bullet'))
                current_list = []
            story.append(Spacer(1, 6))
            continue
        if any(line.lower().startswith(h) for h in sections_keywords):
            if current_list:
                story.append(ListFlowable([ListItem(Paragraph(item, normal_style)) for item in current_list], bulletType='bullet'))
                current_list = []
            story.append(Paragraph(line, heading_style))
        elif line.startswith("-") or line[0].isdigit():
            current_list.append(line)
        else:
            story.append(Paragraph(line, normal_style))
    if current_list:
        story.append(ListFlowable([ListItem(Paragraph(item, normal_style)) for item in current_list], bulletType='bullet'))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# DOCX generator
# -------------------------------
def create_docx(text):
    doc = Document()
    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph.strip())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# -------------------------------
# Helper function to clean markdown
# -------------------------------
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# -------------------------------
# Gemini AI setup
# -------------------------------
api_key = st.secrets.get("gemini_api", None)
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    st.warning("Please add your Gemini API key to st.secrets['gemini_api'].")

# -------------------------------
# Login Page
# -------------------------------
def login_page():
    show_logo("logo.png", width=200)
    st.title("📚 LessonLift AI")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

    choice = st.radio("Choose an option", ["Login", "Register"], key="login_register_choice")

    if choice == "Login":
        username_or_email = st.text_input("Username or Email", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_button"):
            success, msg = login_user(username_or_email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = msg
                st.session_state.page = "generator"
            else:
                st.error(msg)

    elif choice == "Register":
        reg_user = st.text_input("Choose a username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register", key="register_button"):
            if reg_pass != reg_confirm:
                st.error("Passwords do not match.")
            else:
                success, msg = register_user(reg_user, reg_email, reg_pass)
                if success:
                    st.success(msg + " Please login now.")
                else:
                    st.error(msg)

# -------------------------------
# Lesson Generator Page
# -------------------------------
def lesson_generator_page():
    show_logo("logo.png", width=200)
    st.title("📚 LessonLift AI")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

    st.write(f"Logged in as {st.session_state.username}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"

    # Lesson form
    submitted = False
    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
        lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")

        submitted = st.form_submit_button("🚀 Generate Lesson Plan")

    if submitted:
        prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {lesson_data['year_group']}
Ability Level: {lesson_data['ability_level']}
Lesson Duration: {lesson_data['lesson_duration']}
Subject: {lesson_data['subject']}
Topic: {lesson_data['topic']}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}
"""
        generate_and_display_plan(prompt, title="Original")

# -------------------------------
# Generate and display plan
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            st.session_state["lesson_history"].append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            # Sections display
            sections = [
                "Lesson title","Learning outcomes","Starter activity","Main activity",
                "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
            ]
            pattern = re.compile(r"(" + "|".join(sections) + r")[:\s]*", re.IGNORECASE)
            matches = list(pattern.finditer(clean_output))
            for i, match in enumerate(matches):
                sec_name = match.group(1).capitalize()
                start_idx = match.end()
                end_idx = matches[i+1].start() if i+1 < len(matches) else len(clean_output)
                section_text = clean_output[start_idx:end_idx].strip()
                st.markdown(f"<div class='stCard'><b>{sec_name}</b><br>{section_text}</div>", unsafe_allow_html=True)

            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

            # Download buttons
            pdf_buffer = create_pdf(clean_output)
            docx_buffer = create_docx(clean_output)
            st.markdown(f"""
            <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                <a href="data:text/plain;base64,{base64.b