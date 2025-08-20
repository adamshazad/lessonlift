import streamlit as st
import google.generativeai as genai
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
</style>
""", unsafe_allow_html=True)

# --- Sidebar: API Key ---
st.sidebar.title("🔑 API Key Setup")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar.")
    st.stop()
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# --- Function to show logo ---
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

# --- Helper to strip Markdown ---
def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)           # Remove headings
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italics
    return text

# --- Initialize session state ---
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- Login page ---
if not st.session_state["logged_in"]:
    show_logo("logo.png", width=200)
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Please log in to access the lesson generator")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Log in"):
        # Replace these with your real credentials
        if username == "teacher" and password == "1234":
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
else:
    # --- Main generator page ---
    show_logo("logo.png", width=200)
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate tailored UK primary school lesson plans in seconds!")

    # --- PDF generation ---
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

    # --- Generate lesson plan ---
    def generate_and_display_plan(prompt, title="Latest"):
        with st.spinner("✨ Creating lesson plan..."):
            try:
                response = model.generate_content(prompt)
                output = response.text.strip()
                clean_output = strip_markdown(output)

                st.session_state["lesson_history"].append({"title": title, "content": clean_output})

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

                # Full text area
                st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)

                # PDF and TXT downloads
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
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Error generating lesson plan: {e}")

    # --- Form ---
    lesson_data = {}
    submitted = False
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

    # --- Lesson history in sidebar ---
    st.sidebar.header("📚 Lesson History")
    for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
        if st.sidebar.button(lesson["title"], key=i):
            st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)