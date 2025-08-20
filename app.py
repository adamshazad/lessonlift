import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
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

# --- Demo Users ---
USERS = {"demo@demo.com": "demo123"}  # You can add more demo accounts here

# --- Logo ---
def show_logo(path="logo.png", width=200):
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

show_logo()

# --- Login ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("🔑 Sign In (Demo Mode)")
    email = st.text_input("Email", placeholder="demo@demo.com")
    password = st.text_input("Password", type="password", placeholder="demo123")
    if st.button("Sign In"):
        if email in USERS and USERS[email] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = email
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# --- Lesson History ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- Helper Functions ---
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

# --- Demo content generator ---
def generate_demo_plan(prompt):
    # This is a mock lesson plan generator for demo mode
    demo_output = f"""
Lesson title: **{prompt.get('topic','Sample Topic')}**
Learning outcomes: **Understand the basics of {prompt.get('topic','the topic')}**
Starter activity: **Quick discussion questions**
Main activity: **Hands-on practice**
Plenary activity: **Review and reflect**
Resources needed: **Worksheet, pencils, board**
Differentiation ideas: **Provide visual aids for lower ability**
Assessment methods: **Observation and quick quiz**
"""
    return demo_output

def display_plan(plan_text):
    clean_output = strip_markdown(plan_text)
    st.session_state["lesson_history"].append({"title": clean_output.splitlines()[0], "content": clean_output})

    # Display sections
    sections = ["Lesson title","Learning outcomes","Starter activity","Main activity",
                "Plenary activity","Resources needed","Differentiation ideas","Assessment methods"]
    for sec in sections:
        start_idx = clean_output.find(sec)
        if start_idx == -1:
            continue
        end_idx = len(clean_output)
        for next_sec in sections:
            if next_sec == sec:
                continue
            next_idx = clean_output.find(next_sec, start_idx+1)
            if next_idx != -1 and next_idx > start_idx:
                end_idx = min(end_idx, next_idx)
        section_text = clean_output[start_idx:end_idx].strip()
        st.markdown(f"<div class='stCard'>{section_text}</div>", unsafe_allow_html=True)

    # Full lesson plan
    st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)
    pdf_buffer = create_pdf_wrapped(clean_output)

    # Download buttons
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

# --- Lesson Form ---
st.title("📚 LessonLift - AI Lesson Planner (Demo Mode)")

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
    plan_text = generate_demo_plan(lesson_data)
    display_plan(plan_text)

# --- Sidebar history ---
st.sidebar.header("📚 Lesson History")
for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
    if st.sidebar.button(lesson["title"], key=i):
        st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)