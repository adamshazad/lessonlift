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
import datetime
from supabase import create_client, Client

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# -------------------------------
# CSS (tweaked scrollable box max-height)
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
    max-height: 70vh;  /* Increased for better scroll */
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
            st.success("✅ Signup successful! Please verify your email and login.")
            st.session_state.authenticated = False
            st.experimental_rerun()  # <--- Fixed double-click
        else:
            st.error("⚠️ Signup failed. " + str(user))
    except Exception as e:
        st.error(f"⚠️ Signup error: {str(e)}")

def login(email, password):
    if not supabase:
        st.error("⚠️ Supabase not configured. Cannot login.")
        return
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if user.user:
            st.session_state.user = user.user
            st.session_state.authenticated = True
            st.success("✅ Logged in successfully!")
            st.experimental_rerun()  # <--- Fixed double-click
        else:
            st.error("⚠️ Login failed. Check credentials.")
    except Exception as e:
        st.error(f"⚠️ Login error: {str(e)}")

# -------------------------------
# Show login/signup page if not authenticated
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
    st.stop()  # Stop execution until authenticated

# -------------------------------
# Session defaults (authenticated users)
# -------------------------------
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "lesson_count" not in st.session_state:
    st.session_state.lesson_count = 0
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.date.today()

# Reset daily count at midnight
today = datetime.date.today()
if st.session_state.last_reset_date != today:
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = today

# -------------------------------
# Gemini API key setup (server-side)
# -------------------------------
api_key = st.secrets.get("gemini_api", None)
model = None
use_dummy_generator = False

if api_key:
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        working_model_found = False
        for m in models:
            if not working_model_found and hasattr(m, 'supported_methods') and "generateContent" in m.supported_methods:
                model = genai.GenerativeModel(m.name)
                working_model_found = True
        if not working_model_found:
            st.warning("⚠️ No models supporting generateContent found for this API key. Using dummy generator instead.")
            use_dummy_generator = True
    except Exception as e:
        st.warning(f"Could not list models: {e}. Using dummy generator instead.")
        use_dummy_generator = True
else:
    st.warning("⚠️ Gemini API key missing from server. Using dummy generator instead.")
    use_dummy_generator = True

# -------------------------------
# Helper functions
# -------------------------------
def clean_markdown(text):
    text = re.sub(r'\|.*\|', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'-{2,}', '', text)
    text = re.sub(r'•', '-', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

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

# -------------------------------
# Exporters
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    story = []
    for line in text.splitlines():
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
    for line in text.splitlines():
        doc.add_paragraph(line.rstrip())
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# Generator (patched for user lesson limit + dummy fallback)
# -------------------------------
# ... rest of your generate_and_display_plan and lesson_generator_page code unchanged ...
# -------------------------------
# Sidebar and run code unchanged ...