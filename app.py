import streamlit as st
import google.generativeai as genai
import re
import base64
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# -------------------------------
# CSS
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
    max-height: 300px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Safe rerun flag
# -------------------------------
if "trigger_rerun" not in st.session_state:
    st.session_state.trigger_rerun = False

# -------------------------------
# Session defaults
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None

# -------------------------------
# Users store (JSON)
# -------------------------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, email, password):
    users = load_users()
    if username in users or any(u.get("email","").lower() == email.lower() for u in users.values()):
        return False, "Username or email already exists."
    users[username] = {"email": email, "password": password}
    save_users(users)
    return True, "Registration successful! Please login."

def login_user(username_or_email, password):
    users = load_users()
    for uname, data in users.items():
        if (uname.lower() == username_or_email.lower() or data.get("email","").lower() == username_or_email.lower()) and data.get("password") == password:
            return True, uname
    return False, "Invalid username/email or password."

# -------------------------------
# API key setup
# -------------------------------
api_key = st.secrets.get("gemini_api", None)
if not api_key:
    st.sidebar.title("🔑 API Key Setup")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    model = None

# -------------------------------
# UI helpers
# -------------------------------
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; align-items:center; margin-bottom:16px;">
                <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                    <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;" />
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png' to the app folder.")

def title_and_tagline():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# -------------------------------
# Exporters
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    story = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            story.append(Spacer(1,6))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, normal))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for raw in text.splitlines():
        doc.add_paragraph(raw.rstrip())
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# Generator
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    if not model:
        st.error("⚠️ No Gemini API key found. Add it in the sidebar or in st.secrets['gemini_api'].")
        return

    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            st.session_state.lesson_history.append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            sections = [
                "Lesson title","Learning outcomes","Starter activity","Main activity",
                "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
            ]
            pattern = re.compile(r"(" + "|".join(sections) + r")[:\s]*", re.IGNORECASE)
            matches = list(pattern.finditer(clean_output))
            if matches:
                for i,m in enumerate(matches):
                    sec_name = m.group(1).capitalize()
                    start_idx = m.end()
                    end_idx = matches[i+1].start() if i+1<len(matches) else len(clean_output)
                    section_text = clean_output[start_idx:end_idx].strip()
                    st.markdown(f"<div class='stCard'><b>{sec_name}</b><br>{section_text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)

# -------------------------------
# Pages
# -------------------------------
def login_page():
    show_logo()
    title_and_tagline()
    st.subheader("Teacher Sign In / Register")

    tab_login, tab_register = st.tabs(["🔓 Login","🆕 Register"])
    with tab_login:
        login_user_or_email = st.text_input("Username or Email", key="login_username_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            success,result = login_user(login_user_or_email, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = result
                st.session_state.page = "generator"
                st.session_state.trigger_rerun = True
            else:
                st.error(result)

    with tab_register:
        reg_username = st.text_input("Choose a username", key="reg_username")
        reg_email = st.text_input("Your email", key="reg_email")
        reg_password = st.text_input("Choose a password", type="password", key="reg_password")
        reg_password2 = st.text_input("Confirm password", type="password", key="reg_password2")
        if st.button("Create account", key="register_btn"):
            if not reg_username or not reg_email or not reg_password:
                st.error("Please fill in all fields.")
            elif reg_password != reg_password2:
                st.error("Passwords do not match.")
            else:
                ok,msg = register_user(reg_username, reg_email, reg_password)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    if not api_key:
        st.info("Tip: Add your Gemini API key in the sidebar to enable plan generation.")

def lesson_generator_page():
    st.sidebar.header("Account")
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.session_state.trigger_rerun = True

    st.sidebar.header("📚 Lesson History")
    for i, lesson in enumerate(reversed(st.session_state.lesson_history)):
        if st.sidebar.button(lesson["title"], key=f"hist_{i}"):
            st.markdown(f"<div class='stCard'><b>{lesson['title']}</b><br>{lesson['content']}</div>", unsafe_allow_html=True)

    show_logo()
    title_and_tagline()
    st.caption(f"Logged in as **{st.session_state.username}**")

# -------------------------------
# Main router
# -------------------------------
def main():
    if st.session_state.logged_in:
        st.session_state.page = "generator"
    else:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    else:
        lesson_generator_page()

    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = False
        st.experimental_rerun()

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    main()