import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import json
import os

# -------------------
# User authentication
# -------------------
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

# -------------------
# Streamlit page config
# -------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# -------------------
# CSS styling
# -------------------
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

# -------------------
# Gemini API setup
# -------------------
st.sidebar.title("🔑 API Key Setup")
api_key = st.secrets.get("gemini_api", None) or st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar or configure it in st.secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# -------------------
# Helper functions
# -------------------
def show_logo(path, width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center; align-items:center; margin-bottom:10px;">
            <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.25);">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png' in the app folder.")

def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=14)
    story = []
    for paragraph in text.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), normal_style))
            story.append(Spacer(1, 6))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph.strip())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# -------------------
# Generate lesson
# -------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            if "lesson_history" not in st.session_state:
                st.session_state["lesson_history"] = []
            st.session_state["lesson_history"].append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

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

            pdf_buffer = create_pdf(clean_output)
            docx_buffer = create_docx(clean_output)

            st.markdown(f"""
            <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                    <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ TXT</button>
                </a>
                <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                    <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ PDF</button>
                </a>
                <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buffer.read()).decode()}" download="lesson_plan.docx">
                    <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white; cursor:pointer;">⬇ DOCX</button>
                </a>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg:
                st.error("⚠️ Invalid or missing API key. Please check your Gemini key.")
            elif "quota" in error_msg:
                st.error("⚠️ API quota exceeded. Please try again later.")
            else:
                st.error(f"Error generating lesson plan: {e}")

# -------------------
# Login/Register pages
# -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login_page():
    st.header("Login / Register")
    show_logo("logo.png", width=200)
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

    choice = st.radio("Choose an option", ["Login", "Register"])

    if choice == "Login":
        login_input = st.text_input("Username or Email")
        login_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = login_user(login_input, login_pass)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = msg
                st.success(f"Welcome back, {msg}!")
                st.experimental_rerun()
            else:
                st.error(msg)

    elif choice == "Register":
        reg_user = st.text_input("Choose a username")
        reg_email = st.text_input("Your email")
        reg_pass = st.text_input("Choose a password", type="password")
        reg_confirm = st.text_input("Confirm password", type="password")
        if st.button("Register"):
            if reg_pass != reg_confirm:
                st.error("Passwords do not match.")
            else:
                success, msg = register_user(reg_user, reg_email, reg_pass)
                if success:
                    st.success(msg + " Please login now.")
                else:
                    st.error(msg)

def lesson_generator_page():
    show_logo("logo.png", width=200)
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

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
        st.session_state["last_prompt"] = prompt
        generate_and_display_plan(prompt, title="Original")

# -------------------
# Main page routing
# -------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        lesson_generator_page()

main()