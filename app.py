import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
import os

# --- Page config ---
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

# --- Paths ---
USERS_FILE = "users.json"
SESSION_FILE = "session.json"
LOGO_FILE = "logo.png"

# --- Helper functions ---
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# --- Logo display ---
def show_logo(path, width=200):
    if not os.path.exists(path):
        st.warning("Logo file not found.")
        return
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div style="display:flex; justify-content:center; align-items:center; margin-bottom:20px;">
        <div style="box-shadow:0 8px 24px rgba(0,0,0,0.25); border-radius:12px; padding:8px;">
            <img src="data:image/png;base64,{b64}" width="{width}" style="border-radius:12px;">
        </div>
    </div>
    """, unsafe_allow_html=True)

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
</style>
""", unsafe_allow_html=True)

# --- Sidebar API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Authentication ---
users = load_json(USERS_FILE)
session = load_json(SESSION_FILE)
current_user = session.get("user")

if not current_user:
    # Home / Auth page
    show_logo(LOGO_FILE)
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")
    
    auth_mode = st.radio("Choose option:", ["Login", "Sign Up"])
    
    email_or_username = st.text_input("Email or Username")
    password = st.text_input("Password", type="password")
    
    if auth_mode == "Sign Up":
        confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button(auth_mode):
        if auth_mode == "Login":
            found = False
            for u, info in users.items():
                if email_or_username in [u, info.get("email")] and password == info["password"]:
                    current_user = u
                    save_json(SESSION_FILE, {"user": current_user})
                    found = True
                    st.success(f"Welcome back, {current_user}!")
                    st.experimental_rerun()
            if not found:
                st.error("Invalid username/email or password.")
        else:  # Sign Up
            if email_or_username in users:
                st.error("Username already exists.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                users[email_or_username] = {"email": email_or_username, "password": password}
                save_json(USERS_FILE, users)
                current_user = email_or_username
                save_json(SESSION_FILE, {"user": current_user})
                st.success(f"Account created! Welcome, {current_user}.")
                st.experimental_rerun()
else:
    # --- Logout button ---
    if st.sidebar.button("Logout"):
        os.remove(SESSION_FILE)
        st.experimental_rerun()
    
    # --- Lesson Generator Page ---
    show_logo(LOGO_FILE)
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write(f"Logged in as: {current_user}")
    
    # --- Helper to strip Markdown ---
    def strip_markdown(md_text):
        text = re.sub(r'#+\s*', '', md_text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        return text

    if "lesson_history" not in st.session_state:
        st.session_state["lesson_history"] = []

    def create_pdf(text):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        lines = text.splitlines()
        y = height - 50
        for line in lines:
            c.drawString(50, y, line)
            y -= 14
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        buffer.seek(0)
        return buffer

    def generate_and_display_plan(prompt, title="Latest", regen_message=""):
        with st.spinner("✨ Creating lesson plan..."):
            try:
                response = model.generate_content(prompt)
                output = response.text.strip()
                clean_output = strip_markdown(output)
                st.session_state["lesson_history"].append({"title": title, "content": clean_output})
                if regen_message:
                    st.info(f"🔄 {regen_message}")
                sections = ["Lesson title","Learning outcomes","Starter activity","Main activity",
                            "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"]
                for sec in sections:
                    start_idx = clean_output.find(sec)
                    if start_idx == -1: continue
                    end_idx = len(clean_output)
                    for next_sec in sections:
                        if next_sec == sec: continue
                        next_idx = clean_output.find(next_sec, start_idx+1)
                        if next_idx != -1 and next_idx > start_idx:
                            end_idx = min(end_idx, next_idx)
                    section_text = clean_output[start_idx:end_idx].strip()
                    st.markdown(f"<div class='stCard'>{section_text}</div>", unsafe_allow_html=True)
                st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)
                pdf_buffer = create_pdf(clean_output)
                st.markdown(
                    f"""
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <a href="data:text/plain;base64,{base64.b64encode(clean_output.encode()).decode()}" download="lesson_plan.txt">
                            <button style="
                                padding:10px 16px;
                                font-size:14px;
                                border-radius:8px;
                                border:none;
                                background-color:#4CAF50;
                                color:white;
                                cursor:pointer;
                            ">⬇ Download TXT</button>
                        </a>
                        <a href="data:application/pdf;base64,{base64.b64encode(pdf_buffer.read()).decode()}" download="lesson_plan.pdf">
                            <button style="
                                padding:10px 16px;
                                font-size:14px;
                                border-radius:8px;
                                border:none;
                                background-color:#4CAF50;
                                color:white;
                                cursor:pointer;
                            ">⬇ Download PDF</button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Error generating lesson plan: {e}")

    # --- Lesson Form ---
    submitted = False
    lesson_data = {}

    with st.form("lesson_form"):
        st.subheader("Lesson Details")
        lesson_data['year_group'] = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        lesson_data['subject'] = st.text_input("Subject", placeholder="e.g. English, Maths, Science")
        lesson_data['topic'] = st.text_input("Topic", placeholder="e.g. Fractions, The Romans, Plant Growth")
        lesson_data['learning_objective'] = st.text_area("Learning Objective (optional)", placeholder="e.g. To understand fractions")
        lesson_data['ability_level'] = st.selectbox("Ability Level", ["Mixed ability","Lower ability","Higher ability"])
        lesson_data['lesson_duration'] = st.selectbox("Lesson Duration", ["30 min","45 min","60 min"])
        lesson_data['sen_notes'] = st.text_area("SEN/EAL Notes (optional)", placeholder="e.g. Visual aids, sentence starters")
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
        st.session_state["last_prompt"] = prompt
        generate_and_display_plan(prompt, title="Original")