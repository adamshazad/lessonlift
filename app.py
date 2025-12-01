# -------------------------------
# App.py - LessonLift (Final Formatting Lock)
# -------------------------------

import os
import streamlit as st
import re
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import datetime
import openai

# -------------------------------
# Page Config
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
    line-height: 1.55em;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

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

if st.session_state.last_reset_date != datetime.date.today():
    st.session_state.lesson_count = 0
    st.session_state.last_reset_date = datetime.date.today()

# -------------------------------
# Load API Key
# -------------------------------
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# Permanent Clean Markdown
# -------------------------------
def clean_markdown(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # REMOVE ALL MARKDOWN THAT BREAKS PDF/DOCX
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)  # remove hashtags
    text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)           # remove bold/italics
    text = re.sub(r'•', '-', text)                              # convert dots → dash
    text = re.sub(r'−', '-', text)                              # weird dash → normal
    text = re.sub(r'\n{3,}', '\n\n', text)                       # prevent huge gaps

    # REMOVE ANY STAR BULLETS
    text = re.sub(r'^\s*\*\s*', '- ', text, flags=re.MULTILINE)

    # FORCE TITLE → 1 LINE → DASH BULLETS
    lines = text.split("\n")
    fixed = []
    prev = ""
    for line in lines:
        stripped = line.strip()

        if stripped == "":
            if prev != "":
                fixed.append("")  # keep ONE blank line only
        else:
            fixed.append(line)

        prev = stripped

    return "\n".join(fixed).strip()

# -------------------------------
# Logo
# -------------------------------
def show_logo(path="logo.png", width=200):
    try:
        with open(path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <div style="text-align:center; margin-bottom:16px;">
                <img src="data:image/png;base64,{encoded}" width="{width}" />
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

def title_and_tagline():
    st.title("📚 LessonLift - AI Lesson Planner")
    st.write("Generate high-quality UK primary school lesson plans instantly.")

# -------------------------------
# PDF Export
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('NormalFixed', parent=styles['Normal'], fontSize=11, leading=15)

    story = []
    for line in text.split("\n"):
        if line.strip() == "":
            story.append(Spacer(1, 6))
        else:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, normal))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# DOCX Export
# -------------------------------
def create_docx(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# -------------------------------
# Generate Plan
# -------------------------------
def generate_and_display_plan(prompt, title="Latest"):
    daily_limit = 10
    if st.session_state.lesson_count >= daily_limit:
        st.error("Daily limit reached.")
        return

    st.session_state.lesson_count += 1

    with st.spinner("Generating plan..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            output = clean_markdown(response.choices[0].message.content)

            st.session_state.lesson_history.append({"title": title, "content": output})

            st.markdown(f"### 📖 {title}")
            st.markdown(f"<div class='stCard'>{output}</div>", unsafe_allow_html=True)

            pdf = create_pdf(output)
            docx = create_docx(output)

            st.markdown(
                f"""
                <a href="data:application/pdf;base64,{base64.b64encode(pdf.read()).decode()}" download="lesson_plan.pdf">
                    <button>⬇ PDF</button>
                </a>
                <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{base64.b64encode(docx.read()).decode()}" download="lesson_plan.docx">
                    <button>⬇ DOCX</button>
                </a>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error: {e}")

# -------------------------------
# Main UI
# -------------------------------
def lesson_generator_page():
    show_logo()
    title_and_tagline()

    with st.form("lesson_form"):
        year_group = st.selectbox("Year Group", ["Year 1","Year 2","Year 3","Year 4","Year 5","Year 6"])
        ability = st.selectbox("Ability Level", ["Mixed ability", "Lower ability", "Higher ability"])
        duration = st.selectbox("Duration", ["30 min","45 min","60 min"])
        subject = st.text_input("Subject")
        topic = st.text_input("Topic")
        lo = st.text_area("Learning Objective (optional)")
        sen = st.text_area("SEN/EAL Notes (optional)")
        submitted = st.form_submit_button("Generate")

    if submitted:
        prompt = f"""
Write a **high-detail UK primary school lesson plan**.

FORMAT RULES:
- NO hashtags
- NO bold
- NO stars
- All bullet points MUST use "- "
- No more than ONE blank line at a time
- No borders, no separator lines
- Structure: Title, 1 line space, dash bullets
- Include emojis in section titles
- Keep content very detailed

DETAILS:
Year Group: {year_group}
Ability Level: {ability}
Duration: {duration}
Subject: {subject}
Topic: {topic}
Learning Objective: {lo or 'Not specified'}
SEN/EAL Notes: {sen or 'None'}
"""
        st.session_state.last_prompt = prompt
        generate_and_display_plan(prompt, title="Original Lesson Plan")

# -------------------------------
# Sidebar
# -------------------------------
def show_history():
    st.sidebar.title("📜 Lesson History")
    for entry in reversed(st.session_state.lesson_history):
        with st.sidebar.expander(entry["title"]):
            st.write(entry["content"])

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    show_history()
    lesson_generator_page()
