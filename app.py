import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

MAX_LESSONS_PER_DAY = 50

# Demo user accounts (replace with database later)
USERS = {
    "teacher1": "password123",
    "teacher2": "password456",
}

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
}
button {
    cursor:pointer;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Helpers
# -------------------------------
def show_logo(path, width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
            <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
                <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Please upload 'logo.png' in the app folder.")

def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def create_pdf_wrapped(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleN.fontSize = 12
    styleN.leading = 16
    paragraphs = [Paragraph(p.replace('\n', '<br/>'), styleN) for p in text.split('\n\n')]
    story = []
    for p in paragraphs:
        story.append(p)
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# Session state setup
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "daily_count" not in st.session_state:
    st.session_state.daily_count = {}
if "last_date" not in st.session_state:
    st.session_state.last_date = str(datetime.today().date())

# Reset daily counts if new day
today = str(datetime.today().date())
if st.session_state.last_date != today:
    st.session_state.daily_count = {}
    st.session_state.last_date = today

# -------------------------------
# LOGIN PAGE
# -------------------------------
if not st.session_state.logged_in:
    show_logo("logo.png", width=180)
    st.title("🔐 LessonLift Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# -------------------------------
# MAIN APP (after login)
# -------------------------------
show_logo("logo.png", width=200)
st.title("📚 LessonLift - AI Lesson Planner")
st.write(f"Welcome **{st.session_state.username}**! Generate tailored UK primary school lesson plans in seconds.")

# Track usage for this user
user = st.session_state.username
count = st.session_state.daily_count.get(user, 0)

# ✅ Show progress bar + counter
st.progress(min(count / MAX_LESSONS_PER_DAY, 1.0))
st.write(f"**{count}/{MAX_LESSONS_PER_DAY} lesson plans used today**")

if count >= MAX_LESSONS_PER_DAY:
    st.error("🚫 Maximum lesson plans (50) reached for today. Please try again tomorrow.")
    st.stop()

# --- API Key (hidden for now, demo mode) ---
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    st.warning("⚠️ Demo mode active – no API key provided.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

# -------------------------------
# Lesson Form
# -------------------------------
with st.form("lesson_form"):
    st.subheader("Lesson Details")
    
    year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
    subject = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
    topic = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
    learning_objective = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")
    ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
    lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
    sen_notes = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")

    submitted = st.form_submit_button("🚀 Generate Lesson Plan")

if submitted:
    # Count usage
    st.session_state.daily_count[user] = count + 1
    st.success(f"Lesson plan {count+1}/{MAX_LESSONS_PER_DAY} generated successfully! ✅")