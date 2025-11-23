# -------------------------------
# Set up (NO GEMINI ANYWHERE)
# -------------------------------
import os
import streamlit as st
from openai import OpenAI
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import datetime
from supabase import create_client, Client

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# -------------------------------
# CSS (unchanged)
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
    line-height: 1.6em;
    white-space: pre-wrap;
    max-height: 70vh;
    overflow-y: auto;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    display: none !important;
}
[data-testid="stSidebar"] {
    max-width: 250px !important;
    min-width: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Supabase setup
# -------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

if "user" not in st.session_state:
    st.session_state.user = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# -------------------------------
# Login / Signup
# -------------------------------
def signup(email, password):
    if not supabase:
        st.error("⚠️ Supabase not configured. Cannot sign up.")
        return
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        if user.user:
            st.success("✅ Signup successful! Please verify email and login.")
        else:
            st.error("⚠️ Signup failed.")
    except Exception as e:
        st.error(f"⚠️ Signup error: {e}")

def login(email, password):
    if not supabase:
        st.error("⚠️ Supabase not configured. Cannot login.")
        return
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if user.user:
            st.session_state.user = user.user
            st.session_state.authenticated = True
            st.success("✅ Logged in!")
        else:
            st.error("⚠️ Login failed.")
    except Exception as e:
        st.error(f"⚠️ Login error: {e}")

# -------------------------------
# Login Gate
# -------------------------------
if not st.session_state.authenticated:
    st.title("🔐 LessonLift Login / Signup")
    choice = st.radio("Choose action:", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if choice == "Signup":
        if st.button("Sign Up"):
            signup(email, password)
    else:
        if st.button("Login"):
            login(email, password)
    st.stop()

# -------------------------------
# Session Defaults
# -------------------------------
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "lesson_count" not in st.session_state:
    st.session_state.lesson_count = 0
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.date.today()

today = datetime.date.today()
if st.session_state.last_reset_date != today:
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = today

# -------------------------------
# OpenAI Setup (GPT-5.1-mini)
# -------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL_NAME = "gpt-5.1-mini"

# -------------------------------
# Helper Functions
# -------------------------------
def clean_markdown(text: str):
    text = re.sub(r'\|.*\|', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1')
    text = re.sub(r'\*(.*?)\*', r'\1')
    text = re.sub(r'`(.*?)`', r'\1')
    text = re.sub(r'-{2,}', '', text)
    text = re.sub(r'•', '-', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center;">
            <img src="data:image/png;base64,{b64}" width="{width}" />
        </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("Logo file not found.")

def title_and_tagline():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

# -------------------------------
# PDF + DOCX Exporters
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'],
                            fontSize=11, leading=15, spaceAfter=6)
    story = []
    for line in text.splitlines():
        if not line.strip():
            story.append(Spacer(1, 6))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, normal))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# Generator
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error(f"🚫 Daily limit reached.")
        return

    st.session_state.lesson_count += 1

    structured_prompt = f"""
Create a complete UK primary school lesson plan with this exact structure:

1. Lesson Title
2. Subject
3. Year Group
4. Duration
5. Learning Objectives
6. Success Criteria (All/Most/Some)
7. Key Vocabulary
8. Resources & Preparation
9. Starter (timings + instructions)
10. Main Input / Teaching (timings)
11. Main Activity (differentiated)
12. Plenary
13. Optional Homework
14. SEN notes

{prompt}
"""

    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a lesson-plan generator."},
                    {"role": "user", "content": structured_prompt}
                ],
                max_completion_tokens=1500
            )

            output = response.choices[0].message.content
            clean_output = clean_markdown(output)

            st.session_state.lesson_history.append({
                "title": title,
                "content": clean_output
            })

            if regen_message:
                st.info(f"🔄 {regen_message}")

            remaining = daily_limit - st.session_state.lesson_count
            st.info(f"📊 {st.session_state.lesson_count}/{daily_limit} used — {remaining} left")

            st.markdown(f"### 📖 {title}")
            st.markdown(f"<div class='stCard'>{clean_output}</div>", unsafe_allow_html=True)

            # Export buttons
            pdf_buf = create_pdf(clean_output)
            docx_buf = create_docx(clean_output)

            st.markdown(f"""
            <div style="display:flex; gap:10px; margin-top:10px;">
                <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson.txt">
                    <button>⬇ TXT</button>
                </a>

                <a href="data:application/pdf;base64,{base64.b64encode(pdf_buf.read()).decode()}" download="lesson.pdf">
                    <button>⬇ PDF</button>
                </a>

                <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx_buf.read()).decode()}" download="lesson.docx">
                    <button>⬇ DOCX</button>
                </a>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ Lesson plan could not be generated: {e}")

# -------------------------------
# Main Page
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()

    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        lesson_data['subject'] = st.text_input("Subject")
        lesson_data['topic'] = st.text_input("Topic")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)")
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)")
        submitted = st.form_submit_button("🚀 Generate Lesson Plan")

    if submitted:
        prompt = f"""
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

    # Regeneration section
    if st.session_state.last_prompt:
        st.markdown("### 🔄 Not happy with the plan?")
        regen_style = st.selectbox(
            "Regeneration Style:",
            ["♻️ Just regenerate",
             "🎨 More creative & engaging",
             "📋 More structured with timings",
             "🧩 Simplify for lower ability",
             "🚀 Challenge for higher ability"]
        )
        custom_instruction = st.text_input("Custom instruction (optional)")

        if st.button("🔁 Regenerate"):
            extra = ""
            msg = ""

            if not custom_instruction:
                if regen_style == "🎨 More creative & engaging":
                    extra = "Make the activities more creative and interactive."
                    msg = "Added creativity."
                elif regen_style == "📋 More structured with timings":
                    extra = "Add more structure and clear timings."
                    msg = "Added structure."
                elif regen_style == "🧩 Simplify for lower ability":
                    extra = "Simplify language and add scaffolding."
                    msg = "Simplified."
                elif regen_style == "🚀 Challenge for higher ability":
                    extra = "Increase challenge with stretch tasks."
                    msg = "Increased challenge."
            else:
                extra = custom_instruction
                msg = custom_instruction

            new_prompt = st.session_state.last_prompt + "\n\n" + extra
            generate_and_display_plan(new_prompt,
                                      title=f"Regenerated {len(st.session_state.lesson_history)+1}",
                                      regen_message=msg)

# -------------------------------
# Sidebar History
# -------------------------------
def show_lesson_history():
    st.sidebar.title("📜 Lesson History")
    if st.session_state.lesson_history:
        for entry in reversed(st.session_state.lesson_history):
            with st.sidebar.expander(entry["title"]):
                st.markdown(f"<div class='stCard'>{entry['content']}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.write("No lessons yet.")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()
