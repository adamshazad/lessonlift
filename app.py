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

# --- Demo users and login state ---
if "users" not in st.session_state:
    st.session_state["users"] = {"demo@demo.com": "demo123"}  # demo account
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""
if "lesson_history" not in st.session_state:
    st.session_state["lesson_history"] = []

# --- Login/Register UI ---
st.title("🔑 LessonLift Login")

choice = st.radio("Select an option:", ["Login", "Register"])
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if choice == "Login":
    if st.button("Sign In"):
        if email in st.session_state["users"] and st.session_state["users"][email] == password:
            st.session_state["logged_in"] = True
            st.session_state["current_user"] = email
            st.success(f"Logged in as {email}")
        else:
            st.error("❌ Invalid username or password")

elif choice == "Register":
    if st.button("Create Account"):
        if email in st.session_state["users"]:
            st.error("❌ User already exists")
        else:
            st.session_state["users"][email] = password
            st.success(f"Account created for {email}. You can now log in!")

# --- Only show lesson generator if logged in ---
if st.session_state["logged_in"]:
    st.write(f"Welcome, {st.session_state['current_user']}!")

    # --- Optional: API key for Gemini if needed ---
    api_key = st.text_input("Gemini API Key (optional for demo)", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
    else:
        model = None  # demo mode, no real API calls

    # --- Helper functions ---
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

    # --- Lesson Form ---
    st.subheader("Lesson Details")
    with st.form("lesson_form"):
        lesson_data = {}
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
        # --- Demo generation if no API ---
        if model:
            try:
                response = model.generate_content(prompt)
                output = response.text.strip()
            except Exception:
                output = "Demo lesson plan content. Replace with Gemini API for real data."
        else:
            output = "Demo lesson plan content. Replace with Gemini API for real data."

        clean_output = strip_markdown(output)
        st.session_state["lesson_history"].append({"title": f"Lesson {len(st.session_state['lesson_history'])+1}", "content": clean_output})

        st.text_area("Full Lesson Plan (copyable)", value=clean_output, height=400)
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

    # --- Lesson History Sidebar ---
    st.sidebar.header("📚 Lesson History")
    for i, lesson in enumerate(reversed(st.session_state["lesson_history"])):
        if st.sidebar.button(lesson["title"], key=i):
            st.text_area(f"Lesson History: {lesson['title']}", value=lesson["content"], height=400)

else:
    st.info("Please log in or register to generate lesson plans.")