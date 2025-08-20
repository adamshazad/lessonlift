import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- CSS ---
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

# --- Demo mode flag ---
DEMO_MODE = True  # Set True for testing without exhausting API quota

# --- Show logo ---
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-bottom:20px;">
            <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Logo file not found. Upload 'logo.png' in the app folder.")

# --- User database (replace with your own DB for production) ---
if "users" not in st.session_state:
    st.session_state["users"] = {}  # {email: {"password":..., "last_reset":..., "count":...}}

# --- Session flags ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# --- Helper functions ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

def create_pdf_wrapped(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)
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

def check_reset_usage(email):
    user = st.session_state["users"][email]
    today = datetime.now().date()
    if "last_reset" not in user or user["last_reset"] < today:
        user["last_reset"] = today
        user["count"] = 0

# --- Display login / register page ---
show_logo()

st.title("📚 LessonLift - AI Lesson Planner")
st.subheader("Teacher Sign-In / Register")

auth_choice = st.radio("Choose:", ["Login", "Register"])

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if auth_choice == "Register":
    if st.button("Create Account"):
        if email in st.session_state["users"]:
            st.error("Email already registered.")
        else:
            st.session_state["users"][email] = {"password": password, "last_reset": datetime.now().date(), "count": 0}
            st.success("Account created! You can now log in.")
elif auth_choice == "Login":
    if st.button("Sign In"):
        if email in st.session_state["users"] and st.session_state["users"][email]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.success(f"Welcome, {email}!")
        else:
            st.error("Invalid email or password.")

# --- Lesson generator ---
if st.session_state["logged_in"]:
    user_email = st.session_state["user_email"]
    check_reset_usage(user_email)
    user_data = st.session_state["users"][user_email]

    st.markdown("---")
    st.subheader("Generate a Lesson Plan")

    if user_data["count"] >= 50 and not DEMO_MODE:
        st.warning("⚠ Maximum lessons reached for today.")
    else:
        # Optional Gemini API key for production
        if not DEMO_MODE:
            api_key = st.text_input("Gemini API Key", type="password")
            if not api_key:
                st.warning("Enter your Gemini API key to generate lessons.")
                st.stop()
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
        else:
            model = None  # Dummy in demo mode

        year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        subject = st.text_input("Subject", placeholder="e.g. English, Maths")
        topic = st.text_input("Topic", placeholder="e.g. Fractions, The Romans")
        learning_objective = st.text_area("Learning Objective", placeholder="Optional")
        ability_level = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_duration = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        sen_notes = st.text_area("SEN/EAL Notes", placeholder="Optional")

        if st.button("🚀 Generate Lesson Plan"):
            user_data["count"] += 1
            prompt = f"""
Create a detailed UK primary school lesson plan:

Year Group: {year_group}
Subject: {subject}
Topic: {topic}
Learning Objective: {learning_objective or 'Not specified'}
Ability Level: {ability_level}
Lesson Duration: {lesson_duration}
SEN/EAL Notes: {sen_notes or 'None'}
"""
            if DEMO_MODE:
                clean_output = f"Demo lesson plan for {subject} ({topic})..."
            else:
                response = model.generate_content(prompt)
                clean_output = strip_markdown(response.text.strip())

            st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=300)
            pdf_buffer = create_pdf_wrapped(clean_output)

            st.markdown(
                f"""
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white;">⬇ Download TXT</button>
                    </a>
                    <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                        <button style="padding:10px 16px; font-size:14px; border-radius:8px; border:none; background-color:#4CAF50; color:white;">⬇ Download PDF</button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )