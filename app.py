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
from datetime import datetime

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="LessonLift - AI Lesson Planner", layout="centered")

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
    max-height: 300px;   /* limit height */
    overflow-y: auto;    /* make it scrollable */
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Session defaults
# -------------------------------
if "lesson_history" not in st.session_state:
    st.session_state.lesson_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "lessons_used" not in st.session_state:
    st.session_state.lessons_used = 0
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = datetime.now().date()

# -------------------------------
# Daily limit
# -------------------------------
DAILY_LIMIT = 10
today = datetime.now().date()
if st.session_state.last_reset_date != today:
    st.session_state.lessons_used = 0
    st.session_state.last_reset_date = today

# -------------------------------
# API key setup
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
    st.info(f"📊 Lessons used today: {st.session_state.lessons_used}/{DAILY_LIMIT}")

def strip_markdown(md_text):
    text = re.sub(r'#+\s*', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    return text

# -------------------------------
# Exporters
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    story = []
    for raw in text.splitlines():
        line = raw.rstrip()
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
    for raw in text.splitlines():
        doc.add_paragraph(raw.rstrip())
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# Generator
# -------------------------------
def generate_and_display_plan(prompt, title="Latest", regen_message=""):
    if not model:
        st.error("⚠️ No Gemini API key found. Add it in the sidebar or in st.secrets['gemini_api'].")
        return

    if st.session_state.lessons_used >= DAILY_LIMIT:
        st.error("🚫 You’ve reached your daily lesson limit. Please try again tomorrow.")
        return

    # ✅ increment immediately
    st.session_state.lessons_used += 1

    with st.spinner("✨ Creating lesson plan..."):
        try:
            response = model.generate_content(prompt)
            output = response.text.strip()
            clean_output = strip_markdown(output)

            # Save to history
            st.session_state.lesson_history.append({"title": title, "content": clean_output})

            if regen_message:
                st.info(f"🔄 {regen_message}")

            # Show latest plan
            st.markdown(f"### 📖 {title}")
            st.markdown(f"<div class='stCard'>{clean_output.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

            # Download buttons
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
# Main generator page
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()

    if not api_key:
        st.error("No Gemini API key found. Add it in the sidebar to generate plans.")
        return

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
# Sidebar history
# -------------------------------
def show_lesson_history():
    st.sidebar.title("📜 Lesson History")
    if st.session_state.lesson_history:
        for i, entry in enumerate(reversed(st.session_state.lesson_history), 1):
            with st.sidebar.expander(f"{entry['title']}"):
                st.markdown(f"<div class='stCard'>{entry['content'].replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.write("No lesson history yet.")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    show_lesson_history()
    lesson_generator_page()