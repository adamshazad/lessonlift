# app.py - Final LessonLift (copy-paste ready)
import streamlit as st
import json
import os
import re
import base64
from io import BytesIO

# ReportLab for PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

# DOCX
from docx import Document

# Optional Gemini (only used if available & API key provided)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# --------------------------
# Config + CSS
# --------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

st.markdown(
    """
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
    .button-row a { text-decoration: none !important; }
    .button-row button {
        padding:10px 16px; font-size:14px; border-radius:8px; border:none;
        background-color:#4CAF50; color:white; cursor:pointer;
    }
    img.app-logo { border-radius:12px; box-shadow:0px 8px 24px rgba(0,0,0,0.25); }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# Auth helpers (persistent JSON)
# --------------------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, email, password):
    users = load_users()
    if not username or not email or not password:
        return False, "Please fill all fields."
    # check duplicates
    if username in users or any(u["email"].lower() == email.lower() for u in users.values()):
        return False, "Username or email already exists."
    users[username] = {"email": email, "password": password}
    save_users(users)
    return True, "Registration successful!"

def login_user(username_or_email, password):
    users = load_users()
    for username, data in users.items():
        if (username.lower() == username_or_email.lower() or data["email"].lower() == username_or_email.lower()):
            if data["password"] == password:
                return True, username
    return False, "Invalid username/email or password."

# --------------------------
# Logo + header helpers
# --------------------------
def show_logo_image(path="logo.png", width=200):
    """Show logo reliably on top using st.image if possible; fallback to base64 HTML."""
    try:
        st.image(path, width=width, use_column_width=False, output_format="PNG")
        return
    except Exception:
        # fallback to base64 HTML
        try:
            with open(path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(
                f'<div style="display:flex;justify-content:center;"><img class="app-logo" src="data:image/png;base64,{b64}" width="{width}"/></div>',
                unsafe_allow_html=True
            )
        except FileNotFoundError:
            st.warning("Logo file not found. Please upload 'logo.png' in the app folder.")

def show_title():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

# --------------------------
# PDF / DOCX builders
# --------------------------
SECTION_KEYS = [
    "Lesson title","Learning outcomes","Starter activity","Main activity",
    "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"
]

def build_pdf_story_from_text(text: str):
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.darkblue,
        spaceBefore=10,
        spaceAfter=6
    )

    def is_heading(line: str) -> bool:
        lower = line.strip().lower().rstrip(":")
        return any(lower.startswith(h.lower()) for h in SECTION_KEYS)

    story = []
    lines = text.splitlines()
    current_list = []

    def flush_list():
        nonlocal current_list, story
        if current_list:
            story.append(ListFlowable([ListItem(Paragraph(item, normal)) for item in current_list], bulletType='bullet'))
            current_list = []

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_list()
            story.append(Spacer(1, 6))
            continue

        # Heading?
        if is_heading(line):
            flush_list()
            title_line = line.rstrip(":")
            story.append(Paragraph(title_line, heading))
            continue

        # Bullet-like
        if re.match(r"^(-|\u2022|•|\d+[\.\)])\s+", line):
            # strip bullet marker
            current_list.append(re.sub(r"^(-|\u2022|•|\d+[\.\)])\s+", "", line))
            continue

        # Normal paragraph
        flush_list()
        story.append(Paragraph(line, normal))

    flush_list()
    return story

def create_pdf_wrapped(text: str) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = build_pdf_story_from_text(text)
    doc.build(story)
    buf.seek(0)
    return buf

def create_docx(text: str) -> BytesIO:
    doc = Document()
    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph.strip())
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --------------------------
# Simple markdown stripper
# --------------------------
def strip_markdown(md_text: str) -> str:
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# --------------------------
# Session state defaults
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None

# --------------------------
# Top: logo + title (always)
# --------------------------
show_logo_image("logo.png", width=200)
show_title()

# --------------------------
# Login/Register (tabs) - shown before generator
# --------------------------
if not st.session_state.logged_in:
    st.markdown("### 🔐 Teacher Access")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        col1, col2 = st.columns([2,1])
        with col1:
            login_input = st.text_input("Username or Email")
        with col2:
            login_pass = st.text_input("Password", type="password")

        if st.button("🔓 Login"):
            ok, who = login_user(login_input or "", login_pass or "")
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = who
                st.success(f"Welcome back, {who}!")
                try:
                    st.rerun()
                except Exception:
                    st.experimental_rerun()
            else:
                st.error(who)

    with tab_register:
        reg_user = st.text_input("Choose a username")
        reg_email = st.text_input("Your email")
        colp1, colp2 = st.columns(2)
        with colp1:
            reg_pass = st.text_input("Choose a password", type="password")
        with colp2:
            reg_pass2 = st.text_input("Confirm password", type="password")

        if st.button("📝 Create account"):
            if reg_pass != reg_pass2:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(reg_user or "", reg_email or "", reg_pass or "")
                if ok:
                    st.success(msg + " Please log in.")
                else:
                    st.error(msg)

    # stop so the generator part doesn't render
    st.stop()

# --------------------------
# Post-login: generator and history
# --------------------------
st.success(f"Logged in as {st.session_state.username} 👋")

# API key: prefer st.secrets, but allow owner fallback in sidebar (won't block login)
api_key = st.secrets.get("gemini_api") if "gemini_api" in st.secrets else None
if not api_key:
    st.sidebar.title("🔑 API Key (owner only)")
    api_key = st.sidebar.text_input("Gemini API Key (optional)", type="password")

model = None
if GEMINI_AVAILABLE and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
    except Exception:
        model = None

# --------------------------
# Generator form
# --------------------------
st.header("🧠 Generate a Lesson Plan")

with st.form("lesson_form"):
    st.subheader("Lesson Details")
    c1, c2 = st.columns(2)
    with c1:
        year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        subject = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
        ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    with c2:
        topic = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
        learning_objective = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")
        lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    sen_notes = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")
    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

# helper generate function that uses model if available
def generate_and_display_plan(prompt: str, title: str="Latest", regen_message: str=""):
    # if model not configured, show instructive message
    if not GEMINI_AVAILABLE:
        st.error("Gemini library not available in this environment. The generator requires the Gemini client.")
        return
    if not model:
        st.error("Gemini API key not configured. Put it in st.secrets['gemini_api'] or the sidebar (owner only).")
        return

    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            # save to history
            st.session_state.lesson_history.append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            # display sections: robust split by section headers
            # make pattern to find headers at line starts (case-insensitive)
            pattern = re.compile(r"(?im)^(" + "|".join(re.escape(h) for h in SECTION_KEYS) + r")\s*:?\s*$")
            parts = re.split(pattern, clean_output)
            # parts: [pre, header1, content1, header2, content2, ...] or no headers
            if len(parts) > 1:
                for i in range(1, len(parts), 2):
                    header = parts[i].strip()
                    body = parts[i+1].strip() if i+1 < len(parts) else ""
                    if body:
                        st.markdown(f"<div class='stCard'><b>{header}</b><br>{body}</div>", unsafe_allow_html=True)
            else:
                # fallback: just show whole plan in a card
                st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)

            # Full text area
            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

            # Prepare downloads
            pdf_buf = create_pdf_wrapped(clean_output)
            docx_buf = create_docx(clean_output)
            txt_b64 = base64.b64encode(clean_output.encode()).decode()

            # Ensure buffer pointers reset before reading
            pdf_buf.seek(0)
            docx_buf.seek(0)

            # Inline buttons (identical style, side-by-side)
            st.markdown(
                f"""
                <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                    <a href="data:text/plain;base64,{txt_b64}" download="lesson_plan.txt">
                        <button>⬇ TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buf.read()).decode()}" download="lesson_plan.pdf">
                        <button>⬇ PDF</button>
                    </a>
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buf.read()).decode()}" download="lesson_plan.docx">
                        <button>⬇ DOCX</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            em = str(e).lower()
            if "quota" in em:
                st.error("⚠️ API quota exceeded for today.")
            elif "api key" in em or "permission" in em:
                st.error("⚠️ Invalid or missing API key.")
            else:
                st.error(f"Error generating lesson plan: {e}")

# Run generation when submitted
if submitted:
    prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}

Format with clear section headings:
- Lesson title
- Learning outcomes
- Starter activity
- Main activity
- Plenary activity
- Resources needed
- Differentiation ideas
- Assessment methods

Use concise bullet points where appropriate.
"""
    st.session_state.last_prompt = prompt
    generate_and_display_plan(prompt, title="Original")

# --------------------------
# Regeneration options (same UI you had)
# --------------------------
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
        ]
    )
    custom_instruction = st.text_input(
        "Or type your own custom instruction (optional)",
        placeholder="e.g. Make it more interactive with outdoor activities"
    )

    if st.button("🔁 Regenerate Lesson Plan"):
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

# --------------------------
# Sidebar: history and logout
# --------------------------
st.sidebar.header("📚 Lesson History")
for i, lesson in enumerate(reversed(st.session_state.lesson_history)):
    key = f"hist_{i}"
    if st.sidebar.button(lesson["title"], key=key):
        st.markdown(f"<div class='stCard'><b>{lesson['title']}</b><br>{lesson['content']}</div>", unsafe_allow_html=True)

if st.sidebar.button("🚪 Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()