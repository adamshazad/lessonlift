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
# CSS (keep your look & feel)
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
# Safe rerun flag (fixes first-click errors)
# -------------------------------
if "needs_rerun" not in st.session_state:
    st.session_state.needs_rerun = False

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
# Users store (simple JSON)
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
# API key setup (secrets or sidebar)
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
# Exporters (PDF & DOCX)
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    story = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            story.append(Spacer(1, 6))
        else:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
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
# Core generator
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
                for i, m in enumerate(matches):
                    sec_name = m.group(1).capitalize()
                    start_idx = m.end()
                    end_idx = matches[i+1].start() if i+1 < len(matches) else len(clean_output)
                    section_text = clean_output[start_idx:end_idx].strip()
                    st.markdown(f"<div class='stCard'><b>{sec_name}</b><br>{section_text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)

            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

            pdf_buffer = create_pdf(clean_output)
            docx_buffer = create_docx(clean_output)
            st.markdown(
                f"""
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
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            msg = str(e).lower()
            if "api key" in msg:
                st.error("⚠️ Invalid or missing API key. Please check your Gemini key.")
            elif "quota" in msg:
                st.error("⚠️ API quota exceeded. Please try again later.")
            else:
                st.error(f"Error generating lesson plan: {e}")

# -------------------------------
# Pages
# -------------------------------
def login_page():
    show_logo("logo.png", width=200)
    title_and_tagline()

    st.subheader("Teacher Sign In / Register")
    tab_login, tab_register = st.tabs(["🔓 Login", "🆕 Register"])

    with tab_login:
        login_user_or_email = st.text_input("Username or Email", key="login_username_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        colA, colB = st.columns([1,1])
        with colA:
            if st.button("Login", key="login_btn"):
                success, result = login_user(login_user_or_email, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = result
                    st.session_state.page = "generator"
                    st.session_state.needs_rerun = True
                    st.success(f"Welcome back, {result}!")
                    return  # immediately stop rest of page to avoid first-click errors
                else:
                    st.error(result)
        with colB:
            st.write("")

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
                ok, msg = register_user(reg_username, reg_email, reg_password)
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
        st.session_state.needs_rerun = True
        return  # safe rerun

    st.sidebar.header("📚 Lesson History")
    for i, lesson in enumerate(reversed(st.session_state.lesson_history)):
        if st.sidebar.button(lesson["title"], key=f"hist_{i}"):
            st.markdown(f"<div class='stCard'><b>{lesson['title']}</b><br>{lesson['content']}</div>", unsafe_allow_html=True)

    show_logo("logo.png", width=200)
    title_and_tagline()
    st.caption(f"Logged in as **{st.session_state.username}**")

    if not api_key:
        st.error("No Gemini API key found. Add it in the sidebar to generate plans.")
        return

    submitted = False
    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"], key="year_group")
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"], key="ability_level")
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"], key="lesson_duration")
        lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. English, Maths, Science", key="subject")
        lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth", key="topic")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions", key="lo")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters", key="sen")
        submitted = st.form_submit_button("🚀 Generate Lesson Plan")

    if submitted:
        prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {lesson_data['year_group']}
Subject: {lesson_data['subject']}
Topic: {lesson_data['topic']}
Learning Objective: {lesson_data['learning_objective'] or 'Not specified'}
Ability Level: {lesson_data['ability_level']}
Lesson Duration: {lesson_data['lesson_duration']}
SEN/EAL Notes: {lesson_data['sen_notes'] or 'None'}
"""
        st.session_state.last_prompt = prompt
        generate_and_display_plan(prompt, title="Original")

    if st.session_state.last_prompt:
        st.markdown("### 🔄 Not happy with the plan?")
        regen_style = st.selectbox(
            "Choose a regeneration style:",
            [
                "♻️ Just regenerate (different variation)",
                "🎨 More creative & engaging activities",
                "📋 More structured with timings",
                "🧩 Simplify for lower ability",
                "🚀 Challenge for higher ability"
            ],
            key="regen_style"
        )

        custom_instruction = st.text_input(
            "Or type your own custom instruction (optional)",
            placeholder="e.g. Make it more interactive with outdoor activities",
            key="custom_instruction"
        )

        if st.button("🔁 Regenerate Lesson Plan", key="regen_btn"):
            extra_instruction = ""
            regen_message = ""

            if not custom_instruction:
                if regen_style == "🎨 More creative & engaging activities":
                    extra_instruction = "Make activities more creative, interactive, and fun."
                    regen_message = "Lesson updated with more creative and engaging activities."
                elif regen_style == "📋 More structured with timings":
                    extra_instruction = "Add clear structure with timings for each section."
                    regen_message = "Lesson updated with clearer structure and timings."
                elif regen_style == "🧩 Simplify for lower ability":
                    extra_instruction = "Adapt for lower ability: simpler language, more scaffolding, step-by-step."
                    regen_message = "Lesson simplified for lower ability."
                elif regen_style == "🚀 Challenge for higher ability":
                    extra_instruction = "Adapt for higher ability: include stretch/challenge tasks and deeper thinking questions."
                    regen_message = "Lesson updated with higher ability challenge tasks."
                else:
                    regen_message = "Here’s a new updated version of your lesson plan."
            else:
                extra_instruction = custom_instruction
                regen_message = f"Lesson updated: {custom_instruction}"

            new_prompt = st.session_state.last_prompt + "\n\n" + extra_instruction
            generate_and_display_plan(new_prompt, title=f"Regenerated {len(st.session_state.lesson_history)+1}", regen_message=regen_message)

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

    if st.session_state.needs_rerun:
        st.session_state.needs_rerun = False
        st.experimental_rerun()

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    main()